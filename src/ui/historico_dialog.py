from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem
from database.db import connect


class HistoricoDialog(QDialog):
    def __init__(self, aluno_id, nome):
        super().__init__()
        self.setWindowTitle(f"Histórico Financeiro - {nome}")
        self.resize(500, 400)

        layout = QVBoxLayout(self)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(
            ["Vencimento", "Valor", "Status", "Pago em"]
        )

        layout.addWidget(self.tabela)
        self.load(aluno_id)

    def load(self, aluno_id):
        conn = connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT data_vencimento, valor, status, data_pagamento
            FROM mensalidades
            WHERE aluno_id=?
            ORDER BY data_vencimento DESC
        """, (aluno_id,))
        rows = cur.fetchall()
        conn.close()

        self.tabela.setRowCount(0)
        for row in rows:
            r = self.tabela.rowCount()
            self.tabela.insertRow(r)
            for c, v in enumerate(row):
                self.tabela.setItem(r, c, QTableWidgetItem(str(v)))
