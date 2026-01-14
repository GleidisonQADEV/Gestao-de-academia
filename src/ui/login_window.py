from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit,
    QPushButton, QLabel, QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from database.db import connect


class LoginWindow(QWidget):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success

        self.setWindowTitle("Centro de Treinamento Legacy BJJ")
        self.resize(400, 460)

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignCenter)
        root.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedWidth(340)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)
        card_layout.setContentsMargins(32, 32, 32, 32)

        titulo = QLabel("Centro de Treinamento")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size:16px;font-weight:600;")

        subtitulo = QLabel("Legacy BJJ")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("font-size:22px;font-weight:800;")

        acesso = QLabel("Acesso ao Sistema")
        acesso.setAlignment(Qt.AlignCenter)
        acesso.setStyleSheet("color:#6b7280;")

        self.user = QLineEdit()
        self.user.setPlaceholderText("Usuário")

        self.pwd = QLineEdit()
        self.pwd.setPlaceholderText("Senha")
        self.pwd.setEchoMode(QLineEdit.Password)

        btn = QPushButton("Entrar")
        btn.clicked.connect(self.login)

        card_layout.addWidget(titulo)
        card_layout.addWidget(subtitulo)
        card_layout.addWidget(acesso)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.user)
        card_layout.addWidget(self.pwd)
        card_layout.addSpacing(10)
        card_layout.addWidget(btn)

        root.addWidget(card)

    def login(self):
        conn = connect()
        cur = conn.cursor()

        cur.execute(
            "SELECT usuario FROM usuarios WHERE usuario=? AND senha=?",
            (self.user.text(), self.pwd.text())
        )

        ok = cur.fetchone()
        conn.close()

        if ok:
            self.close()
            self.on_success(ok[0])
        else:
            QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos")
