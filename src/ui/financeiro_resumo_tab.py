"""Aba de Resumo Financeiro com Receitas, Despesas e Projeções."""
from datetime import date, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QDialog, QFormLayout, QLineEdit, QDateEdit,
    QDoubleSpinBox, QCheckBox, QSpinBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor

from ui.base_tab import BaseTab, SCROLLBAR_STYLE
from database.db import (
    criar_lancamento, listar_lancamentos, excluir_lancamento, obter_resumo_financeiro
)
from ui.app_dialog import show_info, show_error, show_question


class FinanceiroResumoTab(BaseTab):
    """Aba de resumo financeiro com receitas, despesas e projeções."""

    def __init__(self):
        super().__init__()
        self.mes_atual = date.today().month
        self.ano_atual = date.today().year
        self.build_ui()
        self.load()

    def build_ui(self):
        layout = self.layout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Título
        title = QLabel("Resumo Financeiro")
        title.setStyleSheet(
            "color:#ffffff; font-size:22px; font-weight:700;"
            " font-family:'Arial Black',sans-serif; background:transparent; border:none;"
        )
        layout.addWidget(title)

        # Seletor de mês/ano
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(12)

        lbl_mes = QLabel("Mês/Ano:")
        lbl_mes.setStyleSheet("color:#aaaaaa; font-weight:600;")
        filter_layout.addWidget(lbl_mes)

        self.combo_mes = QComboBox()
        meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        self.combo_mes.addItems(meses)
        self.combo_mes.setCurrentIndex(self.mes_atual - 1)
        self.combo_mes.setStyleSheet(self._combo_style())
        self.combo_mes.currentIndexChanged.connect(self.load)
        filter_layout.addWidget(self.combo_mes)

        self.spin_ano = QSpinBox()
        self.spin_ano.setMinimum(2020)
        self.spin_ano.setMaximum(2100)
        self.spin_ano.setValue(self.ano_atual)
        self.spin_ano.setStyleSheet(self._spin_style())
        self.spin_ano.valueChanged.connect(self.load)
        filter_layout.addWidget(self.spin_ano)

        filter_layout.addStretch()

        btn_nova_receita = QPushButton("+ Receita")
        btn_nova_receita.setStyleSheet(self._btn_style_success())
        btn_nova_receita.clicked.connect(lambda: self.open_lancamento_dialog("RECEITA"))
        filter_layout.addWidget(btn_nova_receita)

        btn_nova_despesa = QPushButton("+ Despesa")
        btn_nova_despesa.setStyleSheet(self._btn_style_danger())
        btn_nova_despesa.clicked.connect(lambda: self.open_lancamento_dialog("DESPESA"))
        filter_layout.addWidget(btn_nova_despesa)

        layout.addLayout(filter_layout)

        # Cards de resumo
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        self.card_receita = self._create_card("💰 Receita Realizada", "R$ 0,00", "#4CAF50")
        self.card_despesa = self._create_card("💸 Despesas", "R$ 0,00", "#ff6b6b")
        self.card_saldo = self._create_card("📊 Saldo", "R$ 0,00", "#2196F3")
        self.card_projecao = self._create_card("🔮 Receita Projetada", "R$ 0,00", "#9C27B0")

        cards_layout.addWidget(self.card_receita)
        cards_layout.addWidget(self.card_despesa)
        cards_layout.addWidget(self.card_saldo)
        cards_layout.addWidget(self.card_projecao)

        layout.addLayout(cards_layout)

        # Tabelas de receitas e despesas
        tabelas_layout = QHBoxLayout()
        tabelas_layout.setSpacing(20)

        # Receitas
        receita_frame = QFrame()
        receita_frame.setStyleSheet("background: #161616; border-radius: 10px; border: 1px solid #222222;")
        receita_layout = QVBoxLayout(receita_frame)
        receita_layout.setContentsMargins(16, 16, 16, 16)
        receita_layout.setSpacing(12)

        lbl_receita = QLabel("Receitas Extras")
        lbl_receita.setStyleSheet("color: #4CAF50; font-size: 14px; font-weight: 700;")
        receita_layout.addWidget(lbl_receita)

        self.tabela_receitas = QTableWidget()
        self.tabela_receitas.setColumnCount(5)
        self.tabela_receitas.setHorizontalHeaderLabels(["Data", "Categoria", "Descrição", "Valor", ""])
        self.tabela_receitas.setStyleSheet(self._table_style())
        receita_layout.addWidget(self.tabela_receitas)

        tabelas_layout.addWidget(receita_frame)

        # Despesas
        despesa_frame = QFrame()
        despesa_frame.setStyleSheet("background: #161616; border-radius: 10px; border: 1px solid #222222;")
        despesa_layout = QVBoxLayout(despesa_frame)
        despesa_layout.setContentsMargins(16, 16, 16, 16)
        despesa_layout.setSpacing(12)

        lbl_despesa = QLabel("Despesas")
        lbl_despesa.setStyleSheet("color: #ff6b6b; font-size: 14px; font-weight: 700;")
        despesa_layout.addWidget(lbl_despesa)

        self.tabela_despesas = QTableWidget()
        self.tabela_despesas.setColumnCount(5)
        self.tabela_despesas.setHorizontalHeaderLabels(["Data", "Categoria", "Descrição", "Valor", ""])
        self.tabela_despesas.setStyleSheet(self._table_style())
        despesa_layout.addWidget(self.tabela_despesas)

        tabelas_layout.addWidget(despesa_frame)

        layout.addLayout(tabelas_layout)

    def load(self):
        """Carrega dados do mês selecionado."""
        self.mes_atual = self.combo_mes.currentIndex() + 1
        self.ano_atual = self.spin_ano.value()

        resumo = obter_resumo_financeiro(self.ano_atual, self.mes_atual)

        # Atualizar cards
        self._update_card_value(
            self.card_receita,
            f"R$ {resumo['receita_realizada']:,.2f}".replace(",", ".")
        )
        self._update_card_value(
            self.card_despesa,
            f"R$ {resumo['despesas']:,.2f}".replace(",", ".")
        )

        saldo_color = "#4CAF50" if resumo['saldo'] >= 0 else "#ff6b6b"
        self._update_card_value(
            self.card_saldo,
            f"R$ {resumo['saldo']:,.2f}".replace(",", "."),
            saldo_color
        )

        self._update_card_value(
            self.card_projecao,
            f"R$ {resumo['receita_projetada']:,.2f}".replace(",", ".")
        )

        # Carregar tabelas
        self._load_lancamentos()

    def _load_lancamentos(self):
        """Carrega receitas e despesas para o mês selecionado."""
        receitas = listar_lancamentos(self.ano_atual, self.mes_atual, "RECEITA")
        despesas = listar_lancamentos(self.ano_atual, self.mes_atual, "DESPESA")

        # Carregar receitas
        self.tabela_receitas.setRowCount(len(receitas))
        for i, (lanc_id, tipo, categoria, descricao, valor, data, recorrente) in enumerate(receitas):
            self.tabela_receitas.setItem(i, 0, QTableWidgetItem(str(data)))
            self.tabela_receitas.setItem(i, 1, QTableWidgetItem(categoria or "—"))
            self.tabela_receitas.setItem(i, 2, QTableWidgetItem(descricao or "—"))
            valor_item = QTableWidgetItem(f"R$ {valor:,.2f}".replace(",", "."))
            valor_item.setForeground(QColor("#4CAF50"))
            self.tabela_receitas.setItem(i, 3, valor_item)

            btn_del = QPushButton("🗑️")
            btn_del.setFixedSize(32, 32)
            btn_del.setStyleSheet("background: transparent; border: none; color: #888888;")
            btn_del.clicked.connect(lambda checked, lid=lanc_id: self.delete_lancamento(lid))
            self.tabela_receitas.setCellWidget(i, 4, btn_del)

        # Carregar despesas
        self.tabela_despesas.setRowCount(len(despesas))
        for i, (lanc_id, tipo, categoria, descricao, valor, data, recorrente) in enumerate(despesas):
            self.tabela_despesas.setItem(i, 0, QTableWidgetItem(str(data)))
            self.tabela_despesas.setItem(i, 1, QTableWidgetItem(categoria or "—"))
            self.tabela_despesas.setItem(i, 2, QTableWidgetItem(descricao or "—"))
            valor_item = QTableWidgetItem(f"R$ {valor:,.2f}".replace(",", "."))
            valor_item.setForeground(QColor("#ff6b6b"))
            self.tabela_despesas.setItem(i, 3, valor_item)

            btn_del = QPushButton("🗑️")
            btn_del.setFixedSize(32, 32)
            btn_del.setStyleSheet("background: transparent; border: none; color: #888888;")
            btn_del.clicked.connect(lambda checked, lid=lanc_id: self.delete_lancamento(lid))
            self.tabela_despesas.setCellWidget(i, 4, btn_del)

        self.tabela_receitas.resizeColumnsToContents()
        self.tabela_despesas.resizeColumnsToContents()

    def open_lancamento_dialog(self, tipo):
        """Abre diálogo para criar novo lançamento."""
        dlg = LancamentoDialog(self, tipo)
        if dlg.exec() == QDialog.Accepted:
            criar_lancamento(
                tipo=tipo,
                valor=dlg.valor,
                data=dlg.data_str,
                categoria=dlg.categoria,
                descricao=dlg.descricao,
                recorrente=dlg.recorrente
            )
            self.load()
            show_info(self, "Sucesso", f"{tipo.capitalize()} criada com sucesso!")

    def delete_lancamento(self, lanc_id):
        """Deleta um lançamento após confirmação."""
        if show_question(
            self,
            "Confirmar Exclusão",
            "Deseja realmente excluir este lançamento?",
            "Sim", "Não"
        ):
            excluir_lancamento(lanc_id)
            self.load()

    def _create_card(self, titulo, valor, cor):
        """Cria um card de resumo."""
        frame = QFrame()
        frame.setStyleSheet(
            f"background: #161616; border-radius: 10px; border: 2px solid {cor};"
            "padding: 16px;"
        )
        layout = QVBoxLayout(frame)
        layout.setSpacing(8)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet(f"color: {cor}; font-size: 12px; font-weight: 600;")
        layout.addWidget(lbl_titulo)

        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: 700;")
        lbl_valor.setObjectName("valor")
        layout.addWidget(lbl_valor)

        return frame

    def _update_card_value(self, card, valor, cor=None):
        """Atualiza o valor exibido em um card."""
        lbl = card.findChild(QLabel, "valor")
        if lbl:
            lbl.setText(valor)
            if cor:
                lbl.setStyleSheet(f"color: {cor}; font-size: 18px; font-weight: 700;")

    @staticmethod
    def _combo_style():
        return """
            QComboBox {
                background-color: #0e0e0e;
                padding: 7px 10px;
                border-radius: 10px;
                border: 1px solid #1e1e1e;
                font-size: 13px;
                color: #ffffff;
                min-width: 80px;
            }
            QComboBox:focus { border: 1.5px solid #cc1e1e; }
        """

    @staticmethod
    def _spin_style():
        return """
            QSpinBox {
                background-color: #0e0e0e;
                padding: 7px 10px;
                border-radius: 10px;
                border: 1px solid #1e1e1e;
                font-size: 13px;
                color: #ffffff;
                min-width: 80px;
            }
            QSpinBox:focus { border: 1.5px solid #cc1e1e; }
        """

    @staticmethod
    def _btn_style_success():
        return """
            QPushButton {
                background: #4CAF50; color: #ffffff;
                border: none; border-radius: 6px;
                font-size: 12px; font-weight: 600;
                padding: 6px 16px;
            }
            QPushButton:hover { background: #66BB6A; }
        """

    @staticmethod
    def _btn_style_danger():
        return """
            QPushButton {
                background: #ff6b6b; color: #ffffff;
                border: none; border-radius: 6px;
                font-size: 12px; font-weight: 600;
                padding: 6px 16px;
            }
            QPushButton:hover { background: #ff8787; }
        """

    @staticmethod
    def _table_style():
        return """
            QTableWidget {
                background: #0e0e0e; color: #ffffff;
                border: 1px solid #1e1e1e; border-radius: 8px;
                gridline-color: #1e1e1e;
            }
            QTableWidget::item { padding: 8px; }
            QTableWidget::item:selected { background: #cc1e1e; }
            QHeaderView::section {
                background: #161616; color: #aaaaaa;
                border: none; padding: 8px;
                font-weight: 600;
            }
        """


class LancamentoDialog(QDialog):
    """Diálogo para criar novo lançamento (receita ou despesa)."""

    def __init__(self, parent, tipo):
        super().__init__(parent)
        self.tipo = tipo
        self.valor = 0.0
        self.data_str = date.today().isoformat()
        self.categoria = ""
        self.descricao = ""
        self.recorrente = False

        self.setWindowTitle(f"Novo Lançamento - {tipo}")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setStyleSheet("background: #111111;")
        self.build_ui()

    def build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # Título
        titulo = QLabel(f"Novo Lançamento - {self.tipo}")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        titulo.setStyleSheet("color: #ffffff;")
        main.addWidget(titulo)

        # Formulário
        form = QFormLayout()
        form.setSpacing(12)

        # Data
        lbl_data = QLabel("Data:")
        lbl_data.setStyleSheet("color: #aaaaaa;")
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setStyleSheet(self._input_style())
        form.addRow(lbl_data, self.date_edit)

        # Categoria
        lbl_cat = QLabel("Categoria:")
        lbl_cat.setStyleSheet("color: #aaaaaa;")
        self.input_categoria = QLineEdit()
        self.input_categoria.setPlaceholderText("Ex: Aluguel, Alimento, etc...")
        self.input_categoria.setStyleSheet(self._input_style())
        form.addRow(lbl_cat, self.input_categoria)

        # Descrição
        lbl_desc = QLabel("Descrição:")
        lbl_desc.setStyleSheet("color: #aaaaaa;")
        self.input_descricao = QLineEdit()
        self.input_descricao.setPlaceholderText("Opcional")
        self.input_descricao.setStyleSheet(self._input_style())
        form.addRow(lbl_desc, self.input_descricao)

        # Valor
        lbl_valor = QLabel("Valor (R$):")
        lbl_valor.setStyleSheet("color: #aaaaaa;")
        self.spin_valor = QDoubleSpinBox()
        self.spin_valor.setMinimum(0.0)
        self.spin_valor.setMaximum(999999.99)
        self.spin_valor.setDecimals(2)
        self.spin_valor.setStyleSheet(self._input_style())
        form.addRow(lbl_valor, self.spin_valor)

        # Recorrente
        self.check_recorrente = QCheckBox("Despesa/Receita recorrente (mensal)")
        self.check_recorrente.setStyleSheet("color: #aaaaaa;")
        form.addRow("", self.check_recorrente)

        main.addLayout(form)

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(36)
        btn_cancelar.setStyleSheet(self._btn_style_secondary())
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        btn_confirmar = QPushButton("Confirmar")
        btn_confirmar.setFixedHeight(36)
        btn_confirmar.setStyleSheet(self._btn_style_primary())
        btn_confirmar.clicked.connect(self.confirmar)
        btn_layout.addWidget(btn_confirmar)

        main.addLayout(btn_layout)

    def confirmar(self):
        """Valida e confirma o lançamento."""
        if self.spin_valor.value() <= 0:
            show_error(self, "Erro", "O valor deve ser maior que zero.")
            return

        self.valor = self.spin_valor.value()
        self.data_str = self.date_edit.date().toPython().isoformat()
        self.categoria = self.input_categoria.text().strip()
        self.descricao = self.input_descricao.text().strip()
        self.recorrente = self.check_recorrente.isChecked()

        self.accept()

    @staticmethod
    def _input_style():
        return """
            QLineEdit, QDateEdit, QDoubleSpinBox {
                background: #0e0e0e; color: #ffffff;
                border: 1px solid #1e1e1e; border-radius: 6px;
                padding: 8px 12px; font-size: 12px;
            }
            QLineEdit:focus, QDateEdit:focus, QDoubleSpinBox:focus {
                border: 1.5px solid #cc1e1e;
            }
        """

    @staticmethod
    def _btn_style_primary():
        return """
            QPushButton {
                background: #cc1e1e; color: #ffffff;
                border: none; border-radius: 6px;
                font-size: 12px; font-weight: 600;
                padding: 6px 16px;
            }
            QPushButton:hover { background: #e02020; }
        """

    @staticmethod
    def _btn_style_secondary():
        return """
            QPushButton {
                background: #1e1e1e; color: #888888;
                border: 1px solid #2a2a2a; border-radius: 6px;
                font-size: 12px; font-weight: 500;
                padding: 6px 16px;
            }
            QPushButton:hover { background: #252525; color: #cccccc; }
        """
