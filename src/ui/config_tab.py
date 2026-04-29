import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame,
    QLineEdit, QFormLayout, QDialog, QScrollArea
)
from PySide6.QtCore import Qt
from .base_tab import BaseTab, SCROLLBAR_STYLE
from .change_password_dialog import ChangePasswordDialog
from .app_dialog import show_info, show_error, show_question
from database.db import listar_planos, criar_plano, atualizar_plano, excluir_plano, plano_existe


class ConfigTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.build_ui()

    def build_ui(self):
        layout = self.layout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

        # ── TÍTULO ──
        title = QLabel("Configurações")
        title.setStyleSheet(
            "color:#ffffff; font-size:22px; font-weight:700;"
            " font-family:'Arial Black',sans-serif; background:transparent; border:none;"
        )
        layout.addWidget(title)

        # Wrapper centralizado
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setMaximumWidth(640)
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(16)

        # ── SEÇÃO SEGURANÇA ──
        sec_seg = QFrame()
        sec_seg.setObjectName("secCard")
        sec_seg.setStyleSheet(
            "#secCard { background: #161616; border: 1px solid #1e1e1e; border-radius: 10px; }"
        )
        sec_seg_layout = QVBoxLayout(sec_seg)
        sec_seg_layout.setContentsMargins(20, 16, 20, 16)
        sec_seg_layout.setSpacing(10)

        lbl_sec = QLabel("Segurança")
        lbl_sec.setStyleSheet(
            "color:#ffffff; font-size:14px; font-weight:600; background:transparent; border:none;"
        )
        sec_seg_layout.addWidget(lbl_sec)

        sep = QFrame()
        sep.setObjectName("sepLine")
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("#sepLine { background: #1e1e1e; border: none; max-height: 1px; }")
        sec_seg_layout.addWidget(sep)

        row_senha = QHBoxLayout()
        lbl_senha_desc = QLabel("Altere a senha de acesso ao sistema")
        lbl_senha_desc.setStyleSheet(
            "color:#555555; font-size:12px; background:transparent; border:none;"
        )
        row_senha.addWidget(lbl_senha_desc)
        row_senha.addStretch()

        btn_trocar_senha = QPushButton("Trocar Senha")
        btn_trocar_senha.setFixedHeight(34)
        btn_trocar_senha.setCursor(Qt.PointingHandCursor)
        btn_trocar_senha.setStyleSheet("""
            QPushButton {
                background: #cc1e1e; color: #ffffff; border: none;
                border-radius: 7px; font-size: 12px; font-weight: 600; padding: 0 16px;
            }
            QPushButton:hover  { background: #e02020; }
            QPushButton:pressed{ background: #a01515; }
        """)
        btn_trocar_senha.clicked.connect(self.trocar_senha)
        row_senha.addWidget(btn_trocar_senha)
        sec_seg_layout.addLayout(row_senha)

        container_layout.addWidget(sec_seg)

        # ── SEÇÃO PLANOS ──
        sec_planos = QFrame()
        sec_planos.setObjectName("secCardPlanos")
        sec_planos.setStyleSheet(
            "#secCardPlanos { background: #161616; border: 1px solid #1e1e1e; border-radius: 10px; }"
        )
        sec_planos_layout = QVBoxLayout(sec_planos)
        sec_planos_layout.setContentsMargins(20, 16, 20, 16)
        sec_planos_layout.setSpacing(12)

        row_planos_header = QHBoxLayout()
        lbl_planos = QLabel("Planos")
        lbl_planos.setStyleSheet(
            "color:#ffffff; font-size:14px; font-weight:600; background:transparent; border:none;"
        )
        row_planos_header.addWidget(lbl_planos)
        row_planos_header.addStretch()

        btn_novo_plano = QPushButton("+ Novo Plano")
        btn_novo_plano.setFixedHeight(34)
        btn_novo_plano.setCursor(Qt.PointingHandCursor)
        btn_novo_plano.setStyleSheet("""
            QPushButton {
                background: #cc1e1e; color: #ffffff; border: none;
                border-radius: 7px; font-size: 12px; font-weight: 600; padding: 0 16px;
            }
            QPushButton:hover  { background: #e02020; }
            QPushButton:pressed{ background: #a01515; }
        """)
        btn_novo_plano.clicked.connect(self.novo_plano)
        row_planos_header.addWidget(btn_novo_plano)
        sec_planos_layout.addLayout(row_planos_header)

        sep2 = QFrame()
        sep2.setObjectName("sepLine2")
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("#sepLine2 { background: #1e1e1e; border: none; max-height: 1px; }")
        sec_planos_layout.addWidget(sep2)

        lbl_planos_desc = QLabel("Gerencie os planos disponíveis para cadastro de alunos")
        lbl_planos_desc.setStyleSheet(
            "color:#555555; font-size:11px; background:transparent; border:none;"
        )
        sec_planos_layout.addWidget(lbl_planos_desc)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(320)
        scroll_area.setStyleSheet(
            f"QScrollArea {{ border: none; background: transparent; }} {SCROLLBAR_STYLE}"
        )

        self.cards_widget = QWidget()
        self.cards_widget.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.cards_layout.setSpacing(8)
        self.cards_layout.setAlignment(Qt.AlignTop)
        scroll_area.setWidget(self.cards_widget)
        sec_planos_layout.addWidget(scroll_area)

        container_layout.addWidget(sec_planos)
        container_layout.addStretch()

        wrapper_layout.addStretch()
        wrapper_layout.addWidget(container)
        wrapper_layout.addStretch()
        layout.addWidget(wrapper)

        self.carregar_planos()

    def trocar_senha(self):
        dialog = ChangePasswordDialog("admin")
        dialog.exec()

    def notificar_atualizacao_planos(self):
        try:
            parent = self.parent()
            while parent and not hasattr(parent, 'cadastro_tab'):
                parent = parent.parent()
            if parent and hasattr(parent, 'cadastro_tab'):
                if hasattr(parent.cadastro_tab, 'carregar_planos'):
                    parent.cadastro_tab.carregar_planos()
        except Exception as e:
            print(f"Erro ao notificar atualização de planos: {e}")

    def carregar_planos(self):
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        try:
            planos = listar_planos()
            if not planos:
                sem_planos = QLabel("Nenhum plano cadastrado")
                sem_planos.setObjectName("emptyLabel")
                sem_planos.setStyleSheet(
                    "#emptyLabel { color:#333333; font-size:13px; background:transparent; border:none; }"
                )
                sem_planos.setAlignment(Qt.AlignCenter)
                self.cards_layout.addWidget(sem_planos)
                return
            for plano_id, nome, valor in planos:
                card = PlanoCard(plano_id, nome, valor)
                card.set_editar_callback(self.editar_plano_card)
                card.set_excluir_callback(self.excluir_plano_card)
                self.cards_layout.addWidget(card)
        except Exception as e:
            show_error(self, "Erro ao carregar planos", f"Erro: {str(e)}")

    def novo_plano(self):
        dialog = PlanoDialog(self, "Novo Plano")
        if dialog.exec() == QDialog.Accepted:
            self.carregar_planos()
            self.notificar_atualizacao_planos()

    def editar_plano_card(self, plano_id, nome, valor):
        dialog = PlanoDialog(self, "Editar Plano", plano_id, nome, valor)
        if dialog.exec() == QDialog.Accepted:
            self.carregar_planos()
            self.notificar_atualizacao_planos()

    def excluir_plano_card(self, plano_id, nome):
        if show_question(self, "Confirmar Exclusão", f"Deseja realmente excluir o plano '{nome}'?"):
            try:
                excluir_plano(plano_id)
                show_info(self, "Sucesso", "Plano excluído com sucesso!")
                self.carregar_planos()
                self.notificar_atualizacao_planos()
            except Exception as e:
                show_error(self, "Erro ao excluir plano", f"Erro: {str(e)}")


class PlanoCard(QFrame):
    def __init__(self, plano_id, nome, valor):
        super().__init__()
        self.plano_id = plano_id
        self.nome = nome
        self.valor = valor
        self.editar_clicked = None
        self.excluir_clicked = None
        self.build_ui()

    def build_ui(self):
        self.setObjectName("planoCard")
        self.setStyleSheet(
            "QFrame#planoCard { background: #111111; border: 1px solid #1e1e1e; border-radius: 8px; }"
            "QFrame#planoCard:hover { border: 1px solid #2a2a2a; }"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        # Info
        info = QVBoxLayout()
        info.setSpacing(3)

        lbl_nome = QLabel(self.nome)
        lbl_nome.setStyleSheet(
            "color:#cccccc; font-size:13px; font-weight:500; background:transparent; border:none;"
        )
        lbl_nome.setWordWrap(True)
        info.addWidget(lbl_nome)

        if self.valor == 0:
            valor_text = "Gratuito"
            valor_color = "#2d8a52"
        else:
            valor_text = f"R$ {self.valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            valor_color = "#cc1e1e"

        lbl_valor = QLabel(valor_text)
        lbl_valor.setStyleSheet(
            f"color:{valor_color}; font-size:12px; font-weight:600; background:transparent; border:none;"
        )
        info.addWidget(lbl_valor)
        layout.addLayout(info, 1)

        # Botões
        btn_editar = QPushButton("Editar")
        btn_editar.setFixedHeight(28)
        btn_editar.setCursor(Qt.PointingHandCursor)
        btn_editar.setStyleSheet("""
            QPushButton {
                background: #1e1e1e; color: #888888;
                border: 1px solid #2a2a2a; border-radius: 5px;
                font-size: 11px; font-weight: 500; padding: 0 12px;
            }
            QPushButton:hover { background: #252525; color: #cccccc; }
        """)
        btn_editar.clicked.connect(self.editar)

        btn_excluir = QPushButton("Excluir")
        btn_excluir.setFixedHeight(28)
        btn_excluir.setCursor(Qt.PointingHandCursor)
        btn_excluir.setStyleSheet("""
            QPushButton {
                background: rgba(204,30,30,0.08); color: #c04444;
                border: 1px solid rgba(204,30,30,0.2); border-radius: 5px;
                font-size: 11px; font-weight: 500; padding: 0 12px;
            }
            QPushButton:hover { background: rgba(204,30,30,0.15); color: #e05050; }
        """)
        btn_excluir.clicked.connect(self.excluir)

        layout.addWidget(btn_editar)
        layout.addWidget(btn_excluir)

    def editar(self):
        if self.editar_clicked:
            self.editar_clicked(self.plano_id, self.nome, self.valor)

    def excluir(self):
        if self.excluir_clicked:
            self.excluir_clicked(self.plano_id, self.nome)

    def set_editar_callback(self, callback):
        self.editar_clicked = callback

    def set_excluir_callback(self, callback):
        self.excluir_clicked = callback


class PlanoDialog(QDialog):
    def __init__(self, parent, titulo, plano_id=None, nome="", valor=0.0):
        super().__init__(parent)
        self.plano_id = plano_id
        self.nome_inicial = nome
        self.valor_inicial = valor
        self.setWindowTitle(titulo)
        self.setFixedSize(480, 340)
        self.setModal(True)
        self.setObjectName("planoDialog")
        self.setStyleSheet("#planoDialog { background: #111111; }")
        self.build_ui()

    def build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        card = QFrame()
        card.setObjectName("planoDialogCard")
        card.setStyleSheet(
            "#planoDialogCard { background: #161616; border-radius: 10px; border: 1px solid #222222; }"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(14)

        lbl_title = QLabel("Editar Plano" if self.plano_id else "Novo Plano")
        lbl_title.setStyleSheet(
            "color:#ffffff; font-size:15px; font-weight:700; background:transparent; border:none;"
        )
        card_layout.addWidget(lbl_title)

        _label_style = "color:#888888; font-size:12px; font-weight:500; background:transparent; border:none;"
        _field_style = """
            QLineEdit {
                background-color: #0e0e0e; padding: 8px 10px;
                border-radius: 8px; border: 1px solid #1e1e1e;
                font-size: 13px; color: #cccccc;
            }
            QLineEdit:focus { border: 1.5px solid #cc1e1e; }
        """

        form_widget = QWidget()
        form_widget.setStyleSheet("background: transparent;")
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(12)

        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Ex: Família Premium")
        self.nome_input.setText(self.nome_inicial)
        self.nome_input.setStyleSheet(_field_style)
        lbl_nome = QLabel("Nome do Plano:")
        lbl_nome.setStyleSheet(_label_style)
        form_layout.addRow(lbl_nome, self.nome_input)

        self.valor_input = QLineEdit()
        self.valor_input.setPlaceholderText("Ex: 250.00")
        if self.valor_inicial > 0:
            self.valor_input.setText(str(self.valor_inicial))
        self.valor_input.setStyleSheet(_field_style)
        lbl_valor = QLabel("Valor (R$):")
        lbl_valor.setStyleSheet(_label_style)
        form_layout.addRow(lbl_valor, self.valor_input)

        lbl_dica = QLabel("Digite 0 para plano gratuito")
        lbl_dica.setStyleSheet(
            "color:#333333; font-size:11px; font-style:italic; background:transparent; border:none;"
        )
        form_layout.addRow("", lbl_dica)

        card_layout.addWidget(form_widget)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.setAlignment(Qt.AlignCenter)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(38)
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background: #1e1e1e; color: #888888;
                border: 1px solid #2a2a2a; border-radius: 7px;
                font-size: 13px; font-weight: 500; padding: 0 20px;
            }
            QPushButton:hover { background: #252525; color: #cccccc; }
        """)
        btn_cancelar.clicked.connect(self.reject)

        btn_salvar = QPushButton("Salvar Alterações" if self.plano_id else "Criar Plano")
        btn_salvar.setFixedHeight(38)
        btn_salvar.setCursor(Qt.PointingHandCursor)
        btn_salvar.setStyleSheet("""
            QPushButton {
                background: #cc1e1e; color: #ffffff; border: none;
                border-radius: 7px; font-size: 13px; font-weight: 600; padding: 0 20px;
            }
            QPushButton:hover  { background: #e02020; }
            QPushButton:pressed{ background: #a01515; }
        """)
        btn_salvar.clicked.connect(self.salvar)

        btn_row.addWidget(btn_cancelar)
        btn_row.addWidget(btn_salvar)
        card_layout.addLayout(btn_row)

        main.addWidget(card)

    def salvar(self):
        nome = self.nome_input.text().strip()
        valor_texto = self.valor_input.text().strip()

        if not nome:
            show_error(self, "Erro", "Nome do plano é obrigatório")
            return

        try:
            valor = float(valor_texto) if valor_texto else 0.0
            if valor < 0:
                show_error(self, "Erro", "Valor não pode ser negativo")
                return
        except ValueError:
            show_error(self, "Erro", "Valor inválido. Use apenas números (ex: 150.00)")
            return

        if plano_existe(nome, self.plano_id):
            show_error(self, "Erro", "Já existe um plano com este nome")
            return

        try:
            if self.plano_id:
                atualizar_plano(self.plano_id, nome, valor)
                show_info(self, "Sucesso", "Plano atualizado com sucesso!")
            else:
                criar_plano(nome, valor)
                show_info(self, "Sucesso", "Plano criado com sucesso!")
            self.accept()
        except Exception as e:
            show_error(self, "Erro ao salvar plano", f"Erro: {str(e)}")
