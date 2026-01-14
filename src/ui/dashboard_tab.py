from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
from database.db import connect
from datetime import date


class Card(QFrame):
    def __init__(self, titulo):
        super().__init__()
        self.setStyleSheet("border-radius:14px;")
        layout = QVBoxLayout(self)

        self.titulo = QLabel(titulo)
        self.valor = QLabel("0")
        self.valor.setStyleSheet("font-size:24px;font-weight:bold;")

        layout.addWidget(self.titulo)
        layout.addWidget(self.valor)

    def set(self, v):
        self.valor.setText(str(v))


class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        cards = QGridLayout()

        self.c1 = Card("Alunos Ativos")
        self.c2 = Card("Inadimplentes")
        self.c3 = Card("Faturamento Mês")

        cards.addWidget(self.c1, 0, 0)
        cards.addWidget(self.c2, 0, 1)
        cards.addWidget(self.c3, 0, 2)

        layout.addLayout(cards)

        # -------- GRÁFICO --------
        self.fig = Figure(figsize=(5, 3))
        self.canvas = Canvas(self.fig)
        layout.addWidget(self.canvas)

        self.load()

    def load(self):
        conn = connect()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM alunos WHERE status='ATIVO'")
        ativos = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(DISTINCT aluno_id)
            FROM mensalidades
            WHERE status='PENDENTE' AND date(data_vencimento) < date('now')
        """)
        inad = cur.fetchone()[0]

        cur.execute("""
            SELECT IFNULL(SUM(valor),0)
            FROM mensalidades
            WHERE status='PAGO'
              AND strftime('%Y-%m', data_pagamento)=strftime('%Y-%m','now')
        """)
        fat = cur.fetchone()[0]

        # gráfico últimos 6 meses
        cur.execute("""
            SELECT strftime('%m', data_pagamento), SUM(valor)
            FROM mensalidades
            WHERE status='PAGO'
            GROUP BY strftime('%Y-%m', data_pagamento)
            ORDER BY data_pagamento DESC
            LIMIT 6
        """)
        data = cur.fetchall()
        conn.close()

        self.c1.set(ativos)
        self.c2.set(inad)
        self.c3.set(f"R$ {fat:.2f}")

        self.fig.clear()
        ax = self.fig.add_subplot(111)
        meses = [d[0] for d in reversed(data)]
        valores = [d[1] for d in reversed(data)]
        ax.plot(meses, valores, marker="o")
        ax.set_title("Faturamento últimos meses")
        self.canvas.draw()
