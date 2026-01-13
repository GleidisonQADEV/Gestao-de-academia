from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QFileDialog
)
from datetime import date, datetime
from database.db import connect
from utils.pdf_report import gerar_relatorio_mes


class FinanceiroTab(QWidget):
    def __init__(self, refresh_callbacks=None):
        super().__init__()
        self.refresh_callbacks = refresh_callbacks or []
        self.build()
        self.load()

    # ---------------- UI ----------------

    def build(self):
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("Aluno:"))

        self.combo_alunos = QComboBox()
        self.combo_alunos.currentIndexChanged.connect(self.load_mensalidades)

        btn_gerar = QPushButton("Gerar mensalidades do mês")
        btn_gerar.clicked.connect(self.gerar_mensalidades)

        btn_pdf = QPushButton("Gerar PDF do mês")
        btn_pdf.clicked.connect(self.gerar_pdf)

        top.addWidget(self.combo_alunos)
        top.addWidget(btn_gerar)
        top.addWidget(btn_pdf)
        layout.addLayout(top)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Aluno", "Vencimento", "Valor", "Status", "Pago em"
        ])
        self.tabela.cellDoubleClicked.connect(self.marcar_pago)

        layout.addWidget(self.tabela)

    # ---------------- DADOS ----------------

    def load(self):
        self.load_alunos_combo()
        self.load_mensalidades()

    def load_alunos_combo(self):
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT id, nome FROM alunos ORDER BY nome")
        alunos = cur.fetchall()
        conn.close()

        self.combo_alunos.blockSignals(True)
        self.combo_alunos.clear()
        self.combo_alunos.addItem("Todos", None)

        for a in alunos:
            self.combo_alunos.addItem(a[1], a[0])

        self.combo_alunos.blockSignals(False)

    def load_mensalidades(self):
        aluno_id = self.combo_alunos.currentData()

        conn = connect()
        cur = conn.cursor()

        if aluno_id:
            cur.execute("""
                SELECT m.id, a.nome, m.data_vencimento, m.valor, m.status, m.data_pagamento
                FROM mensalidades m
                JOIN alunos a ON a.id = m.aluno_id
                WHERE aluno_id=?
                ORDER BY data_vencimento DESC
            """, (aluno_id,))
        else:
            cur.execute("""
                SELECT m.id, a.nome, m.data_vencimento, m.valor, m.status, m.data_pagamento
                FROM mensalidades m
                JOIN alunos a ON a.id = m.aluno_id
                ORDER BY data_vencimento DESC
            """)

        rows = cur.fetchall()
        conn.close()

        self.tabela.setRowCount(0)

        for row in rows:
            r = self.tabela.rowCount()
            self.tabela.insertRow(r)
            for c, v in enumerate(row):
                self.tabela.setItem(r, c, QTableWidgetItem(str(v)))

    # ---------------- REGRAS ----------------

    def gerar_mensalidades(self):
        hoje = date.today()

        conn = connect()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, valor_mensalidade, dia_vencimento
            FROM alunos
            WHERE status='ATIVO'
        """)

        alunos = cur.fetchall()

        for a in alunos:
            aluno_id, valor, dia = a
            venc = date(hoje.year, hoje.month, min(dia, 28))

            cur.execute("""
                SELECT id FROM mensalidades
                WHERE aluno_id=? AND data_vencimento=?
            """, (aluno_id, venc.isoformat()))

            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO mensalidades (aluno_id, valor, data_vencimento, status)
                    VALUES (?, ?, ?, 'ABERTO')
                """, (aluno_id, valor, venc.isoformat()))

        conn.commit()
        conn.close()

        self.load()
        for cb in self.refresh_callbacks:
            cb()

    # ✅ DUPLO CLIQUE → MARCAR PAGO
    def marcar_pago(self, row, col):
        status = self.tabela.item(row, 4).text()
        if status == "PAGO":
            return

        mensal_id = self.tabela.item(row, 0).text()

        if QMessageBox.question(
            self, "Confirmar", "Marcar como PAGO?"
        ) != QMessageBox.Yes:
            return

        conn = connect()
        cur = conn.cursor()
        cur.execute("""
            UPDATE mensalidades
            SET status='PAGO', data_pagamento=DATE('now')
            WHERE id=?
        """, (mensal_id,))
        conn.commit()
        conn.close()

        self.load()

    # ---------------- PDF ----------------

    def gerar_pdf(self):
        hoje = datetime.today()
        ano = hoje.year
        mes = hoje.month

        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar PDF", f"relatorio_{mes}_{ano}.pdf", "PDF (*.pdf)"
        )

        if not caminho:
            return

        gerar_relatorio_mes(ano, mes, caminho)

        QMessageBox.information(self, "PDF", "Relatório gerado com sucesso!")
