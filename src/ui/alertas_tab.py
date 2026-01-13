from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
)

from datetime import date, datetime
from database.db import connect


class AlertasTab(QWidget):
    def __init__(self):
        super().__init__()
        self.build()
        self.load()

    def build(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Mensalidades vencidas (pendentes)"))

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(
            ["Aluno", "Valor", "Venc", "Status", "Dias atraso"]
        )

        layout.addWidget(self.tabela)
        self.setLayout(layout)

    def load(self):
        hoje = date.today()

        conn = connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT a.nome, m.valor, m.data_vencimento, m.status
            FROM mensalidades m
            JOIN alunos a ON a.id = m.aluno_id
            WHERE m.status='PENDENTE'
        """)
        dados = cur.fetchall()
        conn.close()

        alertas = []
        for nome, valor, venc, status in dados:
            venc_date = datetime.fromisoformat(venc).date()
            dias = (hoje - venc_date).days
            if dias >= 0:
                alertas.append((nome, valor, venc, status, dias))

        self.tabela.setRowCount(len(alertas))
        for i, row in enumerate(alertas):
            for j, val in enumerate(row):
                self.tabela.setItem(i, j, QTableWidgetItem(str(val)))
