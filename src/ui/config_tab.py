from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from database.db import connect


class ConfigTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        lbl = QLabel("Configurações do Sistema")
        lbl.setStyleSheet("font-size:18px;font-weight:600;")

        btn_reset = QPushButton("Resetar Banco de Dados")
        btn_reset.setObjectName("secondary")
        btn_reset.clicked.connect(self.reset_db)

        layout.addWidget(lbl)
        layout.addSpacing(20)
        layout.addWidget(btn_reset)
        layout.addStretch()

    def reset_db(self):
        resp = QMessageBox.question(
            self,
            "Confirmação",
            "Isso irá apagar TODOS os dados.\nDeseja continuar?",
            QMessageBox.Yes | QMessageBox.No
        )

        if resp == QMessageBox.Yes:
            conn = connect()
            cur = conn.cursor()
            cur.execute("DELETE FROM mensalidades")
            cur.execute("DELETE FROM alunos")
            conn.commit()
            conn.close()

            QMessageBox.information(self, "OK", "Banco resetado com sucesso.")
