"""Geração de relatórios em PDF (financeiro, lista de alunos, frequência e ficha).

Usa reportlab. As funções retornam o caminho do arquivo gerado.
"""
from datetime import date

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm

from database.db import get_conn, obter_percentual_presenca, AULAS_POR_MES


_MESES = [
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def _estilos():
    return getSampleStyleSheet()


def _cabecalho(story, styles, titulo, subtitulo=None):
    story.append(Paragraph("Centro de Treinamento Legacy BJJ", styles["Title"]))
    story.append(Paragraph(titulo, styles["Heading2"]))
    if subtitulo:
        story.append(Paragraph(subtitulo, styles["Normal"]))
    story.append(Paragraph(
        f"Gerado em {date.today().strftime('%d/%m/%Y')}", styles["Normal"]
    ))
    story.append(Spacer(1, 12))


def _estilo_tabela():
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#cc1e1e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f4f4")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])


# ------------------------------------------------------------------ FINANCEIRO

def gerar_relatorio_financeiro(ano, mes, caminho):
    """Relatório de mensalidades do mês."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.nome, m.data_vencimento, m.valor, m.status, m.data_pagamento
        FROM mensalidades m
        JOIN alunos a ON a.id = m.aluno_id
        WHERE strftime('%Y', m.data_vencimento)=?
          AND strftime('%m', m.data_vencimento)=?
        ORDER BY a.nome
    """, (str(ano), f"{mes:02d}"))
    dados = cur.fetchall()
    conn.close()

    doc = SimpleDocTemplate(caminho, pagesize=A4)
    styles = _estilos()
    story = []
    _cabecalho(story, styles, "Relatório Financeiro", f"{_MESES[mes]} / {ano}")

    total = sum(d[2] or 0 for d in dados)
    pago = sum((d[2] or 0) for d in dados if (d[3] or "").upper() == "PAGO")

    tabela = [["Aluno", "Vencimento", "Valor", "Status", "Pagamento"]]
    for d in dados:
        tabela.append([
            d[0], str(d[1]), f"R$ {d[2]:.2f}", d[3] or "-", str(d[4]) if d[4] else "-",
        ])
    if len(tabela) == 1:
        tabela.append(["Nenhuma mensalidade no período", "", "", "", ""])

    t = Table(tabela, colWidths=[6 * cm, 3 * cm, 2.5 * cm, 2.5 * cm, 3 * cm])
    t.setStyle(_estilo_tabela())
    story.append(t)
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Total previsto:</b> R$ {total:.2f}", styles["Normal"]))
    story.append(Paragraph(f"<b>Total recebido:</b> R$ {pago:.2f}", styles["Normal"]))
    story.append(Paragraph(f"<b>Em aberto:</b> R$ {total - pago:.2f}", styles["Normal"]))

    doc.build(story)
    return caminho


# Compatibilidade com o nome antigo
def gerar_relatorio_mes(ano, mes, caminho):
    return gerar_relatorio_financeiro(ano, mes, caminho)


# ------------------------------------------------------------------ LISTA ALUNOS

def gerar_lista_alunos(caminho):
    """Lista de todos os alunos ativos."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT nome, cpf, telefone, faixa, grau, plano
        FROM alunos WHERE ativo = 1 ORDER BY nome
    """)
    dados = cur.fetchall()
    conn.close()

    doc = SimpleDocTemplate(caminho, pagesize=A4)
    styles = _estilos()
    story = []
    _cabecalho(story, styles, "Lista de Alunos", f"Total: {len(dados)} aluno(s) ativo(s)")

    tabela = [["Nome", "CPF", "Telefone", "Faixa", "Grau", "Plano"]]
    for d in dados:
        tabela.append([d[0], d[1] or "-", d[2] or "-", d[3] or "-", d[4] or "-", d[5] or "-"])
    if len(tabela) == 1:
        tabela.append(["Nenhum aluno cadastrado", "", "", "", "", ""])

    t = Table(tabela, colWidths=[4.5 * cm, 3 * cm, 3 * cm, 2.5 * cm, 1.5 * cm, 3 * cm])
    t.setStyle(_estilo_tabela())
    story.append(t)

    doc.build(story)
    return caminho


# ------------------------------------------------------------------ FREQUÊNCIA

def gerar_relatorio_frequencia(caminho, ano=None, mes=None):
    """Relatório de percentual de presença por aluno no mês."""
    hoje = date.today()
    ano = ano or hoje.year
    mes = mes or hoje.month

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, faixa FROM alunos WHERE ativo = 1 ORDER BY nome")
    alunos = cur.fetchall()
    conn.close()

    doc = SimpleDocTemplate(caminho, pagesize=A4)
    styles = _estilos()
    story = []
    _cabecalho(
        story, styles, "Relatório de Frequência",
        f"{_MESES[mes]} / {ano} — base de {AULAS_POR_MES} aulas/mês",
    )

    tabela = [["Aluno", "Faixa", "Presenças", "% Presença"]]
    for aluno_id, nome, faixa in alunos:
        pct, presencas = obter_percentual_presenca(aluno_id, "adulto", ano, mes)
        tabela.append([nome, faixa or "-", str(presencas), f"{pct:.1f}%"])
    if len(tabela) == 1:
        tabela.append(["Nenhum aluno cadastrado", "", "", ""])

    t = Table(tabela, colWidths=[7 * cm, 3 * cm, 3 * cm, 3 * cm])
    t.setStyle(_estilo_tabela())
    story.append(t)

    doc.build(story)
    return caminho


# ------------------------------------------------------------------ FICHA ALUNO

def gerar_ficha_aluno(aluno_id, caminho):
    """Ficha individual de um aluno."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT nome, cpf, email, telefone, cep, endereco, data_nascimento,
               faixa, grau, peso, altura, plano
        FROM alunos WHERE id = ?
    """, (aluno_id,))
    a = cur.fetchone()
    conn.close()

    if not a:
        raise ValueError("Aluno não encontrado.")

    pct, presencas = obter_percentual_presenca(aluno_id, "adulto")

    doc = SimpleDocTemplate(caminho, pagesize=A4)
    styles = _estilos()
    story = []
    _cabecalho(story, styles, "Ficha do Aluno", a[0])

    campos = [
        ("Nome", a[0]), ("CPF", a[1]), ("E-mail", a[2]), ("Telefone", a[3]),
        ("CEP", a[4]), ("Endereço", a[5]), ("Nascimento", a[6]),
        ("Faixa", a[7]), ("Grau", a[8]), ("Peso", a[9]), ("Altura", a[10]),
        ("Plano", a[11]), ("Presenças no mês", str(presencas)),
        ("% de presença", f"{pct:.1f}%"),
    ]
    tabela = [[c, (v if v not in (None, "") else "-")] for c, v in campos]
    t = Table(tabela, colWidths=[5 * cm, 11 * cm])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f4f4f4")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)

    doc.build(story)
    return caminho
