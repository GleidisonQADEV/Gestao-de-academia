"""Importação de alunos em massa a partir de uma planilha do Google Sheets.

A planilha precisa estar compartilhada como "qualquer pessoa com o link pode ver"
(ou publicada na web). O módulo converte a URL para o export em CSV e não requer
credenciais/OAuth do Google.

Cabeçalhos esperados (primeira linha, sem diferenciar maiúsculas/acentos):
    nome, cpf, email, telefone, cep, endereco, data_nascimento,
    faixa, grau, peso, altura, plano

Apenas ``nome`` é obrigatório. CPFs duplicados (já cadastrados) são ignorados.
"""
import csv
import io
import re
import unicodedata
import urllib.request

from database.db import inserir_aluno, get_conn


# Aliases de cabeçalho -> campo interno
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


def importar_alunos_de_url(url: str):
    """Baixa a planilha e cadastra os alunos.

    Retorna um dicionário com o resumo:
        {'importados': int, 'ignorados': int, 'erros': [str, ...], 'total': int}
    """
    csv_url = extrair_csv_url(url)
    conteudo = _baixar_csv(csv_url)

    leitor = csv.reader(io.StringIO(conteudo))
    linhas = list(leitor)
    if not linhas:
        return {"importados": 0, "ignorados": 0, "erros": ["Planilha vazia."], "total": 0}

    # Mapear cabeçalhos -> índice de coluna
    cabecalho = [_normalizar(c) for c in linhas[0]]
    col_idx = {}
    for i, nome_col in enumerate(cabecalho):
        campo = _HEADER_ALIASES.get(nome_col)
        if campo and campo not in col_idx:
            col_idx[campo] = i

    if "nome" not in col_idx:
        return {
            "importados": 0, "ignorados": 0,
            "erros": ["A planilha precisa ter ao menos a coluna 'nome'."],
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
                telefone=_val(linha, "telefone"),
                cep=_val(linha, "cep"),
                endereco=_val(linha, "endereco"),
                data_nasc=_val(linha, "data_nasc"),
                faixa=_val(linha, "faixa") or "Branca",
                grau=_val(linha, "grau") or "0",
                peso=_val(linha, "peso"),
                altura=_val(linha, "altura"),
                plano=_val(linha, "plano") or None,
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
