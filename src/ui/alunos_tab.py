from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox
)
from database.db import listar_alunos, inativar_aluno, excluir_aluno


class AlunosTab(QWidget):
    def __init__(self):
        super().__init__()
        self.build_ui()
        self.load()

    def build_ui(self):
        layout = QVBoxLayout(self)

        titulo = QLabel("Alunos")
        titulo.setStyleSheet("font-size:20px;font-weight:600;")
        layout.addWidget(titulo)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(
            ["ID", "Nome", "Faixa", "Graus", "Telefone", "Status"]
        )
        layout.addWidget(self.tabela)

        btns = QHBoxLayout()

        self.btn_toggle = QPushButton("Ativar / Inativar")
        self.btn_del = QPushButton("Excluir")

        self.btn_toggle.clicked.connect(self.toggle_status)
        self.btn_del.clicked.connect(self.delete)

        btns.addWidget(self.btn_toggle)
        btns.addWidget(self.btn_del)
        layout.addLayout(btns)

    def load(self):
        dados = listar_alunos()
        self.tabela.setRowCount(len(dados))

        for i, row in enumerate(dados):
            for j, val in enumerate(row):
                if j == 5:
                    val = "Ativo" if val == 1 else "Inativo"
                self.tabela.setItem(i, j, QTableWidgetItem(str(val)))

    def get_selected_id(self):
        row = self.tabela.currentRow()
        if row < 0:
            return None, None
        aluno_id = int(self.tabela.item(row, 0).text())
        status = self.tabela.item(row, 5).text()
        return aluno_id, status

    def toggle_status(self):
        aluno_id, status = self.get_selected_id()
        if not aluno_id:
            return

        novo = 0 if status == "Ativo" else 1
        inativar_aluno(aluno_id, novo)
        self.load()

    def delete(self):
        aluno_id, _ = self.get_selected_id()
        if not aluno_id:
            return

        if QMessageBox.question(self, "Confirmar", "Excluir aluno?") == QMessageBox.Yes:
            excluir_aluno(aluno_id)
            self.load()
