from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from database.db import get_conn


def gerar_relatorio_mes(ano, mes, caminho):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT a.nome, m.data_vencimento, m.valor, m.status
        FROM mensalidades m
        JOIN alunos a ON a.id = m.aluno_id
        WHERE strftime('%Y', m.data_vencimento)=?
        AND strftime('%m', m.data_vencimento)=?
        ORDER BY a.nome
    """, (str(ano), f"{mes:02d}"))

    dados = cur.fetchall()
    conn.close()

    doc = SimpleDocTemplate(caminho, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"Relatório {mes}/{ano}", styles['Title']))
    story.append(Spacer(1, 10))

    tabela = [["Aluno", "Vencimento", "Valor", "Status"]]
    for d in dados:
        tabela.append([d[0], d[1], f"R$ {d[2]:.2f}", d[3]])

    story.append(Table(tabela))
    doc.build(story)
