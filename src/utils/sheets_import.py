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



def extrair_csv_url(url: str) -> str:
    """Converte uma URL do Google Sheets no link de export CSV.

    Aceita URLs de edição normais e também links já em formato de export.
    """
    url = (url or "").strip()
    if not url:
        raise ValueError("URL vazia.")

    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    if not match:
        # Talvez já seja um link CSV direto.
        if "format=csv" in url or url.lower().endswith(".csv"):
            return url
        raise ValueError("URL do Google Sheets inválida.")

    sheet_id = match.group(1)
    gid_match = re.search(r"[#&?]gid=(\d+)", url)
    gid = gid_match.group(1) if gid_match else "0"
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


def _baixar_csv(csv_url: str) -> str:
    req = urllib.request.Request(csv_url, headers={"User-Agent": "LegacyBJJ-import"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8-sig")


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

    ``plano_padrao`` é usado quando a planilha não tem coluna de plano.
    Retorna um dicionário com o resumo:
        {'importados': int, 'ignorados': int, 'erros': [str, ...], 'total': int}
    """
    csv_url = extrair_csv_url(url)
    conteudo = _baixar_csv(csv_url)

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

        nome = _val(linha, "nome")
        if not nome:
            ignorados += 1
            continue

        cpf = re.sub(r"\D", "", _val(linha, "cpf"))
        if cpf and _cpf_ja_existe(cpf):
            ignorados += 1
            continue

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
