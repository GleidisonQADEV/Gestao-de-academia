"""Helper de exportação de relatórios em PDF a partir das telas."""
from datetime import date

from PySide6.QtWidgets import QFileDialog

from .app_dialog import show_info, show_error


_NOMES = {
    "financeiro": "relatorio_financeiro.pdf",
    "alunos": "lista_alunos.pdf",
    "frequencia": "relatorio_frequencia.pdf",
    "ficha": "ficha_aluno.pdf",
}


def exportar_pdf_dialog(parent, tipo, aluno_id=None):
    """Abre o diálogo de salvar, gera o PDF do tipo indicado e dá feedback.

    tipos: 'financeiro', 'alunos', 'frequencia', 'ficha' (requer aluno_id).
    """
    caminho, _ = QFileDialog.getSaveFileName(
        parent, "Salvar PDF", _NOMES.get(tipo, "relatorio.pdf"), "PDF (*.pdf)"
    )
    if not caminho:
        return
    if not caminho.lower().endswith(".pdf"):
        caminho += ".pdf"

    try:
        from utils import pdf_report
        hoje = date.today()
        if tipo == "financeiro":
            pdf_report.gerar_relatorio_financeiro(hoje.year, hoje.month, caminho)
        elif tipo == "alunos":
            pdf_report.gerar_lista_alunos(caminho)
        elif tipo == "frequencia":
            pdf_report.gerar_relatorio_frequencia(caminho)
        elif tipo == "ficha":
            pdf_report.gerar_ficha_aluno(aluno_id, caminho)
        else:
            return
    except Exception as e:  # noqa: BLE001
        show_error(parent, "Erro ao gerar PDF", str(e))
        return

    show_info(parent, "PDF gerado", f"Arquivo salvo em:\n{caminho}")
