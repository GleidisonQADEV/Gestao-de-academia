from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem
)

from database.db import connect
from services.financeiro_service import FinanceiroService


class FinanceiroTab(QWidget):
    def __init__(self, refresh_callbacks=None):
        super().__init__()
        self.refresh_callbacks = refresh_callbacks or []
        self.build()
        self.load()

    def build(self):
        layout = QVBoxLayout()

        btn_gerar = QPushButton("Gerar mensalidades do mês")
        btn_gerar.clicked.connect(self.gerar)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels(
            ["ID", "Aluno", "Valor", "Venc", "Pagto", "Status", "AlunoID"]
        )
        self.tabela.setColumnHidden(6, True)

        btn_pago = QPushButton("Marcar como PAGO")
        btn_pago.clicked.connect(self.pagar)

        layout.addWidget(btn_gerar)
        layout.addWidget(self.tabela)
        layout.addWidget(btn_pago)
        self.setLayout(layout)

    def gerar(self):
        FinanceiroService.gerar_mensalidades()
        self.load()
        self.refresh_all()

    def pagar(self):
        linha = self.tabela.currentRow()
        if linha < 0:
            return

        mensal_id = self.tabela.item(linha, 0).text()
        FinanceiroService.marcar_pago(mensal_id)

        self.load()
        self.refresh_all()

    def load(self):
        conn = connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.id, a.nome, m.valor, m.data_vencimento, 
                   m.data_pagamento, m.status, a.id
            FROM mensalidades m
            JOIN alunos a ON a.id = m.aluno_id
            ORDER BY m.data_vencimento DESC
        """)
        dados = cur.fetchall()
        conn.close()

        self.tabela.setRowCount(len(dados))
        for i, row in enumerate(dados):
            for j, val in enumerate(row):
                self.tabela.setItem(i, j, QTableWidgetItem(str(val) if val else ""))

    def refresh_all(self):
        for cb in self.refresh_callbacks:
            cb()
