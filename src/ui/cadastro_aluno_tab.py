from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt
from database.db import inserir_aluno

FAIXAS = ["Branca", "Azul", "Roxa", "Marrom", "Preta"]


class CadastroAlunoTab(QWidget):
    def __init__(self, refresh_callback=None):
        super().__init__()
        self.refresh_callback = refresh_callback
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)

        titulo = QLabel("Cadastro de Aluno")
        titulo.setStyleSheet("font-size:22px;font-weight:600;")
        layout.addWidget(titulo)

        form = QGridLayout()
        form.setSpacing(10)

        self.nome = QLineEdit()
        self.cpf = QLineEdit()
        self.nascimento = QLineEdit()
        self.telefone = QLineEdit()
        self.email = QLineEdit()
        self.endereco = QLineEdit()

        self.faixa = QComboBox()
        self.faixa.addItems(FAIXAS)

        self.graus = QComboBox()
        self.graus.addItems(["0", "1 Grau", "2 Graus", "3 Graus", "4 Graus"])

        campos = [
            ("Nome", self.nome),
            ("CPF", self.cpf),
            ("Nascimento", self.nascimento),
            ("Telefone", self.telefone),
            ("E-mail", self.email),
            ("Endereço", self.endereco),
            ("Faixa", self.faixa),
            ("Graus", self.graus),
        ]

        for i, (label, campo) in enumerate(campos):
            form.addWidget(QLabel(label), i, 0)
            form.addWidget(campo, i, 1)

        layout.addLayout(form)

        btn = QPushButton("Salvar Aluno")
        btn.setFixedHeight(40)
        btn.clicked.connect(self.salvar)
        layout.addSpacing(10)
        layout.addWidget(btn, alignment=Qt.AlignLeft)

    def salvar(self):
        if not self.nome.text().strip():
            QMessageBox.warning(self, "Erro", "Informe o nome.")
            return

        dados = (
            self.nome.text(),
            self.cpf.text(),
            self.nascimento.text(),
            self.telefone.text(),
            self.email.text(),
            self.endereco.text(),
            self.faixa.currentText(),
            self.graus.currentText(),
        )

        inserir_aluno(dados)
        QMessageBox.information(self, "OK", "Aluno cadastrado.")

        for campo in [self.nome, self.cpf, self.nascimento, self.telefone, self.email, self.endereco]:
            campo.clear()

        if self.refresh_callback:
            self.refresh_callback()
