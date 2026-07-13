"""Diálogo para gerenciar dependentes ao inativar responsável."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QSpinBox, QDoubleSpinBox, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class InativarDependentesDialog(QDialog):
    """Diálogo para escolher entre inativar ou ajustar valores dos dependentes."""

    def __init__(self, parent, responsavel_nome, dependentes):
        super().__init__(parent)
        self.responsavel_nome = responsavel_nome
        self.dependentes = dependentes  # dict: {'adultos': [...], 'kids': [...]}
        self.total_dependentes = len(dependentes.get("adultos", [])) + len(dependentes.get("kids", []))
        self.escolha = None  # 'inativar', 'ajustar', ou None (cancelar)
        self.valores_ajustados = {}  # {id: novo_valor}

        self.setWindowTitle("Gerenciar Dependentes")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setStyleSheet("background: #111111;")
        self.build_ui()

    def build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # Título
        title = QLabel("⚠️  Dependentes do Responsável")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #ffffff;")
        main.addWidget(title)

        # Descrição
        desc = QLabel(
            f"'{self.responsavel_nome}' possui {self.total_dependentes} dependente(s).\n"
            "O que você deseja fazer?"
        )
        desc.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        main.addWidget(desc)

        # Opções de ação
        action_frame = QFrame()
        action_frame.setStyleSheet("background: #161616; border-radius: 10px; border: 1px solid #222222;")
        action_layout = QVBoxLayout(action_frame)
        action_layout.setContentsMargins(16, 16, 16, 16)
        action_layout.setSpacing(12)

        # Opção 1: Inativar todos
        opt1_label = QLabel("🔴 Inativar todos os dependentes")
        opt1_label.setStyleSheet("color: #ffffff; font-weight: 600; font-size: 12px;")
        opt1_desc = QLabel("Os dependentes também ficarão inativos.")
        opt1_desc.setStyleSheet("color: #888888; font-size: 11px;")

        btn_opt1 = QPushButton("Inativar Dependentes")
        btn_opt1.setStyleSheet(self._btn_style_danger())
        btn_opt1.clicked.connect(self.escolher_inativar)

        opt1_box = QHBoxLayout()
        opt1_text = QVBoxLayout()
        opt1_text.addWidget(opt1_label)
        opt1_text.addWidget(opt1_desc)
        opt1_box.addLayout(opt1_text)
        opt1_box.addStretch()
        opt1_box.addWidget(btn_opt1)
        action_layout.addLayout(opt1_box)

        action_layout.addSpacing(8)

        # Opção 2: Ajustar valores
        opt2_label = QLabel("⚙️  Ajustar valores de mensalidades")
        opt2_label.setStyleSheet("color: #ffffff; font-weight: 600; font-size: 12px;")
        opt2_desc = QLabel("Os dependentes permanecerão ativos com novos valores.")
        opt2_desc.setStyleSheet("color: #888888; font-size: 11px;")

        btn_opt2 = QPushButton("Ajustar Valores")
        btn_opt2.setStyleSheet(self._btn_style_primary())
        btn_opt2.clicked.connect(self.escolher_ajustar)

        opt2_box = QHBoxLayout()
        opt2_text = QVBoxLayout()
        opt2_text.addWidget(opt2_label)
        opt2_text.addWidget(opt2_desc)
        opt2_box.addLayout(opt2_text)
        opt2_box.addStretch()
        opt2_box.addWidget(btn_opt2)
        action_layout.addLayout(opt2_box)

        main.addWidget(action_frame)

        # Botões de ação
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(36)
        btn_cancelar.setStyleSheet(self._btn_style_secondary())
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        main.addLayout(btn_layout)

    def escolher_inativar(self):
        self.escolha = "inativar"
        self.accept()

    def escolher_ajustar(self):
        self.escolha = "ajustar"
        self.open_ajuste_dialog()

    def open_ajuste_dialog(self):
        """Abre diálogo para ajustar valores dos dependentes."""
        dlg = AjustarValoresDependentesDialog(self, self.dependentes)
        if dlg.exec() == QDialog.Accepted:
            self.valores_ajustados = dlg.valores_ajustados
            self.accept()

    @staticmethod
    def _btn_style_primary():
        return """
            QPushButton {
                background: #cc1e1e; color: #ffffff;
                border: none; border-radius: 6px;
                font-size: 12px; font-weight: 600;
                padding: 6px 16px; min-width: 100px;
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
                padding: 6px 16px; min-width: 100px;
            }
            QPushButton:hover { background: #252525; color: #cccccc; }
        """

    @staticmethod
    def _btn_style_danger():
        return """
            QPushButton {
                background: #8b0000; color: #ffffff;
                border: none; border-radius: 6px;
                font-size: 12px; font-weight: 600;
                padding: 6px 16px; min-width: 100px;
            }
            QPushButton:hover { background: #a01515; }
        """


class AjustarValoresDependentesDialog(QDialog):
    """Diálogo para ajustar valores de mensalidades dos dependentes."""

    def __init__(self, parent, dependentes):
        super().__init__(parent)
        self.dependentes = dependentes
        self.valores_ajustados = {}

        self.setWindowTitle("Ajustar Valores dos Dependentes")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(400)
        self.setStyleSheet("background: #111111;")
        self.build_ui()

    def build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        title = QLabel("Ajustar Valores de Mensalidades")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #ffffff;")
        main.addWidget(title)

        desc = QLabel(
            "Defina o novo valor de mensalidade para cada dependente.\n"
            "Os dependentes permanecerão ATIVOS após inativar o responsável."
        )
        desc.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        main.addWidget(desc)

        # Tabela com dependentes
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["Nome", "Tipo", "Plano Atual", "Novo Valor (R$)"])
        self.tabela.setStyleSheet(self._table_style())

        row = 0
        for dep_id, dep_nome, dep_plano in self.dependentes.get("adultos", []):
            self._add_row(row, dep_id, dep_nome, "Adulto", dep_plano or "—", "adulto")
            row += 1

        for dep_id, dep_nome, dep_plano in self.dependentes.get("kids", []):
            self._add_row(row, dep_id, dep_nome, "Kid", dep_plano or "—", "kid")
            row += 1

        self.tabela.setRowCount(row)
        self.tabela.resizeColumnsToContents()
        main.addWidget(self.tabela)

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(36)
        btn_cancelar.setStyleSheet(self._btn_style_secondary())
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        btn_confirmar = QPushButton("Aplicar Mudanças")
        btn_confirmar.setFixedHeight(36)
        btn_confirmar.setStyleSheet(self._btn_style_primary())
        btn_confirmar.clicked.connect(self.confirmar)
        btn_layout.addWidget(btn_confirmar)

        main.addLayout(btn_layout)

    def _add_row(self, row, dep_id, nome, tipo, plano, dep_tipo):
        self.tabela.insertRow(row)

        # Nome
        item_nome = QTableWidgetItem(nome)
        item_nome.setStyleSheet("color: #ffffff;")
        self.tabela.setItem(row, 0, item_nome)

        # Tipo
        item_tipo = QTableWidgetItem(tipo)
        item_tipo.setStyleSheet("color: #aaaaaa;")
        self.tabela.setItem(row, 1, item_tipo)

        # Plano atual
        item_plano = QTableWidgetItem(plano)
        item_plano.setStyleSheet("color: #888888;")
        self.tabela.setItem(row, 2, item_plano)

        # Campo de entrada para novo valor
        spin = QDoubleSpinBox()
        spin.setMinimum(0.0)
        spin.setMaximum(9999.99)
        spin.setDecimals(2)
        spin.setValue(0.0)
        spin.setStyleSheet("""
            QDoubleSpinBox {
                background: #0e0e0e; color: #ffffff;
                border: 1px solid #1e1e1e; border-radius: 6px;
                padding: 6px 8px; font-size: 12px;
            }
            QDoubleSpinBox:focus { border: 1.5px solid #cc1e1e; }
        """)
        spin.setProperty("dep_id", dep_id)
        spin.setProperty("dep_tipo", dep_tipo)
        self.tabela.setCellWidget(row, 3, spin)

    def confirmar(self):
        """Coleta os valores ajustados e fecha o diálogo."""
        self.valores_ajustados = {}
        for row in range(self.tabela.rowCount()):
            spin = self.tabela.cellWidget(row, 3)
            if spin:
                dep_id = spin.property("dep_id")
                dep_tipo = spin.property("dep_tipo")
                valor = spin.value()
                if valor > 0:
                    self.valores_ajustados[f"{dep_tipo}_{dep_id}"] = valor

        self.accept()

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

    @staticmethod
    def _btn_style_primary():
        return """
            QPushButton {
                background: #cc1e1e; color: #ffffff;
                border: none; border-radius: 6px;
                font-size: 12px; font-weight: 600;
                padding: 6px 16px; min-width: 100px;
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
                padding: 6px 16px; min-width: 100px;
            }
            QPushButton:hover { background: #252525; color: #cccccc; }
        """
