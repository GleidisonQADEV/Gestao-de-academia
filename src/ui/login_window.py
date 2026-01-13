from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from database.db import connect


class LoginWindow(QWidget):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.setWindowTitle("Login - Academia Jiu-Jitsu")
        self.resize(300, 200)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Usuário"))
        self.user = QLineEdit()
        layout.addWidget(self.user)

        layout.addWidget(QLabel("Senha"))
        self.pwd = QLineEdit()
        self.pwd.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pwd)

        btn = QPushButton("Entrar")
        btn.clicked.connect(self.login)
        layout.addWidget(btn)

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
            self.on_success(ok[0])  # passa o usuário logado
            self.close()
        else:
            QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos")
