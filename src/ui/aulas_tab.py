"""Aba de Aulas — diário do professor.

Permite registrar anotações sobre cada aula: data, horário, conteúdo,
dificuldades observadas e observações gerais.
"""
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QDialog, QLineEdit, QTextEdit, QDateEdit, QTimeEdit, QFormLayout
)
from PySide6.QtCore import Qt, QDate, QTime

from ui.base_tab import BaseTab, SCROLLBAR_STYLE
from ui.app_dialog import show_info, show_error, show_question
from database.db import criar_aula, listar_aulas, atualizar_aula, excluir_aula


def _fmt_data(iso):
    try:
        return datetime.strptime(iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return iso or ""


class AulasTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.build_ui()
        self.load()

    def build_ui(self):
        layout = self.layout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        top = QHBoxLayout()
        title = QLabel("Aulas — Diário do Professor")
        title.setStyleSheet(
            "color:#ffffff; font-size:22px; font-weight:700;"
            " font-family:'Arial Black',sans-serif; background:transparent; border:none;"
        )
        top.addWidget(title)
        top.addStretch()

        btn_nova = QPushButton("+ Nova aula")
        btn_nova.setFixedHeight(36)
        btn_nova.setCursor(Qt.PointingHandCursor)
        btn_nova.setStyleSheet(
            "QPushButton { background:#cc1e1e; color:#fff; border:none; border-radius:7px;"
            " font-size:12px; font-weight:700; padding:0 18px; } QPushButton:hover { background:#e02020; }"
        )
        btn_nova.clicked.connect(self.nova_aula)
        top.addWidget(btn_nova)
        layout.addLayout(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea {{ border:none; background:transparent; }} {SCROLLBAR_STYLE}"
        )
        self.lista_widget = QWidget()
        self.lista_widget.setStyleSheet("background:transparent;")
        self.lista_layout = QVBoxLayout(self.lista_widget)
        self.lista_layout.setContentsMargins(0, 0, 0, 0)
        self.lista_layout.setSpacing(10)
        self.lista_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.lista_widget)
        layout.addWidget(scroll, 1)

    def load(self):
        while self.lista_layout.count():
            item = self.lista_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            aulas = listar_aulas()
        except Exception as e:
            show_error(self, "Erro", f"Erro ao carregar aulas: {str(e)}")
            return

        if not aulas:
            vazio = QLabel("Nenhuma aula registrada ainda. Clique em '+ Nova aula'.")
            vazio.setAlignment(Qt.AlignCenter)
            vazio.setStyleSheet("color:#9a9a9a; font-size:13px; background:transparent; border:none;")
            self.lista_layout.addWidget(vazio)
            return

        for aula in aulas:
            self.lista_layout.addWidget(self._card_aula(aula))

    def _card_aula(self, aula):
        # aula: id, data, hora, titulo, conteudo, dificuldades, observacoes
        aula_id, data, hora, titulo, conteudo, dificuldades, observacoes = aula
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background:#161616; border:1px solid #1e1e1e; border-radius:9px; }"
        )
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(6)

        cabecalho = QHBoxLayout()
        data_hora = _fmt_data(data) + (f" · {hora}" if hora else "")
        lbl_data = QLabel(data_hora)
        lbl_data.setStyleSheet("color:#cc1e1e; font-size:12px; font-weight:700; background:transparent; border:none;")
        cabecalho.addWidget(lbl_data)
        cabecalho.addStretch()

        btn_edit = QPushButton("Editar")
        btn_edit.setFixedHeight(28)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setStyleSheet(
            "QPushButton { background:#1e1e1e; color:#888; border:1px solid #2a2a2a;"
            " border-radius:5px; font-size:11px; padding:0 12px; } QPushButton:hover { background:#252525; color:#ccc; }"
        )
        btn_edit.clicked.connect(lambda: self.editar_aula(aula))
        cabecalho.addWidget(btn_edit)

        btn_del = QPushButton("Excluir")
        btn_del.setFixedHeight(28)
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setStyleSheet(
            "QPushButton { background:rgba(204,30,30,0.08); color:#c04444;"
            " border:1px solid rgba(204,30,30,0.2); border-radius:5px; font-size:11px; padding:0 12px; }"
            "QPushButton:hover { background:rgba(204,30,30,0.15); color:#e05050; }"
        )
        btn_del.clicked.connect(lambda: self.excluir_aula(aula_id))
        cabecalho.addWidget(btn_del)
        lay.addLayout(cabecalho)

        if titulo:
            lbl_titulo = QLabel(titulo)
            lbl_titulo.setStyleSheet("color:#ffffff; font-size:14px; font-weight:600; background:transparent; border:none;")
            lbl_titulo.setWordWrap(True)
            lay.addWidget(lbl_titulo)

        for rotulo, valor in (("Conteúdo", conteudo), ("Dificuldades", dificuldades), ("Observações", observacoes)):
            if valor:
                bloco = QLabel(f"<b style='color:#9a9a9a;'>{rotulo}:</b> <span style='color:#cccccc;'>{valor}</span>")
                bloco.setWordWrap(True)
                bloco.setStyleSheet("font-size:12px; background:transparent; border:none;")
                lay.addWidget(bloco)

        return card

    def nova_aula(self):
        dlg = AulaDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self.load()

    def editar_aula(self, aula):
        dlg = AulaDialog(self, aula)
        if dlg.exec() == QDialog.Accepted:
            self.load()

    def excluir_aula(self, aula_id):
        if show_question(self, "Excluir aula", "Deseja realmente excluir este registro de aula?"):
            try:
                excluir_aula(aula_id)
                self.load()
            except Exception as e:
                show_error(self, "Erro", f"Erro ao excluir: {str(e)}")


class AulaDialog(QDialog):
    def __init__(self, parent, aula=None):
        super().__init__(parent)
        self.aula = aula  # None = nova
        self.setWindowTitle("Registro de Aula")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setStyleSheet("QDialog { background:#111111; }")
        self._build()
        if aula:
            self._preencher(aula)

    def _build(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(14)

        card = QFrame()
        card.setStyleSheet("background:#161616; border:1px solid #222222; border-radius:10px;")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(12)

        titulo = QLabel("Registro de Aula")
        titulo.setStyleSheet("color:#fff; font-size:15px; font-weight:700; background:transparent; border:none;")
        lay.addWidget(titulo)

        _field = (
            "background:#0e0e0e; padding:8px 10px; border-radius:8px; border:1px solid #1e1e1e;"
            " font-size:13px; color:#cccccc;"
        )
        _lbl = "color:#888; font-size:12px; background:transparent; border:none;"

        form = QFormLayout()
        form.setSpacing(10)

        self.data = QDateEdit()
        self.data.setCalendarPopup(True)
        self.data.setDisplayFormat("dd/MM/yyyy")
        self.data.setDate(QDate.currentDate())
        self.data.setStyleSheet(f"QDateEdit {{ {_field} }}")
        l1 = QLabel("Data:"); l1.setStyleSheet(_lbl)
        form.addRow(l1, self.data)

        self.hora = QTimeEdit()
        self.hora.setDisplayFormat("HH:mm")
        self.hora.setTime(QTime.currentTime())
        self.hora.setStyleSheet(f"QTimeEdit {{ {_field} }}")
        l2 = QLabel("Horário:"); l2.setStyleSheet(_lbl)
        form.addRow(l2, self.hora)

        self.titulo = QLineEdit()
        self.titulo.setPlaceholderText("Ex.: Guarda fechada / Passagem de guarda")
        self.titulo.setStyleSheet(f"QLineEdit {{ {_field} }}")
        l3 = QLabel("Título / Tema:"); l3.setStyleSheet(_lbl)
        form.addRow(l3, self.titulo)
        lay.addLayout(form)

        self.conteudo = self._textarea("O que foi dado na aula...")
        lay.addWidget(self._campo_label("Conteúdo da aula"))
        lay.addWidget(self.conteudo)

        self.dificuldades = self._textarea("Dificuldades observadas nos alunos...")
        lay.addWidget(self._campo_label("Dificuldades"))
        lay.addWidget(self.dificuldades)

        self.observacoes = self._textarea("Observações gerais...")
        lay.addWidget(self._campo_label("Observações"))
        lay.addWidget(self.observacoes)

        botoes = QHBoxLayout()
        botoes.addStretch()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(36)
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_cancelar.setStyleSheet(
            "QPushButton { background:#1e1e1e; color:#ccc; border:1px solid #2a2a2a;"
            " border-radius:7px; font-size:12px; font-weight:600; padding:0 18px; } QPushButton:hover { background:#252525; color:#fff; }"
        )
        btn_cancelar.clicked.connect(self.reject)
        botoes.addWidget(btn_cancelar)

        btn_salvar = QPushButton("Salvar")
        btn_salvar.setFixedHeight(36)
        btn_salvar.setCursor(Qt.PointingHandCursor)
        btn_salvar.setStyleSheet(
            "QPushButton { background:#cc1e1e; color:#fff; border:none; border-radius:7px;"
            " font-size:12px; font-weight:700; padding:0 22px; } QPushButton:hover { background:#e02020; }"
        )
        btn_salvar.clicked.connect(self._salvar)
        botoes.addWidget(btn_salvar)
        lay.addLayout(botoes)

        main.addWidget(card)

    def _campo_label(self, texto):
        lbl = QLabel(texto)
        lbl.setStyleSheet("color:#888; font-size:12px; background:transparent; border:none;")
        return lbl

    def _textarea(self, placeholder):
        t = QTextEdit()
        t.setPlaceholderText(placeholder)
        t.setMinimumHeight(60)
        t.setStyleSheet(
            "QTextEdit { background:#0e0e0e; border:1px solid #1e1e1e; border-radius:8px;"
            " color:#cccccc; font-size:13px; padding:6px; } QTextEdit:focus { border:1.5px solid #cc1e1e; }"
        )
        return t

    def _preencher(self, aula):
        _id, data, hora, titulo, conteudo, dificuldades, observacoes = aula
        try:
            d = datetime.strptime(data, "%Y-%m-%d")
            self.data.setDate(QDate(d.year, d.month, d.day))
        except Exception:
            pass
        if hora:
            try:
                h, m = hora.split(":")[:2]
                self.hora.setTime(QTime(int(h), int(m)))
            except Exception:
                pass
        self.titulo.setText(titulo or "")
        self.conteudo.setPlainText(conteudo or "")
        self.dificuldades.setPlainText(dificuldades or "")
        self.observacoes.setPlainText(observacoes or "")

    def _salvar(self):
        data = self.data.date().toString("yyyy-MM-dd")
        hora = self.hora.time().toString("HH:mm")
        titulo = self.titulo.text().strip()
        conteudo = self.conteudo.toPlainText().strip()
        dificuldades = self.dificuldades.toPlainText().strip()
        observacoes = self.observacoes.toPlainText().strip()

        if not (titulo or conteudo or dificuldades or observacoes):
            show_error(self, "Registro vazio", "Preencha ao menos o título ou o conteúdo da aula.")
            return

        try:
            if self.aula:
                atualizar_aula(self.aula[0], data, hora, titulo, conteudo, dificuldades, observacoes)
            else:
                criar_aula(data, hora, titulo, conteudo, dificuldades, observacoes)
            self.accept()
        except Exception as e:
            show_error(self, "Erro", f"Erro ao salvar aula: {str(e)}")
