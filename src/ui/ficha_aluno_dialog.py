"""Ficha do aluno: detalhes completos, frequência e status de pagamento.

Reutilizada pela aba Alunos e pelo Dashboard (ao clicar num aluno).
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QWidget, QPushButton
)
from PySide6.QtCore import Qt

from database.db import get_conn, obter_percentual_presenca, obter_status_pagamento_mes


_BELT_COLORS = {
    "Branca": "#e8e8e8", "Cinza": "#8a8a8a", "Amarela": "#f2c200",
    "Laranja": "#e67e22", "Verde": "#2e9e4f", "Azul": "#1a4fa0",
    "Roxa": "#6b2fa0", "Marrom": "#7a4a20", "Preta": "#444444",
}


def _belt_color(faixa):
    if not faixa:
        return "#888888"
    if faixa in _BELT_COLORS:
        return _BELT_COLORS[faixa]
    for base, col in _BELT_COLORS.items():
        if base.lower() in faixa.lower():
            return col
    return "#888888"


class FichaAlunoDialog(QDialog):
    def __init__(self, aluno_id, tipo="adulto", parent=None):
        super().__init__(parent)
        self.aluno_id = aluno_id
        # normaliza tipo -> 'adulto' | 'kid'
        self.tipo = "kid" if str(tipo).startswith("kid") else "adulto"
        self.setWindowTitle("Ficha do Aluno")
        self.resize(560, 640)
        self.setStyleSheet("QDialog { background: #111111; }")
        self._build()

    def _fetch(self):
        conn = get_conn()
        cur = conn.cursor()
        if self.tipo == "adulto":
            cur.execute("""
                SELECT nome, cpf, email, telefone, cep, endereco, data_nascimento,
                       faixa, grau, peso, altura, plano
                FROM alunos WHERE id = ?
            """, (self.aluno_id,))
        else:
            cur.execute("""
                SELECT nome, cpf, email, telefone, cep, endereco, data_nascimento,
                       faixa, grau, peso, altura, plano, resp_nome, resp_cpf
                FROM kids WHERE id = ?
            """, (self.aluno_id,))
        row = cur.fetchone()
        conn.close()
        return row

    def _build(self):
        dados = self._fetch()
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        if not dados:
            root.addWidget(QLabel("Aluno não encontrado."))
            return

        nome = dados[0]
        faixa = dados[7] or "Branca"
        grau = dados[8] or ""

        # ── HEADER ──
        header = QFrame()
        header.setStyleSheet("background: #161616; border-bottom: 1px solid #222222;")
        hl = QVBoxLayout(header)
        hl.setContentsMargins(24, 20, 24, 16)
        hl.setSpacing(6)

        lbl_nome = QLabel(nome)
        lbl_nome.setStyleSheet("color:#ffffff; font-size:22px; font-weight:700; background:transparent;")
        hl.addWidget(lbl_nome)

        faixa_row = QHBoxLayout()
        faixa_row.setSpacing(8)
        chip = QLabel()
        chip.setFixedSize(30, 8)
        border = "border:1px solid #555;" if faixa == "Preta" else "border:none;"
        chip.setStyleSheet(f"background:{_belt_color(faixa)}; border-radius:3px; {border}")
        faixa_row.addWidget(chip)
        lbl_faixa = QLabel(f"Faixa {faixa}" + (f" · {grau}" if grau else ""))
        lbl_faixa.setStyleSheet("color:#aaaaaa; font-size:12px; background:transparent;")
        faixa_row.addWidget(lbl_faixa)
        faixa_row.addStretch()
        hl.addLayout(faixa_row)

        root.addWidget(header)

        # ── DESTAQUES: frequência + pagamento ──
        destaque_row = QHBoxLayout()
        destaque_row.setContentsMargins(24, 16, 24, 8)
        destaque_row.setSpacing(12)

        pct, presencas = obter_percentual_presenca(self.aluno_id, self.tipo)
        destaque_row.addWidget(self._card_destaque(
            "FREQUÊNCIA (MÊS)", f"{pct:.0f}%", f"{presencas} de 44 aulas", "#2e9e4f"
        ))

        status_mes = {}
        try:
            status_mes = obter_status_pagamento_mes()
        except Exception:
            status_mes = {}
        chave = self.aluno_id if self.tipo == "adulto" else -self.aluno_id
        status_pag = status_mes.get(chave, "Sem cobrança")
        cores_pag = {"Pago": "#2e9e4f", "Atrasado": "#cc1e1e", "A Vencer": "#b8860e"}
        destaque_row.addWidget(self._card_destaque(
            "PAGAMENTO (MÊS)", status_pag, "", cores_pag.get(status_pag, "#555555")
        ))

        root.addLayout(destaque_row)

        # ── DETALHES ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(24, 8, 24, 16)
        cl.setSpacing(6)

        campos = [
            ("CPF", dados[1]), ("E-mail", dados[2]), ("Telefone", dados[3]),
            ("CEP", dados[4]), ("Endereço", dados[5]), ("Nascimento", dados[6]),
            ("Peso", dados[9]), ("Altura", dados[10]), ("Plano", dados[11]),
        ]
        if self.tipo == "kid" and len(dados) > 13:
            campos += [("Responsável", dados[12]), ("CPF do Responsável", dados[13])]

        for rotulo, valor in campos:
            cl.addWidget(self._linha(rotulo, valor))

        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        # ── FECHAR ──
        footer = QHBoxLayout()
        footer.setContentsMargins(24, 8, 24, 16)
        footer.addStretch()
        btn = QPushButton("Fechar")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(36)
        btn.setStyleSheet(
            "QPushButton { background:#cc1e1e; color:#fff; border:none; border-radius:7px;"
            " font-size:13px; font-weight:600; padding:0 20px; } QPushButton:hover { background:#e02020; }"
        )
        btn.clicked.connect(self.accept)
        footer.addWidget(btn)
        root.addLayout(footer)

    def _card_destaque(self, titulo, valor, sub, cor):
        card = QFrame()
        card.setStyleSheet(
            f"QFrame {{ background:#161616; border:1px solid #222222; border-left:3px solid {cor};"
            f" border-radius:10px; }}"
        )
        v = QVBoxLayout(card)
        v.setContentsMargins(14, 12, 14, 12)
        v.setSpacing(2)
        t = QLabel(titulo)
        t.setStyleSheet("color:#555555; font-size:10px; font-weight:600; background:transparent; border:none;")
        val = QLabel(str(valor))
        val.setStyleSheet(f"color:{cor}; font-size:22px; font-weight:700; background:transparent; border:none;")
        v.addWidget(t)
        v.addWidget(val)
        if sub:
            s = QLabel(sub)
            s.setStyleSheet("color:#666666; font-size:10px; background:transparent; border:none;")
            v.addWidget(s)
        return card

    def _linha(self, rotulo, valor):
        row = QFrame()
        row.setStyleSheet("QFrame { background: transparent; border-bottom: 1px solid #191919; }")
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 6, 0, 6)
        lbl_r = QLabel(rotulo)
        lbl_r.setFixedWidth(150)
        lbl_r.setStyleSheet("color:#666666; font-size:12px; background:transparent; border:none;")
        lbl_v = QLabel(str(valor) if valor not in (None, "") else "-")
        lbl_v.setWordWrap(True)
        lbl_v.setStyleSheet("color:#dddddd; font-size:13px; background:transparent; border:none;")
        rl.addWidget(lbl_r)
        rl.addWidget(lbl_v, 1)
        return row
