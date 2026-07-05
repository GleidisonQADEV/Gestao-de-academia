"""Importação de alunos em massa a partir de uma planilha do Google Sheets.

A planilha precisa estar compartilhada como "qualquer pessoa com o link pode ver"
(ou publicada na web). O módulo converte a URL para o export em CSV e não requer
credenciais/OAuth do Google.

Reconhece tanto cabeçalhos simples (nome, cpf, telefone, ...) quanto os gerados
por Google Forms de matrícula (ex.: "Nome completo", "Telefone (WhatsApp)",
"Endereço completo", "Graus", "Data de nascimento"). Também normaliza faixa,
grau, telefone e data (DD/MM/AAAA -> AAAA-MM-DD).

Apenas o nome é obrigatório. CPFs duplicados (já cadastrados) são ignorados.
"""
import csv
import io
import re
import unicodedata
import urllib.request

from database.db import inserir_aluno, get_conn


# Aliases exatos de cabeçalho (normalizado) -> campo interno
_HEADER_ALIASES = {
    "nome": "nome",
    "cpf": "cpf",
    "email": "email",
    "e-mail": "email",
    "telefone": "telefone",
    "celular": "telefone",
    "cep": "cep",
    "endereco": "endereco",
    "endereço": "endereco",
    "data_nascimento": "data_nasc",
    "datanascimento": "data_nasc",
    "data de nascimento": "data_nasc",
    "nascimento": "data_nasc",
    "faixa": "faixa",
    "grau": "grau",
    "peso": "peso",
    "altura": "altura",
    "plano": "plano",
}


def _normalizar(texto: str) -> str:
    """Remove acentos e coloca em minúsculas para casar cabeçalhos."""
    if texto is None:
        return ""
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.strip().lower()


def _campo_do_cabecalho(norm: str):
    """Descobre o campo interno de um cabeçalho (alias exato ou por palavra-chave)."""
    if norm in _HEADER_ALIASES:
        return _HEADER_ALIASES[norm]
    # Correspondência flexível para planilhas de formulário de matrícula.
    if norm.startswith("nome"):            # "nome completo" (mas não "digite seu nome...")
        return "nome"
    if "emergencia" in norm:               # antes de telefone (contém "telefone")
        return "contato_emergencia"
    if "whatsapp" in norm or "telefone" in norm or "celular" in norm:
        return "telefone"
    if "mail" in norm:
        return "email"
    if norm.startswith("endereco"):        # "endereço completo"
        return "endereco"
    if "nascimento" in norm:
        return "data_nasc"
    if norm.startswith("faixa"):           # "faixa" (não "quanto tempo de faixa?")
        return "faixa"
    if norm.startswith("grau"):            # "graus"
        return "grau"
    if norm == "cpf":
        return "cpf"
    if norm.startswith("cep"):
        return "cep"
    if norm.startswith("peso"):
        return "peso"
    if norm.startswith("altura"):
        return "altura"
    if norm.startswith("plano"):
        return "plano"
    # Campos extras da ficha de matrícula
    if "sanguineo" in norm:
        return "tipo_sanguineo"
    if "alergia" in norm:
        return "alergias"
    if "especifique" in norm:
        return "condicoes_esp"
    if "condicoes" in norm or "condicao" in norm:
        return "condicoes_medicas"
    if "tempo" in norm:
        return "tempo_faixa"
    return None


# Normalização de valores -------------------------------------------------

_FAIXAS_VALIDAS = {
    "branca": "Branca", "azul": "Azul", "roxa": "Roxa",
    "marrom": "Marrom", "marron": "Marrom", "preta": "Preta",
    "cinza": "Cinza", "amarela": "Amarela", "laranja": "Laranja", "verde": "Verde",
}


def _norm_faixa(valor: str) -> str:
    v = (valor or "").strip().lower()
    if not v or v in {"0", "?", "-", "n/a", "na"}:
        return "Branca"
    return _FAIXAS_VALIDAS.get(v, valor.strip().title())


_GRAUS = {
    "0": "Sem grau", "sem grau": "Sem grau", "": "Sem grau",
    "1": "1 Grau", "2": "2 Graus", "3": "3 Graus", "4": "4 Graus",
}


def _norm_grau(valor: str) -> str:
    v = (valor or "").strip().lower()
    return _GRAUS.get(v, valor.strip() or "Sem grau")


def _limpar_telefone(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


def _conv_data(valor: str) -> str:
    """Converte DD/MM/AAAA para AAAA-MM-DD; mantém se já estiver em ISO."""
    v = (valor or "").strip()
    if not v:
        return ""
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", v)
    if m:
        d, mth, y = m.groups()
        return f"{y}-{int(mth):02d}-{int(d):02d}"
    return v


# Conectores que ficam em minúsculas no meio do nome
_NOME_MINUSCULAS = {"de", "da", "do", "das", "dos", "e", "di", "du", "del", "la"}


def _norm_nome(valor: str) -> str:
    """Padroniza o nome: espaços colapsados e capitalização (Title Case pt-BR)."""
    v = " ".join((valor or "").split())
    if not v:
        return v
    palavras = v.lower().split(" ")
    out = []
    for i, p in enumerate(palavras):
        if i > 0 and p in _NOME_MINUSCULAS:
            out.append(p)
        else:
            out.append(p[:1].upper() + p[1:] if p else p)
    return " ".join(out)


# Plano padrão aplicado na importação quando a planilha não traz plano.
PLANO_PADRAO = "Adulto - R$180"




def _ids_da_url(url: str):
    """Extrai (sheet_id, gid) de uma URL do Google Sheets."""
    url = (url or "").strip()
    m = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    if not m:
        return None, None
    sid = m.group(1)
    g = re.search(r"[#&?]gid=(\d+)", url)
    return sid, (g.group(1) if g else "0")


def extrair_csv_url(url: str) -> str:
    """Converte uma URL do Google Sheets no link de export CSV.

    Aceita URLs de edição normais e também links já em formato de export.
    """
    url = (url or "").strip()
    if not url:
        raise ValueError("URL vazia.")

    sid, gid = _ids_da_url(url)
    if not sid:
        # Talvez já seja um link CSV direto.
        if "format=csv" in url or url.lower().endswith(".csv"):
            return url
        raise ValueError("URL do Google Sheets inválida.")

    return f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"


def _urls_csv_candidatas(url: str):
    """Lista de URLs de CSV a tentar (export e, como fallback, gviz)."""
    sid, gid = _ids_da_url(url)
    if not sid:
        return [extrair_csv_url(url)]
    return [
        f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}",
        f"https://docs.google.com/spreadsheets/d/{sid}/gviz/tq?tqx=out:csv&gid={gid}",
    ]


def _baixar_csv(csv_url: str) -> str:
    import urllib.error

    # User-Agent de navegador evita respostas 400 do Google para clientes "estranhos".
    ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/120.0 Safari/537.36 LegacyBJJ-import")
    req = urllib.request.Request(csv_url, headers={"User-Agent": ua})

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            conteudo = resp.read().decode("utf-8-sig")
    except urllib.error.HTTPError as e:
        if e.code in (400, 401, 403):
            raise ValueError(
                "Não foi possível acessar a planilha. Verifique se ela está "
                "compartilhada como 'Qualquer pessoa com o link' (Leitor) e se o "
                "link está correto."
            )
        if e.code == 404:
            raise ValueError("Planilha não encontrada. Confira o link.")
        raise ValueError(f"Erro ao baixar a planilha (HTTP {e.code}).")
    except urllib.error.URLError as e:
        raise ValueError(f"Sem conexão para baixar a planilha: {e.reason}")

    # Se veio HTML (página de login), a planilha não está pública.
    inicio = conteudo.lstrip()[:200].lower()
    if inicio.startswith("<!doctype html") or "<html" in inicio:
        raise ValueError(
            "A planilha não está pública. Compartilhe como "
            "'Qualquer pessoa com o link' (Leitor) e tente novamente."
        )
    return conteudo


def _baixar_csv_robusto(url_original: str) -> str:
    """Tenta baixar o CSV pelas URLs candidatas; retorna o primeiro conteúdo válido."""
    ultimo_erro = None
    for u in _urls_csv_candidatas(url_original):
        try:
            return _baixar_csv(u)
        except ValueError as e:
            ultimo_erro = e
    raise ultimo_erro or ValueError("Não foi possível baixar a planilha.")



def _cpf_ja_existe(cpf: str) -> bool:
    if not cpf:
        return False
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM alunos WHERE cpf = ?", (cpf,))
    existe = cur.fetchone() is not None
    conn.close()
    return existe


def importar_alunos_de_url(url: str, plano_padrao: str = None):
    """Baixa a planilha e cadastra os alunos.

    ``plano_padrao`` é usado quando a planilha não tem coluna de plano
    (padrão: ``Adulto - R$180``).
    Retorna um dicionário com o resumo:
        {'importados': int, 'ignorados': int, 'erros': [str, ...], 'total': int}
    """
    if not plano_padrao:
        plano_padrao = PLANO_PADRAO
    conteudo = _baixar_csv_robusto(url)

    leitor = csv.reader(io.StringIO(conteudo))
    linhas = list(leitor)
    if not linhas:
        return {"importados": 0, "ignorados": 0, "erros": ["Planilha vazia."], "total": 0}

    # Mapear cabeçalhos -> índice de coluna (primeira ocorrência vence)
    cabecalho = [_normalizar(c) for c in linhas[0]]
    col_idx = {}
    for i, nome_col in enumerate(cabecalho):
        campo = _campo_do_cabecalho(nome_col)
        if campo and campo not in col_idx:
            col_idx[campo] = i

    if "nome" not in col_idx:
        return {
            "importados": 0, "ignorados": 0,
            "erros": ["A planilha precisa ter ao menos uma coluna de nome."],
            "total": max(len(linhas) - 1, 0),
        }

    def _val(linha, campo):
        idx = col_idx.get(campo)
        if idx is None or idx >= len(linha):
            return ""
        return (linha[idx] or "").strip()

    importados = 0
    ignorados = 0
    erros = []
    dados = linhas[1:]

    for num, linha in enumerate(dados, start=2):
        if not any((c or "").strip() for c in linha):
            continue  # linha em branco

        nome = _norm_nome(_val(linha, "nome"))
        if not nome:
            ignorados += 1
            continue

        cpf = re.sub(r"\D", "", _val(linha, "cpf"))
        if cpf and _cpf_ja_existe(cpf):
            ignorados += 1
            continue

        # Combina condição médica + especificação
        cond = _val(linha, "condicoes_medicas")
        cond_esp = _val(linha, "condicoes_esp")
        if cond and cond_esp:
            condicoes = f"{cond} — {cond_esp}"
        else:
            condicoes = cond or cond_esp

        try:
            inserir_aluno(
                nome=nome,
                cpf=cpf or None,
                email=_val(linha, "email") or None,
                telefone=_limpar_telefone(_val(linha, "telefone")),
                cep=_val(linha, "cep"),
                endereco=_val(linha, "endereco"),
                data_nasc=_conv_data(_val(linha, "data_nasc")),
                faixa=_norm_faixa(_val(linha, "faixa")),
                grau=_norm_grau(_val(linha, "grau")),
                peso=_val(linha, "peso"),
                altura=_val(linha, "altura"),
                plano=_val(linha, "plano") or plano_padrao,
                foto_path=None,
                certificado_path=None,
                biometria_data=None,
                tipo_sanguineo=_val(linha, "tipo_sanguineo") or None,
                contato_emergencia=_val(linha, "contato_emergencia") or None,
                alergias=_val(linha, "alergias") or None,
                condicoes_medicas=condicoes or None,
                tempo_faixa=_val(linha, "tempo_faixa") or None,
            )
            importados += 1
        except Exception as e:  # noqa: BLE001 - reportamos qualquer falha por linha
            erros.append(f"Linha {num} ({nome}): {e}")

    return {
        "importados": importados,
        "ignorados": ignorados,
        "erros": erros,
        "total": importados + ignorados + len(erros),
    }


# ============================ IMPORTAÇÃO DE KIDS ============================

def _campo_do_cabecalho_kid(norm: str):
    """Mapeia cabeçalhos da planilha de matrícula de menores.

    Diferencia colunas do aluno das do responsável (ambas têm 'nome'/'cpf').
    """
    # Colunas do responsável primeiro (contêm nome/cpf/telefone/e-mail)
    if "responsavel" in norm:
        if "cpf" in norm:
            return "resp_cpf"
        if "nome" in norm:
            return "resp_nome"
        if "telefone" in norm or "whatsapp" in norm:
            return "telefone"
        if "mail" in norm:
            return "email"
        return None
    # Colunas do aluno (menor)
    if norm.startswith("nome"):            # "nome completo do aluno"
        return "nome"
    if "cpf" in norm:                      # "cpf do aluno"
        return "cpf"
    if "nascimento" in norm:
        return "data_nasc"
    if norm.startswith("faixa"):
        return "faixa"
    if norm.startswith("endereco"):
        return "endereco"
    if norm.startswith("grau"):
        return "grau"
    if "tempo" in norm:
        return "tempo_faixa"
    return None


# Faixas kids -> formato do app (Branca, Cinza c/b, Amarela, Verde c/p, ...)
_BASES_FAIXA = {
    "branca": "Branca", "cinza": "Cinza", "amarela": "Amarela",
    "laranja": "Laranja", "verde": "Verde",
    "azul": "Azul", "roxa": "Roxa", "marrom": "Marrom",
    "marron": "Marrom", "preta": "Preta",
}


def _norm_faixa_kid(valor: str) -> str:
    v = (valor or "").strip().lower()
    if not v or v in {"0", "?", "-", "n/a", "na"}:
        return "Branca"
    base = None
    for k, b in _BASES_FAIXA.items():
        if k in v:
            base = b
            break
    if not base:
        return valor.strip().title()
    if base in ("Branca", "Azul", "Roxa", "Marrom", "Preta"):
        return base
    # Faixas kids têm variantes com ponta branca (c/b) e com ponta preta (c/p)
    if "branc" in v:
        return f"{base} c/b"
    if "ponta" in v or "pret" in v:
        return f"{base} c/p"
    return base


def _buscar_adulto_por_cpf(cpf: str):
    """Retorna (id, nome) do aluno adulto ativo com esse CPF, ou None."""
    if not cpf:
        return None
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, nome FROM alunos WHERE cpf = ? AND ativo = 1", (cpf,))
    row = cur.fetchone()
    conn.close()
    return row


def _cpf_kid_ja_existe(cpf: str) -> bool:
    if not cpf:
        return False
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM kids WHERE cpf = ?", (cpf,))
        existe = cur.fetchone() is not None
    except Exception:
        existe = False
    conn.close()
    return existe


def importar_kids_de_url(url: str, plano_padrao: str = "Kids (5-13) - R$150"):
    """Importa a planilha de menores e vincula ao responsável quando ele é aluno.

    Se o CPF do responsável corresponder a um aluno adulto cadastrado, usa o
    nome oficial do responsável e conta como 'vinculado'.

    Retorna: {'importados', 'vinculados', 'ignorados', 'erros', 'total'}.
    """
    from database.kids_db import inserir_kid

    conteudo = _baixar_csv_robusto(url)
    leitor = csv.reader(io.StringIO(conteudo))
    linhas = list(leitor)
    if not linhas:
        return {"importados": 0, "vinculados": 0, "ignorados": 0, "erros": ["Planilha vazia."], "total": 0}

    cabecalho = [_normalizar(c) for c in linhas[0]]
    col_idx = {}
    for i, nome_col in enumerate(cabecalho):
        campo = _campo_do_cabecalho_kid(nome_col)
        if campo and campo not in col_idx:
            col_idx[campo] = i

    if "nome" not in col_idx:
        return {
            "importados": 0, "vinculados": 0, "ignorados": 0,
            "erros": ["A planilha precisa ter a coluna de nome do aluno."],
            "total": max(len(linhas) - 1, 0),
        }

    def _val(linha, campo):
        idx = col_idx.get(campo)
        if idx is None or idx >= len(linha):
            return ""
        return (linha[idx] or "").strip()

    importados = vinculados = ignorados = 0
    erros = []

    for num, linha in enumerate(linhas[1:], start=2):
        if not any((c or "").strip() for c in linha):
            continue

        nome = _norm_nome(_val(linha, "nome"))
        if not nome:
            ignorados += 1
            continue

        cpf_kid = re.sub(r"\D", "", _val(linha, "cpf"))
        if cpf_kid and _cpf_kid_ja_existe(cpf_kid):
            ignorados += 1
            continue

        resp_cpf = re.sub(r"\D", "", _val(linha, "resp_cpf"))
        resp_nome = _norm_nome(_val(linha, "resp_nome"))

        # Vinculação: se o responsável é um aluno adulto cadastrado
        adulto = _buscar_adulto_por_cpf(resp_cpf)
        if adulto:
            resp_nome = adulto[1]  # nome oficial do responsável cadastrado
            vinculados += 1

        try:
            inserir_kid(
                nome, cpf_kid or None, resp_nome or "", resp_cpf or "",
                _val(linha, "email") or None,
                _limpar_telefone(_val(linha, "telefone")),
                _val(linha, "cep"),
                _val(linha, "endereco"),
                _conv_data(_val(linha, "data_nasc")),
                _norm_faixa_kid(_val(linha, "faixa")),
                _norm_grau(_val(linha, "grau")),
                "", "",
                plano_padrao,
                None, None,
            )
            importados += 1
        except Exception as e:  # noqa: BLE001
            erros.append(f"Linha {num} ({nome}): {e}")

    return {
        "importados": importados,
        "vinculados": vinculados,
        "ignorados": ignorados,
        "erros": erros,
        "total": importados + ignorados + len(erros),
    }

