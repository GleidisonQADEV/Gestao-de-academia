from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from database.db import get_conn, obter_percentual_presenca


class AlunoProfile(QWidget):
    def __init__(self, aluno_id):
        super().__init__()
        self.aluno_id = aluno_id
        layout = QVBoxLayout(self)

        self.info = QLabel()
        layout.addWidget(self.info)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["Vencimento", "Valor", "Pagamento", "Status"])
        layout.addWidget(self.tabela)

        self.load()

    def load(self):
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT nome, cpf, telefone, faixa, email FROM alunos WHERE id=?", (self.aluno_id,))
        a = cur.fetchone()

        pct, presencas = obter_percentual_presenca(self.aluno_id, "adulto")

        self.info.setText(
            f"<b>{a[0]}</b><br>CPF: {a[1]} | Tel: {a[2]} | Faixa: {a[3]}<br>{a[4]}"
            f"<br>Presença no mês: <b>{pct:.1f}%</b> ({presencas} de 44 aulas)"
        )

        cur.execute("""
            SELECT data_vencimento, valor, data_pagamento, status
            FROM mensalidades WHERE aluno_id=?
        """, (self.aluno_id,))
        rows = cur.fetchall()
        conn.close()

        self.tabela.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j, v in enumerate(r):
                self.tabela.setItem(i, j, QTableWidgetItem(str(v)))
