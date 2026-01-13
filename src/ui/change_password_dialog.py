from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from database.db import connect


class ChangePasswordDialog(QDialog):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Trocar Senha")
        self.resize(300, 220)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Senha atual"))
        self.atual = QLineEdit()
        self.atual.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.atual)

        layout.addWidget(QLabel("Nova senha"))
        self.nova = QLineEdit()
        self.nova.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.nova)

        layout.addWidget(QLabel("Confirmar nova senha"))
        self.conf = QLineEdit()
        self.conf.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.conf)

        btn = QPushButton("Alterar senha")
        btn.clicked.connect(self.alterar)
        layout.addWidget(btn)

    def alterar(self):
        if self.nova.text() != self.conf.text():
            QMessageBox.warning(self, "Erro", "As senhas não conferem")
            return

        conn = connect()
        cur = conn.cursor()

        cur.execute(
            "SELECT id FROM usuarios WHERE usuario=? AND senha=?",
            (self.usuario, self.atual.text())
        )

        if not cur.fetchone():
            QMessageBox.warning(self, "Erro", "Senha atual incorreta")
            conn.close()
            return

        cur.execute(
            "UPDATE usuarios SET senha=? WHERE usuario=?",
            (self.nova.text(), self.usuario)
        )

        conn.commit()
        conn.close()

        QMessageBox.information(self, "OK", "Senha alterada com sucesso")
        self.close()
