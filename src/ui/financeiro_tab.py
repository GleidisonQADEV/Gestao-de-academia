from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem

from database.db import listar_mensalidades


class FinanceiroTab(QWidget):
    def __init__(self):
        super().__init__()
        self.build_ui()
        self.load()

    def build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Financeiro")
        title.setStyleSheet("font-size:20px;font-weight:bold;")
        layout.addWidget(title)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(
            ["ID", "Aluno", "Valor", "Data pagamento"]
        )

        layout.addWidget(self.tabela)

    def load(self):
        dados = listar_mensalidades()
        self.tabela.setRowCount(len(dados))

        for i, row in enumerate(dados):
            for j, val in enumerate(row):
                self.tabela.setItem(i, j, QTableWidgetItem(str(val)))

        self.tabela.resizeColumnsToContents()
