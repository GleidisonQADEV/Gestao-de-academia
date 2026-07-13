import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QDialog, QScrollArea, QSizePolicy,
    QDateEdit, QComboBox, QFileDialog, QFormLayout, QCheckBox,
    QTextEdit, QTabWidget, QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap, QPalette, QBrush

from ui.base_tab import BaseTab
from database.db import listar_alunos, inativar_aluno, excluir_aluno, listar_todos_alunos, atualizar_aluno, cpf_existe, email_existe, obter_status_pagamento_mes, atualizar_mensalidades_por_plano, definir_plano_aluno, gerar_mensalidades_anuais, get_planos_formatados, obter_dependentes, reatribuir_dependentes, desvincular_dependentes, inativar_dependentes, atualizar_valor_dependente
from database.kids_db import get_conn, atualizar_kid, cpf_kid_existe, excluir_kid
from ui.app_dialog import show_info, show_warning, show_error, show_question, show_custom, show_input, show_combo

# ================= ESTILOS CSS =================
campo_nome_style = """
QLabel {
    background: #1e1e1e;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 14px;
    font-weight: bold;
    color: #ffffff;
    border: 1px solid #2a2a2a;
}
"""

campo_style = """
QLabel {
    background: #181818;
    border-radius: 5px;
    padding: 6px 10px;
    font-size: 11px;
    color: #aaaaaa;
    border: 1px solid #222222;
    margin: 1px;
}
"""

# ================= CORES DAS FAIXAS =================
_BELT_COLORS_MAP = {
    "Branca": "#d0d0d0", "Cinza": "#8a8a8a", "Amarela": "#f2c200",
    "Laranja": "#e67e22", "Verde": "#2e9e4f",
    "Azul": "#1a4fa0", "Roxa": "#6b2fa0", "Marrom": "#8b4a1f", "Preta": "#111111",
}


def cor_faixa(faixa):
    """Cor da faixa cobrindo variantes Kids (ex.: 'Amarela c/b')."""
    if not faixa:
        return "#888888"
    if faixa in _BELT_COLORS_MAP:
        return _BELT_COLORS_MAP[faixa]
    fl = faixa.lower()
    for base, col in _BELT_COLORS_MAP.items():
        if base.lower() in fl:
            return col
    return "#888888"


# ================= CARD CRACHÁ =================
class AlunoCard(QFrame):
    def __init__(self):
        super().__init__()
        self.dados = None
        self.build_ui()

    def build_ui(self):
        self.setFixedSize(480, 320)
        self.setStyleSheet("""
            QFrame {
                background: #161616;
                border-radius: 8px;
                border: 1px solid #222222;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 15)  # Margens aumentadas
        layout.setSpacing(12)  # Espaçamento aumentado

        # HEADER com foto e nome
        header = QHBoxLayout()
        header.setSpacing(12)
        
        # FOTO menor
        self.foto = QLabel()
        self.foto.setFixedSize(80, 80)
        self.foto.setStyleSheet("""
            QLabel {
                background: #1e1e1e;
                border-radius: 6px;
                border: 1px solid #2a2a2a;
            }
        """)
        self.foto.setAlignment(Qt.AlignCenter)
        self.foto.setScaledContents(True)
        header.addWidget(self.foto)
        
        # Nome e status
        nome_status = QVBoxLayout()
        
        self.lbl_nome = QLabel("")
        self.lbl_nome.setStyleSheet(campo_nome_style)
        self.lbl_nome.setWordWrap(True)
        
        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setFixedHeight(24)
        self.status.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 10px;
                border-radius: 6px;
                padding: 2px 6px;
                background: rgba(26,122,60,0.15);
                color: #4caf50;
                border: 1px solid rgba(26,122,60,0.3);
            }
        """)
        
        nome_status.addWidget(self.lbl_nome)
        nome_status.addWidget(self.status)
        nome_status.addStretch()
        
        header.addLayout(nome_status, 1)
        layout.addLayout(header)

        # DADOS em grid 2x4
        dados_grid = QHBoxLayout()
        dados_grid.setSpacing(8)
        
        # Coluna 1
        col1 = QVBoxLayout()
        col1.setSpacing(8)  # Espaçamento aumentado para melhor distribuição
        
        self.lbl_cpf = QLabel("")
        self.lbl_cpf.setStyleSheet(campo_style)
        
        self.lbl_email = QLabel("")
        self.lbl_email.setStyleSheet(campo_style)
        self.lbl_email.setWordWrap(True)
        
        self.lbl_telefone = QLabel("")
        self.lbl_telefone.setStyleSheet(campo_style)
        
        self.lbl_faixa = QLabel("")
        self.lbl_faixa.setStyleSheet(campo_style)
        
        self.lbl_belt_color = QLabel()
        self.lbl_belt_color.setFixedSize(26, 6)
        self.lbl_belt_color.setStyleSheet("background: #d0d0d0; border-radius: 2px;")

        col1.addWidget(self.lbl_cpf)
        col1.addWidget(self.lbl_email)
        col1.addWidget(self.lbl_telefone)
        col1.addWidget(self.lbl_faixa)
        col1.addWidget(self.lbl_belt_color)
        
        # Coluna 2
        col2 = QVBoxLayout()
        col2.setSpacing(8)  # Espaçamento aumentado para melhor distribuição
        
        self.lbl_endereco = QLabel("")
        self.lbl_endereco.setStyleSheet(campo_style)
        self.lbl_endereco.setWordWrap(True)
        
        self.lbl_nascimento = QLabel("")
        self.lbl_nascimento.setStyleSheet(campo_style)
        
        self.lbl_plano = QLabel("")
        self.lbl_plano.setStyleSheet(campo_style)
        
        self.lbl_resp = QLabel("")
        self.lbl_resp.setStyleSheet(campo_style)
        self.lbl_resp.setWordWrap(True)
        
        self.lbl_dependentes = QLabel("")
        self.lbl_dependentes.setStyleSheet(campo_style)
        self.lbl_dependentes.setWordWrap(True)
        
        col2.addWidget(self.lbl_endereco)
        col2.addWidget(self.lbl_nascimento)
        col2.addWidget(self.lbl_plano)
        col2.addWidget(self.lbl_resp)
        col2.addWidget(self.lbl_dependentes)
        
        dados_grid.addLayout(col1, 1)
        dados_grid.addLayout(col2, 1)
        
        layout.addLayout(dados_grid)
        layout.addStretch()

    # -------- preencher dados --------

    def set_dados(self, dados):
        self.dados = dados

        self.lbl_nome.setText(dados["nome"])
        self.lbl_cpf.setText(f"CPF: {dados.get('cpf','N/A')}")
        
        # Email mais conciso
        email = dados.get('email', '')
        self.lbl_email.setText(f"📧 {email}" if email else "📧 Não informado")
        
        # Telefone
        telefone = dados.get('telefone', '')
        self.lbl_telefone.setText(f"📞 {telefone}" if telefone else "📞 Não informado")
        
        # Endereço mais compacto
        endereco = dados.get('endereco', '')
        cep = dados.get('cep', '')
        if endereco:
            endereco_text = f"🏠 {endereco[:30]}{'...' if len(endereco) > 30 else ''}"
            if cep:
                endereco_text += f" - {cep}"
            self.lbl_endereco.setText(endereco_text)
        else:
            self.lbl_endereco.setText("🏠 Não informado")
        
        # Data de nascimento com idade
        nascimento = dados.get('data_nascimento', '')
        if nascimento:
            from datetime import datetime
            try:
                dt = datetime.strptime(nascimento, '%Y-%m-%d')
                nascimento_fmt = dt.strftime('%d/%m/%Y')
                hoje = datetime.now()
                idade = hoje.year - dt.year - ((hoje.month, hoje.day) < (dt.month, dt.day))
                self.lbl_nascimento.setText(f"🎂 {nascimento_fmt} ({idade} anos)")
            except:
                self.lbl_nascimento.setText(f"🎂 {nascimento}")
        else:
            self.lbl_nascimento.setText("🎂 Não informado")
            
        # Faixa com informações extras
        faixa_info = f"🥋 {dados['faixa']} - {dados['grau']}"
        peso = dados.get('peso', '')
        altura = dados.get('altura', '')
        if peso or altura:
            extras = []
            if peso: extras.append(f"{peso}kg")
            if altura: extras.append(f"{altura}cm")
            faixa_info += f" ({'/'.join(extras)})"
        self.lbl_faixa.setText(faixa_info)
        faixa_key = dados.get('faixa', 'Branca')
        belt_color = cor_faixa(faixa_key)
        needs_border = faixa_key == "Preta"
        border_str = "border: 1px solid #555555;" if needs_border else ""
        self.lbl_belt_color.setStyleSheet(
            f"background: {belt_color}; border-radius: 2px; {border_str}"
        )

        self.lbl_plano.setText(f"💳 {dados['plano']}")

        # Responsável (para alunos que são dependentes)
        if dados.get("responsavel_nome"):
            resp_info = f"👨‍👩‍👧‍👦 Resp: {dados['responsavel_nome']}"
            if dados.get("responsavel_cpf"):
                resp_info += f" ({dados['responsavel_cpf']})"
            self.lbl_resp.setText(resp_info)
            self.lbl_resp.show()
        elif dados.get("responsavel"):  # Para compatibilidade com kids
            resp_info = f"👨‍👩‍👧‍👦 {dados['responsavel']}"
            if dados.get("responsavel_cpf"):
                resp_info += f" - {dados['responsavel_cpf']}"
            self.lbl_resp.setText(resp_info)
            self.lbl_resp.show()
        else:
            self.lbl_resp.hide()
            
        # Dependentes (para alunos que são responsáveis)
        if dados.get("dependentes_nomes") and dados.get("total_dependentes", 0) > 0:
            dep_info = f"👥 Dependentes ({dados['total_dependentes']}): {dados['dependentes_nomes']}"
            self.lbl_dependentes.setText(dep_info)
            self.lbl_dependentes.show()
        else:
            self.lbl_dependentes.hide()

        # Status
        if dados["status"]:
            self.status.setText("ATIVO")
            self.status.setStyleSheet("""
                QLabel {
                    background: rgba(26,122,60,0.15);
                    color: #4caf50;
                    border: 1px solid rgba(26,122,60,0.3);
                    border-radius: 6px; padding: 2px 6px;
                    font-weight: bold; font-size: 10px;
                }
            """)
        else:
            self.status.setText("INATIVO")
            self.status.setStyleSheet("""
                QLabel {
                    background: rgba(204,30,30,0.12);
                    color: #cc6666;
                    border: 1px solid rgba(204,30,30,0.25);
                    border-radius: 6px; padding: 2px 6px;
                    font-weight: bold; font-size: 10px;
                }
            """)

        # Foto com melhor enquadramento
        if dados.get("foto"):
            pix = QPixmap(dados["foto"])
            if not pix.isNull():
                # Escalar mantendo proporção e centralizando
                self.foto.setPixmap(pix.scaled(
                    130, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))
            else:
                self.foto.clear()
                initials = ''.join(w[0].upper() for w in dados.get('nome','?').split()[:2]) if dados.get('nome') else '?'
                self.foto.setText(initials)
                self.foto.setAlignment(Qt.AlignCenter)
                self.foto.setStyleSheet(
                    "background: #1a1a1a; border: 1px solid #252525; border-radius: 14px;"
                    " color: #a0a0a0; font-size: 9px; font-weight: 600;"
                )
        else:
            self.foto.clear()
            initials = ''.join(w[0].upper() for w in dados.get('nome','?').split()[:2]) if dados.get('nome') else '?'
            self.foto.setText(initials)
            self.foto.setAlignment(Qt.AlignCenter)
            self.foto.setStyleSheet(
                "background: #1a1a1a; border: 1px solid #252525; border-radius: 14px;"
                " color: #a0a0a0; font-size: 9px; font-weight: 600;"
            )
            
        # Aviso de vínculo para dependentes
        self.mostrar_vinculo_dependentes(dados)
            
    def mostrar_vinculo_dependentes(self, dados):
        """Adiciona aviso de vínculo se for dependente com outros dependentes"""
        # Remover aviso anterior se existir
        if hasattr(self, 'vinculo_widget'):
            self.vinculo_widget.setParent(None)
            delattr(self, 'vinculo_widget')
            
        if dados["tipo"] == "kids" and dados.get("responsavel_cpf"):
            # Criar widget de vínculo mais compacto
            self.vinculo_widget = QLabel()
            self.vinculo_widget.setText("🔗 Vinculado - Clique para navegar")
            self.vinculo_widget.setStyleSheet("""
                QLabel {
                    background-color: rgba(229, 9, 20, 0.1);
                    color: #cc1e1e;
                    border: 1px dashed #cc1e1e;
                    border-radius: 6px;
                    padding: 2px 6px;
                    font-size: 9px;
                    margin: 1px 0px;
                    max-height: 16px;
                    font-weight: bold;
                }
            """)
            self.vinculo_widget.hide()  # Inicialmente oculto
            
            # Adicionar ao layout de forma que não interfira com outros elementos
            layout = self.layout()
            # Inserir após o header mas antes dos dados
            layout.insertWidget(2, self.vinculo_widget)


# ================= TAB =================
class AlunosTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.registros = []
        self.aluno_atual = None
        self.nav_cadastro = None
        self.build_ui()
        self.carregar_dados()

    # ---------------- UI ----------------

    def build_ui(self):
        root = self.layout()
        self.content_layout.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(8)

        # ── TITLE ROW ──
        top_row = QHBoxLayout()
        titulo = QLabel("Alunos")
        titulo.setStyleSheet(
            "color:#ffffff; font-size:22px; font-weight:700;"
            " font-family:'Arial Black',sans-serif; background:transparent;"
        )
        top_row.addWidget(titulo)
        top_row.addStretch()

        btn_export = QPushButton("Exportar PDF")
        btn_export.setFixedHeight(34)
        btn_export.setCursor(Qt.PointingHandCursor)
        btn_export.setStyleSheet("""
            QPushButton {
                background: #1e1e1e; color: #cccccc;
                font-size: 12px; font-weight: 600;
                border: 1px solid #2a2a2a; border-radius: 7px; padding: 0 16px;
            }
            QPushButton:hover { background: #252525; color: #ffffff; }
        """)
        btn_export.clicked.connect(self.exportar_lista_pdf)
        top_row.addWidget(btn_export)

        btn_excluir_lote = QPushButton("Excluir selecionados")
        btn_excluir_lote.setFixedHeight(34)
        btn_excluir_lote.setCursor(Qt.PointingHandCursor)
        btn_excluir_lote.setStyleSheet("""
            QPushButton {
                background: #2a1414; color: #e06666;
                font-size: 12px; font-weight: 600;
                border: 1px solid #5a1a1a; border-radius: 7px; padding: 0 16px;
            }
            QPushButton:hover { background: #3a1a1a; color: #ff8080; }
        """)
        btn_excluir_lote.clicked.connect(self.excluir_selecionados)
        top_row.addWidget(btn_excluir_lote)

        btn_plano_lote = QPushButton("Definir plano")
        btn_plano_lote.setFixedHeight(34)
        btn_plano_lote.setCursor(Qt.PointingHandCursor)
        btn_plano_lote.setStyleSheet("""
            QPushButton {
                background: #1e1e1e; color: #cccccc;
                font-size: 12px; font-weight: 600;
                border: 1px solid #2a2a2a; border-radius: 7px; padding: 0 16px;
            }
            QPushButton:hover { background: #252525; color: #ffffff; }
        """)
        btn_plano_lote.clicked.connect(self.definir_plano_selecionados)
        top_row.addWidget(btn_plano_lote)

        btn_novo = QPushButton("+ Novo Aluno")
        btn_novo.setFixedHeight(34)
        btn_novo.setStyleSheet("""
            QPushButton {
                background: #cc1e1e; color: #ffffff;
                font-size: 12px; font-weight: 600;
                border: none; border-radius: 7px; padding: 0 16px;
            }
            QPushButton:hover  { background: #e02020; }
            QPushButton:pressed{ background: #a01515; }
        """)
        btn_novo.clicked.connect(lambda: self.nav_cadastro() if self.nav_cadastro else None)
        top_row.addWidget(btn_novo)
        root.addLayout(top_row)

        # ── SEARCH ROW ──
        search_row = QHBoxLayout()
        search_row.setSpacing(7)

        self.busca = QLineEdit()
        self.busca.setPlaceholderText("Buscar por nome, CPF...")
        self.busca.setFixedHeight(32)
        self.busca.setStyleSheet("""
            QLineEdit {
                background: #161616; border: 1px solid #1e1e1e;
                border-radius: 7px; padding: 0 10px;
                font-size: 11px; color: #888888;
            }
            QLineEdit:focus { border-color: #cc1e1e; }
        """)
        self.busca.returnPressed.connect(self.buscar)
        self.busca.textChanged.connect(self._on_search_changed)
        search_row.addWidget(self.busca, 1)

        self.combo_faixa = QComboBox()
        self.combo_faixa.addItems(["Todas as faixas", "Branca", "Azul", "Roxa", "Marrom", "Preta"])
        self.combo_faixa.setFixedHeight(32)
        self.combo_faixa.setStyleSheet("""
            QComboBox {
                background: #161616; border: 1px solid #1e1e1e;
                border-radius: 7px; color: #a0a0a0;
                font-size: 11px; padding: 0 8px;
            }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox QAbstractItemView {
                background: #161616; border: 1px solid #1e1e1e;
                color: #888888; selection-background-color: #cc1e1e;
            }
        """)
        self.combo_faixa.currentIndexChanged.connect(self._on_filter_changed)
        search_row.addWidget(self.combo_faixa)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Todos", "Adulto", "Dependente", "Kids"])
        self.combo_tipo.setFixedHeight(32)
        self.combo_tipo.setStyleSheet("""
            QComboBox {
                background: #161616; border: 1px solid #1e1e1e;
                border-radius: 7px; color: #a0a0a0;
                font-size: 11px; padding: 0 8px;
            }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox QAbstractItemView {
                background: #161616; border: 1px solid #1e1e1e;
                color: #888888; selection-background-color: #cc1e1e;
            }
        """)
        self.combo_tipo.currentIndexChanged.connect(self._on_filter_changed)
        search_row.addWidget(self.combo_tipo)

        root.addLayout(search_row)

        # ── TABLE CONTAINER ──
        table_frame = QFrame()
        table_frame.setObjectName("tableContainer")
        table_frame.setStyleSheet("""
            QFrame#tableContainer {
                background: #161616;
                border: 1px solid #1e1e1e;
                border-radius: 10px;
            }
        """)
        table_vbox = QVBoxLayout(table_frame)
        table_vbox.setContentsMargins(0, 0, 0, 0)
        table_vbox.setSpacing(0)

        # Header row
        header_widget = QWidget()
        header_widget.setObjectName("tableHeader")
        header_widget.setFixedHeight(34)
        header_widget.setStyleSheet(
            "#tableHeader { background: transparent; border-bottom: 1px solid #1a1a1a; }"
        )
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(12, 0, 12, 0)
        header_layout.setSpacing(0)

        _CHK_STYLE = (
            "QCheckBox { background: transparent; }"
            " QCheckBox::indicator { width:15px; height:15px; border:1px solid #444444;"
            " border-radius:3px; background:#0e0e0e; }"
            " QCheckBox::indicator:checked { background:#cc1e1e; border-color:#cc1e1e; }"
        )
        self._chk_style = _CHK_STYLE
        self.chk_todos = QCheckBox()
        self.chk_todos.setFixedWidth(30)
        self.chk_todos.setCursor(Qt.PointingHandCursor)
        self.chk_todos.setStyleSheet(_CHK_STYLE)
        self.chk_todos.setToolTip("Selecionar todos")
        self.chk_todos.stateChanged.connect(self._toggle_selecionar_todos)
        header_layout.addWidget(self.chk_todos)

        _HS = "font-size:9px; color:#8f8f8f; letter-spacing:1px; background:transparent; border:none;"
        lh_nome = QLabel("NOME")
        lh_nome.setStyleSheet(_HS)
        header_layout.addWidget(lh_nome, 1)
        for htext, hw in [("FAIXA", 140), ("PLANO", 140), ("STATUS", 90)]:
            lh = QLabel(htext)
            lh.setFixedWidth(hw)
            lh.setStyleSheet(_HS)
            header_layout.addWidget(lh)
        table_vbox.addWidget(header_widget)

        # Scrollable rows
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                background: #111111; width: 6px; border-radius: 3px; margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #333333; border-radius: 3px; min-height: 20px;
            }
            QScrollBar::handle:vertical:hover { background: #cc1e1e; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0; border: none; background: none;
            }
        """)
        self.cards_area = QWidget()
        self.cards_area.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_area)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(0)
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.cards_area)
        table_vbox.addWidget(self.scroll_area)

        root.addWidget(table_frame, 1)

        # ── ACTION BUTTONS ──
        self.btns = QHBoxLayout()

        self.btn_edit   = self._btn("Editar")
        self.btn_toggle = self._btn("Ativar / Inativar")
        self.btn_del    = self._btn("Excluir")
        self.btn_vincular = self._btn("Vincular")

        self.btn_edit.clicked.connect(self.editar)
        self.btn_toggle.clicked.connect(self.toggle_status)
        self.btn_del.clicked.connect(self.excluir)
        self.btn_vincular.clicked.connect(self.vincular_responsavel)

        self.btn_ficha = self._btn("Ficha PDF")
        self.btn_ficha.clicked.connect(self.exportar_ficha_pdf)

        self.btns.addStretch()
        self.btns.addWidget(self.btn_edit)
        self.btns.addWidget(self.btn_toggle)
        self.btns.addWidget(self.btn_del)
        self.btns.addWidget(self.btn_vincular)
        self.btns.addWidget(self.btn_ficha)
        self.btns.addStretch()
        root.addLayout(self.btns)

        self._toggle_acoes(False)

    def _create_table_row(self, dados):
        row = QFrame()
        row.setObjectName("tableRow")
        row.setStyleSheet("""
            QFrame#tableRow {
                background: transparent;
                border: none;
                border-bottom: 1px solid #181818;
            }
            QFrame#tableRow:hover { background: #1a1a1a; }
        """)
        row.setFixedHeight(56)

        rl = QHBoxLayout(row)
        rl.setContentsMargins(12, 0, 12, 0)
        rl.setSpacing(0)

        # Checkbox de seleção em lote
        chk = QCheckBox()
        chk.setFixedWidth(30)
        chk.setCursor(Qt.PointingHandCursor)
        chk.setStyleSheet(getattr(self, "_chk_style", ""))
        row._checkbox = chk
        rl.addWidget(chk)

        # Name
        lbl_nome = QLabel(dados.get('nome', ''))
        lbl_nome.setStyleSheet(
            "font-size: 14px; color: #ffffff; background: transparent; border: none;"
        )
        rl.addWidget(lbl_nome, 1)

        # Belt
        belt_wrap = QWidget()
        belt_wrap.setObjectName("beltWrap")
        belt_wrap.setFixedWidth(140)
        belt_wrap.setStyleSheet("#beltWrap { background: transparent; }")
        bwl = QHBoxLayout(belt_wrap)
        bwl.setContentsMargins(0, 0, 0, 0)
        bwl.setSpacing(7)
        _BELT_COLORS = {
            "Branca": "#d0d0d0", "Azul": "#1a4fa0",
            "Roxa": "#6b2fa0", "Marrom": "#8b4a1f", "Preta": "#111111",
        }
        faixa = dados.get('faixa', 'Branca')
        bcolor = cor_faixa(faixa)
        border_s = "border: 1px solid #555555;" if faixa == "Preta" else "border: none;"
        belt_rect = QLabel()
        belt_rect.setFixedSize(30, 7)
        belt_rect.setStyleSheet(f"background: {bcolor}; border-radius: 2px; {border_s}")
        bwl.addWidget(belt_rect)
        belt_name = QLabel(faixa)
        belt_name.setStyleSheet(
            "font-size: 11px; color: #a0a0a0; background: transparent; border: none;"
        )
        bwl.addWidget(belt_name)
        bwl.addStretch()
        rl.addWidget(belt_wrap)

        # Plan
        plano_text = (dados.get('plano') or '')
        lbl_plano = QLabel(plano_text)
        lbl_plano.setFixedWidth(140)
        lbl_plano.setStyleSheet(
            "font-size: 11px; color: #a0a0a0; background: transparent; border: none;"
        )
        rl.addWidget(lbl_plano)

        # Payment status badge
        pag_status = dados.get('pagamento_status', '')
        _STATUS_STYLES = {
            'Pago':     ("background: rgba(26,122,60,0.15);  color: #2d8a52;", "Pago"),
            'Atrasado': ("background: rgba(204,30,30,0.15);  color: #c04444;", "Atrasado"),
            'A Vencer': ("background: rgba(184,124,14,0.15); color: #a07020;", "A Vencer"),
        }
        s_style, s_text = _STATUS_STYLES.get(pag_status, ("background: transparent; color: #9a9a9a;", "—"))
        status_lbl = QLabel(s_text)
        status_lbl.setFixedWidth(90)
        status_lbl.setStyleSheet(
            f"{s_style} font-size: 11px; font-weight: 500; padding: 3px 10px;"
            f" border-radius: 5px; border: none;"
        )
        rl.addWidget(status_lbl)

        row._dados = dados

        def on_click(event, r=row, d=dados):
            self._select_table_row(r, d)

        def on_double(event, d=dados):
            self._abrir_ficha_aluno(d)

        row.mousePressEvent = on_click
        row.mouseDoubleClickEvent = on_double
        row.setCursor(Qt.PointingHandCursor)
        return row

    def _abrir_ficha_aluno(self, dados):
        """Abre a ficha completa do aluno (detalhes, frequência e pagamento)."""
        try:
            from ui.ficha_aluno_dialog import FichaAlunoDialog
            tipo_ficha = "kid" if dados.get("tipo") == "kids" else "adulto"
            FichaAlunoDialog(dados["id"], tipo_ficha, self).exec()
        except Exception as e:
            show_error(self, "Erro", f"Não foi possível abrir a ficha: {e}")

    def _select_table_row(self, selected_row, dados):
        """Highlights the selected row, deselects others."""
        for i in range(self.cards_layout.count()):
            w = self.cards_layout.itemAt(i).widget()
            if w and hasattr(w, '_dados'):
                w.setStyleSheet("""
                    QFrame#tableRow {
                        background: transparent; border: none;
                        border-bottom: 1px solid #181818;
                    }
                    QFrame#tableRow:hover { background: #1a1a1a; }
                """)
        selected_row.setStyleSheet("""
            QFrame#tableRow {
                background: rgba(204,30,30,0.08); border: none;
                border-bottom: 1px solid #181818;
                border-left: 2px solid #cc1e1e;
            }
        """)
        self.aluno_atual = dados
        self._toggle_acoes(True)

    def _populate_table(self, alunos_list):
        """Clears and repopulates the table with sorted rows."""
        self.limpar_cards_completo()
        self.aluno_atual = None
        self._toggle_acoes(False)
        sorted_list = sorted(alunos_list, key=lambda x: (x.get('nome') or '').lower())
        for dados in sorted_list:
            row = self._create_table_row(dados)
            self.cards_layout.addWidget(row)

    def _on_search_changed(self, text):
        if not text.strip():
            # Reaplica os filtros (faixa/tipo) ao limpar a busca
            self.buscar()

    def _on_filter_changed(self, _):
        self.buscar()

    def _btn(self, text):
        b = QPushButton(text)
        b.setFixedSize(160, 42)
        b.setStyleSheet("""
            QPushButton {
                background: #cc1e1e; color: white; border-radius: 6px;
                font-weight: bold; border: none;
            }
            QPushButton:hover  { background: #e02020; }
            QPushButton:pressed{ background: #a01515; }
        """)
        return b

    def _toggle_acoes(self, show):
        self.btn_edit.setVisible(show)
        self.btn_toggle.setVisible(show)
        self.btn_del.setVisible(show)
        self.btn_vincular.setVisible(show)
        self.btn_ficha.setVisible(show)

    # ---------------- DADOS ----------------

    def load(self):
        """Método para recarregar dados - usado como callback de refresh"""
        self.carregar_dados()
        self.busca.clear()
        self._populate_table(self.registros)

    def exportar_lista_pdf(self):
        from ui.export_helpers import exportar_pdf_dialog
        exportar_pdf_dialog(self, "alunos")

    def exportar_ficha_pdf(self):
        if not self.aluno_atual:
            show_warning(self, "Erro", "Nenhum aluno selecionado!")
            return
        if self.aluno_atual.get("tipo") != "adulto":
            show_info(self, "Ficha PDF",
                      "A ficha em PDF está disponível para alunos adultos.")
            return
        from ui.export_helpers import exportar_pdf_dialog
        exportar_pdf_dialog(self, "ficha", aluno_id=self.aluno_atual["id"])

    def _linhas_tabela(self):
        """Retorna os widgets de linha (que têm checkbox e _dados)."""
        linhas = []
        if not hasattr(self, "cards_layout"):
            return linhas
        for i in range(self.cards_layout.count()):
            w = self.cards_layout.itemAt(i).widget()
            if w is not None and hasattr(w, "_checkbox") and hasattr(w, "_dados"):
                linhas.append(w)
        return linhas

    def _toggle_selecionar_todos(self, estado):
        marcar = bool(estado)
        for w in self._linhas_tabela():
            w._checkbox.setChecked(marcar)

    def excluir_selecionados(self):
        selecionados = [w._dados for w in self._linhas_tabela() if w._checkbox.isChecked()]
        if not selecionados:
            show_warning(self, "Excluir selecionados", "Nenhum aluno selecionado.")
            return

        if not show_question(
            self, "🗑️  Confirmar Exclusão em Lote",
            f"ATENÇÃO: esta ação não pode ser desfeita!\n\n"
            f"Deseja excluir {len(selecionados)} aluno(s) selecionado(s)?",
            "Sim, Excluir", "Cancelar"
        ):
            return

        erros = 0
        for d in selecionados:
            try:
                if d.get("tipo") == "adulto":
                    excluir_aluno(d["id"])
                else:
                    excluir_kid(d["id"])
            except Exception:
                erros += 1

        if hasattr(self, "chk_todos"):
            self.chk_todos.blockSignals(True)
            self.chk_todos.setChecked(False)
            self.chk_todos.blockSignals(False)
        self.aluno_atual = None

        excluidos = len(selecionados) - erros
        msg = f"{excluidos} aluno(s) excluído(s) com sucesso."
        if erros:
            msg += f"\n{erros} não puderam ser excluídos."
        show_info(self, "Exclusão concluída", msg)
        self.buscar()

    def definir_plano_selecionados(self):
        selecionados = [w._dados for w in self._linhas_tabela() if w._checkbox.isChecked()]
        if not selecionados:
            show_warning(self, "Definir plano", "Nenhum aluno selecionado.")
            return

        opcoes = [p for p in get_planos_formatados() if p != "Plano Personalizado"]
        if "Adulto - R$180" not in opcoes:
            opcoes.insert(0, "Adulto - R$180")
        plano, ok = show_combo(
            self, "Definir plano",
            f"Plano a aplicar aos {len(selecionados)} aluno(s) selecionado(s):",
            opcoes, default="Adulto - R$180"
        )
        if not ok or not plano.strip():
            return
        plano = plano.strip()

        for d in selecionados:
            tipo = d.get("tipo", "adulto")
            definir_plano_aluno(d["id"], plano, "adulto" if tipo == "adulto" else "kids")
            aid = d["id"] if tipo == "adulto" else -d["id"]
            atualizar_mensalidades_por_plano(aid, plano)

        # Gera as mensalidades (mês atual em diante) para quem passou a ter plano
        try:
            gerar_mensalidades_anuais()
        except Exception:
            pass

        if hasattr(self, "chk_todos"):
            self.chk_todos.blockSignals(True)
            self.chk_todos.setChecked(False)
            self.chk_todos.blockSignals(False)

        show_info(
            self, "Plano definido",
            f"Plano '{plano}' aplicado a {len(selecionados)} aluno(s).\n"
            f"As mensalidades foram geradas (do mês atual em diante)."
        )
        self.buscar()

    def carregar_dados(self):
        self.registros.clear()
        try:
            status_mes = obter_status_pagamento_mes()
        except Exception:
            status_mes = {}

        for a in listar_todos_alunos():  # Agora lista TODOS (ativos e inativos) com responsáveis
            # Estrutura da tabela alunos: 0-id, 1-nome, 2-cpf, 3-email, 4-telefone, 5-cep, 6-endereco, 
            # 7-data_nascimento, 8-faixa, 9-grau, 10-peso, 11-altura, 12-plano, 13-foto_path, 
            # 14-certificado_path, 15-ativo, 16-criado_em, 17-biometria_data, 18-responsavel_id
            # Colunas adicionadas pela query: 19-responsavel_nome, 20-responsavel_cpf, 21-dependentes_nomes, 22-total_dependentes
            self.registros.append({
                "tipo": "adulto",
                "id": a[0],           # id
                "nome": a[1],         # nome
                "cpf": a[2],          # cpf
                "email": a[3] or "",  # email
                "telefone": a[4] or "", # telefone
                "cep": a[5] or "",    # cep
                "endereco": a[6] or "", # endereco
                "data_nascimento": a[7] or "", # data_nascimento
                "faixa": a[8],        # faixa
                "grau": a[9],         # grau
                "peso": a[10] or "",  # peso
                "altura": a[11] or "", # altura
                "plano": a[12],       # plano
                "foto": a[13],        # foto_path
                "certificado": a[14], # certificado_path
                "status": a[15],      # ativo ← CORRIGIDO DE NOVO! Índice 15, não 16!
                "criado_em": a[16] if len(a) > 16 else None,  # criado_em
                "biometria": a[17] if len(a) > 17 else None,   # biometria_data
                "responsavel_id": a[18] if len(a) > 18 else None,  # responsavel_id
                "responsavel_nome": a[19] if len(a) > 19 and a[19] else None,
                "responsavel_cpf": a[20] if len(a) > 20 and a[20] else None,
                "dependentes_nomes": a[21] if len(a) > 21 and a[21] else None,
                "total_dependentes": a[22] if len(a) > 22 else 0,
                # Status de pagamento: vazio para dependentes vinculados
                "pagamento_status": "" if (len(a) > 18 and a[18]) else status_mes.get(a[0], ''),
            })

        # Mapa CPF -> id dos adultos (para propagar status do responsável aos kids)
        _cpf_para_id_adulto = {
            r["cpf"]: r["id"] for r in self.registros if r["tipo"] == "adulto" and r.get("cpf")
        }

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM kids")  # Kids já lista todos
        kids = cur.fetchall()
        conn.close()

        for k in kids:
            _plano_kid = (k[14] or "")
            _dependente = ("dependente" in _plano_kid.lower()) or ("vinculado" in _plano_kid.lower())
            _resp_id = _cpf_para_id_adulto.get(k[4])
            if _dependente and _resp_id:
                # Kid dependente: status igual ao do responsável
                _pag_status = status_mes.get(_resp_id, '')
            else:
                _pag_status = status_mes.get(-k[0], '')
            self.registros.append({
                "tipo": "kids",
                "id": k[0],
                "nome": k[1],
                "cpf": k[2] or "",
                "email": k[5] or "",
                "telefone": k[6] or "",
                "cep": k[7] or "",
                "endereco": k[8] or "",
                "data_nascimento": k[9] or "",
                "faixa": k[10],
                "grau": k[11],
                "peso": k[12] or "",
                "altura": k[13] or "",
                "plano": k[14],
                "foto": k[15],
                "status": k[17],
                "responsavel": k[3],
                "responsavel_cpf": k[4],
                "pagamento_status": _pag_status,
            })

    # ---------------- AÇÕES ----------------

    def mostrar_todos_alunos(self):
        """Mostra dialog com todos os alunos listados"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Todos os Alunos")
        dialog.setModal(True)
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Título
        titulo = QLabel(f"Total de Alunos Cadastrados: {len(self.registros)}")
        titulo.setStyleSheet("color:black;font-size:16px;font-weight:bold;margin:10px;")
        layout.addWidget(titulo)
        
        # Área scrollável
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Separar adultos e kids
        adultos = [r for r in self.registros if r["tipo"] == "adulto"]
        kids = [r for r in self.registros if r["tipo"] == "kids"]
        
        if adultos:
            # Seção Adultos
            titulo_adultos = QLabel(f"👨‍🎓 ADULTOS ({len(adultos)})")
            titulo_adultos.setStyleSheet("color:#cc1e1e;font-size:14px;font-weight:bold;margin:10px 0px 5px 0px;")
            scroll_layout.addWidget(titulo_adultos)
            
            for aluno in adultos:
                item = self.criar_item_lista(aluno)
                scroll_layout.addWidget(item)
        
        if kids:
            # Seção Kids
            titulo_kids = QLabel(f"🧒 KIDS ({len(kids)})")
            titulo_kids.setStyleSheet("color:#cc1e1e;font-size:14px;font-weight:bold;margin:10px 0px 5px 0px;")
            scroll_layout.addWidget(titulo_kids)
            
            for kid in kids:
                item = self.criar_item_lista(kid)
                scroll_layout.addWidget(item)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Botão fechar
        btn_fechar = QPushButton("Fechar")
        btn_fechar.setStyleSheet("""
            QPushButton {
                background:#cc1e1e;color:white;border-radius:8px;
                padding:8px 20px;font-weight:bold;
            }
            QPushButton:hover { background:#e02020; }
        """)
        btn_fechar.clicked.connect(dialog.close)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_fechar)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    def criar_item_lista(self, dados):
        """Cria um item da lista de alunos"""
        item = QFrame()
        item.setStyleSheet("""
            QFrame {
                background:rgba(240,240,240,0.9);
                border-radius:8px;
                margin:2px;
                padding:5px;
            }
            QFrame:hover {
                background:rgba(220,220,220,0.9);
            }
        """)
        item.setFixedHeight(60)
        item.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(item)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Informações principais
        info_layout = QVBoxLayout()
        
        nome_label = QLabel(dados["nome"])
        nome_label.setStyleSheet("font-size:13px;font-weight:bold;color:#e0e0e0;")
        
        detalhes = f"CPF: {dados.get('cpf', 'N/A')} • {dados['faixa']} {dados['grau']} • {dados['plano']}"
        if dados.get("responsavel"):
            detalhes += f" • Resp: {dados['responsavel']}"
            
        detalhes_label = QLabel(detalhes)
        detalhes_label.setStyleSheet("font-size:11px;color:#666;")
        
        info_layout.addWidget(nome_label)
        info_layout.addWidget(detalhes_label)
        
        layout.addLayout(info_layout, 1)
        
        # Status
        status_label = QLabel("ATIVO" if dados["status"] else "INATIVO")
        if dados["status"]:
            status_label.setStyleSheet("background:#0f5132;color:#00ff99;padding:4px 8px;border-radius:6px;font-size:10px;font-weight:bold;")
        else:
            status_label.setStyleSheet("background:#5a1a1a;color:#ff6666;padding:4px 8px;border-radius:6px;font-size:10px;font-weight:bold;")
            
        layout.addWidget(status_label)
        
        # Adicionar clique para selecionar aluno
        def selecionar_aluno():
            self.card.set_dados(dados)
            self.card.setVisible(True)
            self._toggle_acoes(True)
            # Fechar o dialog
            item.window().close()
            
        item.mousePressEvent = lambda event: selecionar_aluno()
        
        return item

    # ---------------- AÇÕES ----------------

    def mostrar_hierarquia_familiar(self, responsavel, dependentes_adultos=None, dependentes_kids=None):
        """Mostra hierarquia familiar: responsável → dependentes adultos → kids
        
        COMPATIBILIDADE: Se dependentes_adultos for uma lista e dependentes_kids for None,
        assume que dependentes_adultos contém kids (compatibilidade com versão antiga)
        """
        # Limpar completamente tudo
        self.limpar_cards_completo()
        
        # Container principal com centralização forçada
        container_principal = QWidget()
        container_principal.setStyleSheet("background: transparent;")
        
        # Layout horizontal para centralizar todo o organograma
        layout_horizontal = QHBoxLayout(container_principal)
        layout_horizontal.addStretch(1)  # Stretch à esquerda
        
        # Container do organograma
        container_organograma = QWidget()
        container_organograma.setStyleSheet("background: transparent;")
        
        # Layout vertical para organizar responsável e dependentes
        layout_principal = QVBoxLayout(container_organograma)
        layout_principal.setSpacing(25)  # Espaço entre níveis
        layout_principal.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        
        # === RESPONSÁVEL NO TOPO ===
        layout_responsavel = QHBoxLayout()
        layout_responsavel.setAlignment(Qt.AlignHCenter)
        
        card_responsavel = AlunoCard()
        card_responsavel.set_dados(responsavel)
        card_responsavel.setVisible(True)
        # Adicionar seleção ao card responsável
        self.adicionar_selecao_card(card_responsavel, responsavel)
        
        # Indicador visual de que é o responsável
        card_responsavel.setStyleSheet(card_responsavel.styleSheet() + """
            QFrame {
                border: 2px solid #cc1e1e;
                background: rgba(204,30,30,0.08);
            }
        """)
        
        layout_responsavel.addWidget(card_responsavel)
        layout_principal.addLayout(layout_responsavel)
        
        # === DEPENDENTES ADULTOS (NOVO NÍVEL) ===
        if dependentes_adultos:
            # Linha de conexão para dependentes adultos
            linha_adultos = QFrame()
            linha_adultos.setFrameShape(QFrame.HLine)
            linha_adultos.setFixedHeight(2)
            linha_adultos.setStyleSheet("background: #ffa500; border: none;")  # Cor laranja para adultos
            layout_principal.addWidget(linha_adultos)
            
            layout_adultos = QHBoxLayout()
            layout_adultos.setAlignment(Qt.AlignHCenter)
            layout_adultos.setSpacing(15)
            
            for dependente_adulto in dependentes_adultos:
                card_adulto = AlunoCard()
                card_adulto.set_dados(dependente_adulto)
                card_adulto.setVisible(True)
                # Adicionar seleção ao card dependente adulto
                self.adicionar_selecao_card(card_adulto, dependente_adulto)
                
                # Estilo diferenciado para dependentes adultos
                card_adulto.setStyleSheet(card_adulto.styleSheet() + """
                    QFrame {
                        border: 1px solid rgba(255,165,0,0.8);
                        background: rgba(255,165,0,0.1);
                    }
                """)
                
                layout_adultos.addWidget(card_adulto)
            
            layout_principal.addLayout(layout_adultos)
        
        # === KIDS EMBAIXO ===
        if dependentes_kids:
            # Linha de conexão para kids
            linha_kids = QFrame()
            linha_kids.setFrameShape(QFrame.HLine)
            linha_kids.setFixedHeight(2)
            linha_kids.setStyleSheet("background: #00ff99; border: none;")  # Cor verde para kids
            layout_principal.addWidget(linha_kids)
            
            layout_kids = QHBoxLayout()
            layout_kids.setAlignment(Qt.AlignHCenter)
            layout_kids.setSpacing(15)
            
            for dependente_kid in dependentes_kids:
                card_kid = AlunoCard()
                card_kid.set_dados(dependente_kid)
                card_kid.setVisible(True)
                # Adicionar seleção ao card kid
                self.adicionar_selecao_card(card_kid, dependente_kid)
                
                # Estilo diferenciado para kids
                card_kid.setStyleSheet(card_kid.styleSheet() + """
                    QFrame {
                        border: 1px solid rgba(0,255,153,0.6);
                        background: rgba(0,255,153,0.08);
                    }
                """)
                
                layout_kids.addWidget(card_kid)
            
            layout_principal.addLayout(layout_kids)
        
        # === COMPATIBILIDADE COM CHAMADAS ANTIGAS ===
        # Se foi chamado com parâmetros antigos (responsavel, dependentes), 
        # tratar dependentes como kids
        if dependentes_adultos is None and dependentes_kids is None:
            # Esta é uma chamada antiga - não fazer nada, já foi tratado acima
            pass
        
        # Adicionar o organograma ao layout horizontal centralizado
        layout_horizontal.addWidget(container_organograma)
        layout_horizontal.addStretch(1)  # Stretch à direita
        
        # Adicionar à área de cards
        self.cards_layout.addWidget(container_principal)
        
        # Mostrar área dos cards
        self.cards_area.setVisible(True)
        
        # Responsável como aluno atual inicial
        self.aluno_atual = responsavel
        self._toggle_acoes(True)

    def adicionar_selecao_card(self, card, aluno_dados):
        """Adiciona sistema de seleção ao card"""
        # Estado inicial - não selecionado
        card.selecionado = False
        card.dados_aluno = aluno_dados
        
        # Estilo original do card
        estilo_original = card.styleSheet()
        
        def selecionar_card():
            # Limpar seleção de todos os outros cards
            self.limpar_selecoes_cards()
            
            # Marcar este card como selecionado
            card.selecionado = True
            
            # Aplicar estilo de selecionado
            card.setStyleSheet(estilo_original + """
                QFrame {
                    border: 3px solid #cc1e1e !important;
                    background: rgba(229,9,20,0.1) !important;
                }
            """)
            
            # Definir como aluno atual
            self.aluno_atual = aluno_dados
            self._toggle_acoes(True)
        
        def deselecionar_card():
            card.selecionado = False
            card.setStyleSheet(estilo_original)
        
        # Adicionar evento de clique
        card.mousePressEvent = lambda event: selecionar_card()
        card.deselecionar = deselecionar_card
        
        # Cursor de mão para indicar que é clicável
        card.setCursor(Qt.PointingHandCursor)
    
    def selecionar_card(self, aluno_dados):
        """Seleciona um card específico baseado nos dados do aluno"""
        def encontrar_card_recursivo(widget):
            # Verificar se é um card com dados do aluno
            if hasattr(widget, 'dados_aluno') and hasattr(widget, 'mousePressEvent'):
                if (widget.dados_aluno.get('id') == aluno_dados.get('id') and 
                    widget.dados_aluno.get('tipo') == aluno_dados.get('tipo')):
                    # Simular clique no card para selecioná-lo
                    widget.mousePressEvent(None)
                    return True
            
            # Procurar recursivamente nos filhos
            if hasattr(widget, 'children'):
                for child in widget.children():
                    if encontrar_card_recursivo(child):
                        return True
            return False
        
        # Procurar o card na área de cards
        encontrar_card_recursivo(self.cards_area)
    
    def limpar_selecoes_cards(self):
        """Remove seleção de todos os cards"""
        def limpar_widget_recursivo(widget):
            if hasattr(widget, 'selecionado') and hasattr(widget, 'deselecionar'):
                if widget.selecionado:
                    widget.deselecionar()
            
            # Verificar filhos recursivamente
            for child in widget.children():
                if hasattr(child, 'children'):  # É um widget
                    limpar_widget_recursivo(child)
        
        limpar_widget_recursivo(self.cards_area)

    def mostrar_todos_grid_centralizado(self, alunos_list):
        """Mostra todos os alunos em grid 2 colunas bem centralizado"""
        # Limpar completamente tudo
        self.limpar_cards_completo()
        
        # Container principal com centralização forçada
        container_principal = QWidget()
        container_principal.setStyleSheet("background: transparent;")
        
        # Layout horizontal para centralizar o grid
        layout_horizontal = QHBoxLayout(container_principal)
        layout_horizontal.setContentsMargins(30, 0, 30, 0)  # Margens laterais maiores
        layout_horizontal.addStretch(1)  # Stretch à esquerda
        
        # Container do grid com largura calculada corretamente
        container_grid = QWidget()
        # Largura: 2 cards de 480px + espaçamento de 15px + margens = 1000px
        container_grid.setFixedWidth(1000)
        container_grid.setStyleSheet("background: transparent;")
        
        # Layout em grid
        from PySide6.QtWidgets import QGridLayout
        grid = QGridLayout(container_grid)
        grid.setSpacing(15)  # Espaço reduzido para não cortar
        grid.setAlignment(Qt.AlignCenter)
        grid.setContentsMargins(15, 10, 15, 10)  # Margens uniformes
        
        # Adicionar cards em grid 2 colunas
        row = 0
        col = 0
        
        for aluno in alunos_list:
            card = AlunoCard()
            card.set_dados(aluno)
            card.setVisible(True)
            # Adicionar sistema de seleção ao card
            self.adicionar_selecao_card(card, aluno)
            # Configurar vínculos para dependentes
            self.configurar_vinculo_dependente(card, aluno)
            
            grid.addWidget(card, row, col)
            
            col += 1
            if col >= 2:  # Máximo 2 colunas
                col = 0
                row += 1
        
        # Adicionar o grid ao layout horizontal centralizado
        layout_horizontal.addWidget(container_grid)
        layout_horizontal.addStretch(1)  # Stretch à direita
        
        # Scroll apenas se necessário
        if len(alunos_list) > 8:  # Mais de 4 linhas
            scroll_area = QScrollArea()
            scroll_area.setStyleSheet("background: transparent; border: none;")
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setWidget(container_principal)
            self.cards_layout.addWidget(scroll_area)
        else:
            self.cards_layout.addWidget(container_principal)
        
        # Mostrar área dos cards
        self.cards_area.setVisible(True)

    def organizar_resultado_hierarquico(self, alunos_encontrados):
        """Organiza os resultados: se há responsável com dependentes, mostra hierarquia"""
        # Separar adultos e kids dos resultados
        adultos_encontrados = [a for a in alunos_encontrados if a["tipo"] == "adulto"]
        kids_encontrados = [k for k in alunos_encontrados if k["tipo"] == "kids"]
        
        # Verificar se algum adulto tem dependentes (adultos ou kids)
        responsavel_com_dependentes = None
        dependentes_adultos = []  # NOVA: dependentes adultos
        dependentes_kids = []     # Kids dependentes
        
        for adulto in adultos_encontrados:
            # Procurar dependentes adultos vinculados a este responsável
            adultos_dependentes = []
            for registro in self.registros:
                if (registro["tipo"] == "adulto" and 
                    registro.get("responsavel_id") and
                    registro["responsavel_id"] == adulto["id"] and
                    registro["id"] != adulto["id"]):  # Não incluir ele mesmo
                    adultos_dependentes.append(registro)
            
            # Procurar kids que têm este adulto como responsável
            kids_deste_adulto = []
            for registro in self.registros:
                if (registro["tipo"] == "kids" and 
                    registro.get("responsavel_cpf") == adulto["cpf"]):
                    kids_deste_adulto.append(registro)
            
            # Se tem dependentes (adultos ou kids), este é o responsável da hierarquia
            if adultos_dependentes or kids_deste_adulto:
                responsavel_com_dependentes = adulto
                dependentes_adultos = adultos_dependentes
                dependentes_kids = kids_deste_adulto
                break
        
        if responsavel_com_dependentes and (dependentes_adultos or dependentes_kids):
            # Mostrar hierarquia: responsável → dependentes adultos → kids
            self.mostrar_hierarquia_familiar(responsavel_com_dependentes, dependentes_adultos, dependentes_kids)
        else:
            # Mostrar resultado normal em grid
            alunos_ordenados = sorted(alunos_encontrados, key=lambda x: x["nome"].lower())
            self.mostrar_cards_grid(alunos_ordenados)
        
        # Mostrar área dos cards
        self.cards_area.setVisible(True)
        
        # Atualizar botões de ação para o primeiro aluno
        if alunos_encontrados:
            self.aluno_atual = alunos_encontrados[0]
            self._toggle_acoes(True)
    
    def limpar_cards_completo(self):
        """Remove TODOS os widgets da área de cards"""
        # Limpar tudo do layout de cards
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout_recursive(child.layout())
    
    def limpar_cards(self):
        """Remove todos os cards da tela (método legado)"""
        self.limpar_cards_completo()
    
    def esconder_cards(self):
        """Limpa a tabela e esconde botões de ação."""
        self.limpar_cards_completo()
        self._toggle_acoes(False)

    def mostrar_cards_grid(self, alunos_list):
        """Mostra os alunos em um grid de 2 colunas (caso padrão)"""
        # Limpar completamente tudo
        self.limpar_cards_completo()
        
        # Container principal com centralização forçada
        container_principal = QWidget()
        container_principal.setStyleSheet("background: transparent;")
        
        # Layout horizontal para centralizar o grid
        layout_horizontal = QHBoxLayout(container_principal)
        layout_horizontal.setContentsMargins(30, 0, 30, 0)  # Margens laterais maiores
        layout_horizontal.addStretch(1)  # Stretch à esquerda
        
        # Container do grid com largura calculada corretamente
        container_grid = QWidget()
        # Largura: 2 cards de 480px + espaçamento de 15px + margens = 1000px
        container_grid.setFixedWidth(1000)  
        container_grid.setStyleSheet("background: transparent;")
        
        # Layout em grid
        from PySide6.QtWidgets import QGridLayout
        grid = QGridLayout(container_grid)
        grid.setSpacing(15)  # Espaçamento reduzido para não cortar
        grid.setAlignment(Qt.AlignCenter)
        grid.setContentsMargins(15, 10, 15, 10)  # Margens uniformes
        
        # Adicionar cards em grid 2 colunas
        row = 0
        col = 0
        
        for aluno in alunos_list:
            card = AlunoCard()
            card.set_dados(aluno)
            card.setVisible(True)
            # Adicionar sistema de seleção ao card
            self.adicionar_selecao_card(card, aluno)
            # Configurar vínculos para dependentes
            self.configurar_vinculo_dependente(card, aluno)
            
            # Adicionar no grid (2 colunas)
            grid.addWidget(card, row, col)
            
            col += 1
            if col >= 2:  # Máximo 2 colunas
                col = 0
                row += 1
        
        # Adicionar o grid ao layout horizontal centralizado
        layout_horizontal.addWidget(container_grid)
        layout_horizontal.addStretch(1)  # Stretch à direita
        
        # Adicionar à área de cards
        self.cards_layout.addWidget(container_principal)
        
        # Mostrar área dos cards
        self.cards_area.setVisible(True)

    def buscar(self):
        self.carregar_dados()
        termo = self.busca.text().lower().strip()
        faixa_filtro = self.combo_faixa.currentText() if hasattr(self, 'combo_faixa') else "Todas as faixas"
        tipo_filtro = self.combo_tipo.currentText() if hasattr(self, 'combo_tipo') else "Todos"

        candidatos = self.registros
        if faixa_filtro and faixa_filtro != "Todas as faixas":
            candidatos = [r for r in candidatos if r.get('faixa', '') == faixa_filtro]

        if tipo_filtro == "Adulto":
            candidatos = [r for r in candidatos
                          if r.get('tipo') == 'adulto' and not r.get('responsavel_id')]
        elif tipo_filtro == "Kids":
            candidatos = [r for r in candidatos if r.get('tipo') == 'kids']
        elif tipo_filtro == "Dependente":
            candidatos = [
                r for r in candidatos
                if (r.get('tipo') == 'adulto' and r.get('responsavel_id'))
                or (r.get('tipo') == 'kids' and (r.get('plano') or '') == 'Dependente')
            ]

        if not termo:
            self._populate_table(candidatos)
            return

        alunos_encontrados = [
            r for r in candidatos
            if termo in (r["nome"] or "").lower()
            or termo in (r["cpf"] or "")
            or (r.get("responsavel") and termo in r["responsavel"].lower())
        ]

        if alunos_encontrados:
            self._populate_table(alunos_encontrados)
        else:
            show_info(self, "Não encontrado", "Aluno não localizado.")
            self._populate_table([])

    def toggle_status(self):
        if not self.aluno_atual:
            show_warning(self, "Erro", "Nenhum aluno selecionado!")
            return
            
        d = self.aluno_atual
        nome = d["nome"]
        status_atual = "ATIVO" if d["status"] else "INATIVO"
        novo_status_texto = "INATIVO" if d["status"] else "ATIVO"

        # Verificar dependentes ao inativar responsável
        dependentes = None
        if d["tipo"] == "adulto" and d["status"]:  # Se está inativando
            dependentes = obter_dependentes(d["id"], d.get("cpf"))
            total_dep = len(dependentes.get("adultos", [])) + len(dependentes.get("kids", []))

            if total_dep > 0:
                # Abrir diálogo para gerenciar dependentes
                from ui.inativar_dependentes_dialog import InativarDependentesDialog
                dlg = InativarDependentesDialog(self, nome, dependentes)
                if dlg.exec() != dlg.Accepted:
                    return

                # Processar a escolha do usuário
                if dlg.escolha == "inativar":
                    self.executar_inativacao(d, inativar_deps=True)
                    show_info(
                        self,
                        "Dependentes Inativados",
                        f"✅ Responsável {nome} e seus {total_dep} dependente(s) foram inativados."
                    )
                elif dlg.escolha == "ajustar":
                    self.executar_inativacao(d, inativar_deps=False, valores_ajustados=dlg.valores_ajustados)
                    show_info(
                        self,
                        "Valores Ajustados",
                        f"✅ Responsável {nome} inativado.\n\n"
                        f"Valores de {len(dlg.valores_ajustados)} dependente(s) foram ajustados."
                    )
                else:
                    return
            else:
                # Confirmação normal se não houver dependentes
                if show_question(
                    self,
                    "Confirmar Alteração",
                    f"Aluno: {nome}\nStatus atual: {status_atual}\n\nDeseja alterar para {novo_status_texto}?",
                    "Sim", "Não"
                ):
                    self.executar_inativacao(d)
                    show_info(
                        self,
                        "Sucesso",
                        f"Status do aluno {nome} alterado para {novo_status_texto}!"
                    )
                else:
                    return
        else:
            # Confirmação normal (sem dependentes ou reativando)
            if show_question(
                self,
                "Confirmar Alteração",
                f"Aluno: {nome}\nStatus atual: {status_atual}\n\nDeseja alterar para {novo_status_texto}?",
                "Sim", "Não"
            ):
                self.executar_inativacao(d)
                show_info(
                    self,
                    "Sucesso",
                    f"Status do aluno {nome} alterado para {novo_status_texto}!"
                )

        # Recarregar e repopular a tabela
        self.buscar()
    
    def executar_inativacao(self, dados_aluno, inativar_deps=False, valores_ajustados=None):
        """Executa a inativação/ativação do aluno no banco de dados

        inativar_deps: se True, inativa também todos os dependentes
        valores_ajustados: dict com {tipo_id: valor} para atualizar dependentes
        """
        try:
            novo_status = 0 if dados_aluno["status"] else 1

            if dados_aluno["tipo"] == "adulto":
                # Alterar status no banco adultos
                inativar_aluno(dados_aluno["id"], novo_status)

                # Processar dependentes se necessário
                if inativar_deps and novo_status == 0:
                    inativar_dependentes(dados_aluno["id"])

                if valores_ajustados and novo_status == 0:
                    for key, valor in valores_ajustados.items():
                        tipo, dep_id = key.split("_")
                        atualizar_valor_dependente(int(dep_id), tipo, valor)
            else:
                # Alterar status no banco kids (também sincroniza mensalidades)
                from database.kids_db import inativar_kid
                inativar_kid(dados_aluno["id"], novo_status)

            # Atualizar o objeto atual se for o mesmo
            if self.aluno_atual and self.aluno_atual["id"] == dados_aluno["id"]:
                self.aluno_atual["status"] = novo_status

        except Exception as e:
            show_error(
                self,
                "Erro",
                f"Erro ao alterar status: {str(e)}"
            )

    def vincular_responsavel(self):
        """Vincula o aluno selecionado a um responsável (busca por nome/CPF)."""
        if not self.aluno_atual:
            show_warning(self, "Vincular", "Selecione um aluno primeiro.")
            return
        d = self.aluno_atual
        if d.get("tipo") != "adulto":
            show_warning(self, "Vincular",
                         "A vinculação de dependente é feita apenas para alunos adultos.")
            return
        from utils.vincular_utils import vincular_dependente
        if vincular_dependente(self, d["id"], d.get("nome")):
            self.aluno_atual = None
            self.buscar()

    def excluir(self):
        if not self.aluno_atual:
            show_warning(self, "Erro", "Nenhum aluno selecionado!")
            return

        d = self.aluno_atual
        nome = d["nome"]
        tipo = "Adulto" if d["tipo"] == "adulto" else "Criança"

        # Verificar dependentes (adultos vinculados + kids do mesmo CPF)
        dependentes = {"adultos": [], "kids": []}
        if d["tipo"] == "adulto":
            dependentes = obter_dependentes(d["id"], d.get("cpf"))
        lista_dep = list(dependentes["adultos"]) + list(dependentes["kids"])
        total_dep = len(lista_dep)

        # Se houver dependentes, avisar e pedir uma ação antes de excluir
        if total_dep > 0:
            nomes = "\n".join(f"• {dep[1]}" for dep in lista_dep)
            acao, ok = show_combo(
                self,
                "⚠️  Responsável com dependentes",
                (f"'{nome}' é responsável por {total_dep} dependente(s):\n\n{nomes}\n\n"
                 f"Antes de excluir, escolha o que fazer com os dependentes:"),
                ["Ajustar plano dos dependentes", "Nomear novo responsável"],
                default="Ajustar plano dos dependentes",
            )
            if not ok:
                return
            if acao == "Ajustar plano dos dependentes":
                if not self._ajustar_plano_dependentes(d, dependentes):
                    return
            else:
                if not self._nomear_novo_responsavel(d, dependentes):
                    return

        # Mensagem de confirmação
        mensagem = f"ATENÇÃO: Esta ação não pode ser desfeita!\n\n"
        mensagem += f"Aluno: {nome}\n"
        mensagem += f"Tipo: {tipo}\n"
        mensagem += f"\nAs mensalidades deste aluno também serão excluídas."
        mensagem += f"\n\nDeseja realmente EXCLUIR este aluno?"

        resposta = show_question(
            self,
            "🗑️  Confirmar Exclusão",
            mensagem,
            "Sim, Excluir", "Não, Cancelar"
        )

        if not resposta:
            return

        try:
            if d["tipo"] == "adulto":
                excluir_aluno(d["id"])
            else:
                excluir_kid(d["id"])

            # Feedback de sucesso
            show_info(
                self, 
                "Sucesso", 
                f"Aluno {nome} foi excluído com sucesso!"
            )
            
            # Recarregar tabela
            self.aluno_atual = None
            self.buscar()
                
        except Exception as e:
            show_error(
                self, 
                "Erro", 
                f"Erro ao excluir aluno: {str(e)}"
            )

    def _ajustar_plano_dependentes(self, responsavel, dependentes):
        """Aplica um novo plano aos dependentes e os desvincula do responsável.

        Retorna True se a ação foi concluída (ou não havia o que fazer).
        """
        opcoes = [p for p in get_planos_formatados() if p != "Plano Personalizado"]
        if not opcoes:
            opcoes = ["Adulto - R$180"]
        plano, ok = show_combo(
            self, "Ajustar plano dos dependentes",
            "Selecione o plano que passará a valer para os dependentes:",
            opcoes, default=opcoes[0]
        )
        if not ok or not plano.strip():
            return False
        plano = plano.strip()

        try:
            for dep_id, _dep_nome, _dep_plano in dependentes["adultos"]:
                definir_plano_aluno(dep_id, plano, "adulto")
                atualizar_mensalidades_por_plano(dep_id, plano)
            for dep_id, _dep_nome, _dep_plano in dependentes["kids"]:
                definir_plano_aluno(dep_id, plano, "kids")
                atualizar_mensalidades_por_plano(-dep_id, plano)

            # Dependentes adultos deixam de ter responsável
            desvincular_dependentes(responsavel["id"])

            try:
                gerar_mensalidades_anuais()
            except Exception:
                pass
            return True
        except Exception as e:
            show_error(self, "Erro", f"Não foi possível ajustar os planos: {str(e)}")
            return False

    def _nomear_novo_responsavel(self, responsavel, dependentes):
        """Transfere os dependentes para um novo responsável escolhido pelo usuário.

        Retorna True se a ação foi concluída.
        """
        # Candidatos: dependentes adultos + demais adultos ativos (exceto o que será excluído)
        candidatos = {}  # nome exibido -> (id, nome, cpf)
        for dep_id, dep_nome, _p in dependentes["adultos"]:
            candidatos[f"{dep_nome} (dependente)"] = (dep_id, dep_nome)

        for reg in self.registros:
            if reg.get("tipo") == "adulto" and reg.get("id") != responsavel["id"]:
                if not any(v[0] == reg["id"] for v in candidatos.values()):
                    candidatos[reg["nome"]] = (reg["id"], reg["nome"])

        if not candidatos:
            show_warning(
                self, "Sem candidatos",
                "Não há outro adulto disponível para assumir como responsável.\n"
                "Ajuste o plano dos dependentes."
            )
            return False

        escolha, ok = show_combo(
            self, "Nomear novo responsável",
            "Selecione quem passará a ser o responsável pelos dependentes:",
            list(candidatos.keys()), default=list(candidatos.keys())[0]
        )
        if not ok or escolha not in candidatos:
            return False

        novo_id, novo_nome = candidatos[escolha]

        # Buscar o CPF do novo responsável
        novo_cpf = None
        for reg in self.registros:
            if reg.get("id") == novo_id and reg.get("tipo") == "adulto":
                novo_cpf = reg.get("cpf")
                break

        try:
            reatribuir_dependentes(
                responsavel["id"], responsavel.get("cpf"),
                novo_id, novo_nome, novo_cpf
            )
            show_info(
                self, "Responsável atualizado",
                f"Os dependentes agora estão vinculados a {novo_nome}."
            )
            return True
        except Exception as e:
            show_error(self, "Erro", f"Não foi possível reatribuir os dependentes: {str(e)}")
            return False

                
    def sincronizar_planos_dependentes(self, responsavel_cpf, novo_plano, aluno_origem_id):
        """Sincroniza o plano entre todos os dependentes do mesmo responsável"""
        try:
            conn = get_conn()
            cur = conn.cursor()
            
            # Buscar todos os dependentes do mesmo responsável
            cur.execute(
                "SELECT id, nome FROM kids WHERE responsavel_cpf=? AND ativo=1 AND id!=?",
                (responsavel_cpf, aluno_origem_id)
            )
            outros_dependentes = cur.fetchall()
            
            if len(outros_dependentes) > 0:
                # Perguntar se quer sincronizar
                nomes = [dep[1] for dep in outros_dependentes]
                mensagem = f"Este responsável possui outros {len(outros_dependentes)} dependente(s):\n\n"
                mensagem += "\n".join([f"• {nome}" for nome in nomes])
                mensagem += f"\n\nDeseja aplicar o mesmo plano ({novo_plano}) para todos os dependentes?"
                
                if show_question(
                    self,
                    "🔄 Sincronizar Planos",
                    mensagem,
                    "Sim, Sincronizar", "Não"
                ):
                    # Atualizar todos os outros dependentes
                    cur.execute(
                        "UPDATE kids SET plano=? WHERE responsavel_cpf=? AND ativo=1 AND id!=?",
                        (novo_plano, responsavel_cpf, aluno_origem_id)
                    )
                    
                    conn.commit()
                    
                    show_info(
                        self,
                        "Planos Sincronizados",
                        f"🔄 {len(outros_dependentes)} dependente(s) tiveram seus planos sincronizados para: {novo_plano}"
                    )
                    
                    # Recarregar dados para mostrar as mudanças
                    self.carregar_dados()
            
            conn.close()
                    
        except Exception as e:
            show_error(self, "Erro de Sincronização", f"Erro ao sincronizar planos: {str(e)}")
        
    def obter_outros_dependentes(self, responsavel_cpf, excluir_id):
        """Obtém outros dependentes do mesmo responsável"""
        outros_dependentes = []
        for registro in self.registros:
            if (registro.get("tipo") == "kids" and 
                registro.get("responsavel_cpf") == responsavel_cpf and
                registro.get("id") != excluir_id):
                outros_dependentes.append(registro)
        return outros_dependentes
        
    def configurar_vinculo_dependente(self, card, dados):
        """Configura o aviso de vínculo para dependentes"""
        if dados["tipo"] == "kids" and dados.get("responsavel_cpf"):
            outros_dependentes = self.obter_outros_dependentes(
                dados["responsavel_cpf"], 
                dados["id"]
            )
            
            if len(outros_dependentes) > 0 and hasattr(card, 'vinculo_widget'):
                # Atualizar o texto do aviso de forma mais compacta
                card.vinculo_widget.setText(
                    f"🔗 +{len(outros_dependentes)} dependente(s) - Clique aqui"
                )
                card.vinculo_widget.show()
                
                # Tornar clicável
                card.vinculo_widget.mousePressEvent = lambda event: self.mostrar_opcoes_dependentes(
                    dados, outros_dependentes
                )
                card.vinculo_widget.setCursor(Qt.PointingHandCursor)
                
    def mostrar_opcoes_dependentes(self, dados_atual, outros_dependentes):
        """Mostra opções para navegar entre dependentes"""
        nomes = [dep["nome"] for dep in outros_dependentes]
        # Criar botões com texto padronizado para evitar corte
        botoes_dependentes = [f"Ver Dependente {i+1}" for i in range(len(outros_dependentes))]
        
        escolha = show_custom(
            self,
            f"🔗 Dependentes Vinculados - {dados_atual['nome']}",
            f"Este aluno está vinculado aos seguintes dependentes:\n\n" + 
            "\n".join([f"• {nome}" for nome in nomes]) +
            "\n\nQual dependente deseja visualizar?",
            tuple(botoes_dependentes + ["Cancelar"])
        )
        
        if escolha != "Cancelar":
            # Encontrar o dependente escolhido pelo índice do botão
            for i, botao in enumerate(botoes_dependentes):
                if escolha == botao:
                    dep = outros_dependentes[i]
                    
                    # Verificar o contexto atual para decidir a ação
                    termo_busca = self.busca.text().lower().strip()
                    
                    if termo_busca == "todos":
                        # Se está na tela "todos", tentar selecionar o dependente
                        try:
                            self.selecionar_card(dep)
                        except:
                            # Se falhar, fazer busca pelo nome como fallback
                            self.busca.setText(dep["nome"])
                            self.buscar()
                    else:
                        # Se está em busca específica, buscar pelo nome do dependente
                        self.busca.setText(dep["nome"])
                        self.buscar()
                    break

    def editar(self):
        if not self.aluno_atual:
            show_warning(self, "Erro", "Nenhum aluno selecionado!")
            return
        
        # Abrir dialog de edição
        dialog = EdicaoAlunoDialog(self, self.aluno_atual)
        if dialog.exec():
            # Se salvou as alterações, recarregar dados
            self.carregar_dados()
            # Refazer busca para manter resultado
            termo_atual = self.busca.text()
            if termo_atual:
                self.buscar()
            else:
                self.esconder_cards()

    def _btn(self, text):
        """Cria um botão com estilo padrão"""
        btn = QPushButton(text)
        btn.setFixedHeight(36)
        btn.setStyleSheet("""
            QPushButton {
                background:#cc1e1e;color:white;border-radius:10px;
                padding:8px 16px;font-weight:bold;font-size:11px;
            }
            QPushButton:hover { background:#e02020; }
        """)
        btn.setVisible(False)
        return btn

    def _toggle_acoes(self, show):
        """Mostra/esconde botões de ação"""
        self.btn_edit.setVisible(show)
        self.btn_toggle.setVisible(show)
        self.btn_del.setVisible(show)
        self.btn_ficha.setVisible(show)

# ================= DIALOG DE EDIÇÃO =================
class EdicaoAlunoDialog(QDialog):
    def __init__(self, parent, dados_aluno):
        super().__init__(parent)
        self.dados_aluno = dados_aluno
        self.foto_path = dados_aluno.get("foto", "")
        self.certificado_path = ""
        self.biometria_data = None
        
        # Listas de faixas
        self.faixas_adulto = ["Branca", "Azul", "Roxa", "Marrom", "Preta"]
        self.faixas_kids = [
            "Branca",
            "Cinza c/b", "Cinza", "Cinza c/p",
            "Amarela c/b", "Amarela", "Amarela c/p", 
            "Laranja c/b", "Laranja", "Laranja c/p",
            "Verde c/b", "Verde", "Verde c/p"
        ]
        
        self.setup_ui()
        self.preencher_dados()
        
    def carregar_planos_edicao(self):
        """Carrega planos do banco de dados para edição"""
        try:
            plano_atual = self.plano.currentText() if hasattr(self, 'plano') else ""
            self.plano.clear()
            
            # Importar aqui para evitar imports circulares
            from database.db import get_planos_formatados
            planos = get_planos_formatados()
            self.plano.addItems(planos)
            
            # Restaurar seleção anterior se existir
            if plano_atual:
                index = self.plano.findText(plano_atual)
                if index >= 0:
                    self.plano.setCurrentIndex(index)
                else:
                    self.plano.setEditText(plano_atual)
                    
        except Exception as e:
            # Fallback para planos padrão em caso de erro
            self.plano.clear()
            self.plano.addItems([
                "Adulto - R$180",
                "Kids (5–13) - R$150", 
                "Plano Personalizado"
            ])
        
    def setup_ui(self):
        self.setWindowTitle(f"Editar Aluno")
        self.setModal(True)
        # Tamanho adaptado à tela (evita o rodapé ficar fora em telas menores)
        from PySide6.QtGui import QGuiApplication
        _scr = QGuiApplication.primaryScreen()
        _avail = _scr.availableGeometry() if _scr else None
        _w = min(760, (_avail.width() - 60) if _avail else 760)
        _h = min(860, (_avail.height() - 80) if _avail else 860)
        self.setMinimumSize(600, 420)
        self.resize(_w, _h)
        self.setObjectName("editDialog")
        self.setStyleSheet("""
            #editDialog { background: #111111; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(4)

        # Título
        title = QLabel("Editar Aluno")
        title.setStyleSheet(
            "color: #ffffff; font-size: 20px; font-weight: 700;"
            " background: transparent; border: none;"
            " font-family: 'Arial Black', sans-serif;"
        )
        main_layout.addWidget(title)
        subtitle = QLabel(self.dados_aluno['nome'])
        subtitle.setStyleSheet(
            "color: #a0a0a0; font-size: 11px; background: transparent; border: none; margin-bottom: 10px;"
        )
        main_layout.addWidget(subtitle)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { background: #111111; width: 6px; border-radius: 3px; }
            QScrollBar::handle:vertical { background: #333333; border-radius: 3px; min-height: 20px; }
            QScrollBar::handle:vertical:hover { background: #cc1e1e; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        form = QVBoxLayout(container)
        form.setSpacing(12)
        form.setAlignment(Qt.AlignTop)

        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addWidget(container)

        # -------- TAMANHOS --------
        LABEL_W = 120
        INPUT_W = 480
        SMALL_W = 200
        MINI_W = 210
        CPF_W = 270
        BTN_W = 150
        BTN_H = 36
        
        # -------- ESTILOS (iguais ao cadastro) --------
        def row(label_text, widget):
            h = QHBoxLayout()
            h.setSpacing(12)
            
            label = QLabel(label_text)
            label.setFixedWidth(LABEL_W)
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            label.setStyleSheet("color: #888888; font-size: 13px; background: transparent;")

            h.addWidget(label)
            h.addWidget(widget)
            h.addStretch()
            return h

        input_style = """
            QLineEdit, QDateEdit, QComboBox {
                background-color: #0e0e0e;
                padding: 7px 10px;
                border-radius: 6px;
                border: 1px solid #1e1e1e;
                font-size: 13px;
                color: #ffffff;
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
                border: 1px solid #cc1e1e;
            }
            QComboBox QAbstractItemView {
                background-color: #0e0e0e;
                border: 1px solid #1e1e1e;
                border-radius: 6px;
                selection-background-color: #cc1e1e;
                selection-color: white;
                padding: 5px;
                font-size: 13px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                background-color: #0e0e0e;
                color: #aaaaaa;
                padding: 8px 12px;
                margin: 1px;
                border-radius: 5px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #cc1e1e;
                color: white;
                font-weight: bold;
            }
        """
        
        def red_btn():
            return """
                QPushButton {
                    background-color: #cc1e1e;
                    color: white;
                    border-radius: 9px;
                    padding: 6px 10px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover { background-color: #e02020; }
            """
        
        def bio_btn():
            return """
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border-radius: 9px;
                    padding: 6px 10px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover { background-color: #0056b3; }
            """
        
        legenda = QLabel("* Campos obrigatórios")
        legenda.setStyleSheet(
            "color: #9a9a9a; font-size: 10px; background: transparent; border: none; margin-bottom: 4px;"
        )
        form.addWidget(legenda, alignment=Qt.AlignLeft)
        
        # -------- NOME --------
        self.nome = QLineEdit()
        self.nome.setPlaceholderText("Digite o nome completo *")
        self.nome.setFixedWidth(INPUT_W)
        self.nome.setStyleSheet(input_style)
        form.addLayout(row("Nome:", self.nome))
        
        # -------- CPF --------
        self.cpf = QLineEdit()
        self.cpf.setInputMask("000.000.000-00")
        self.cpf.setPlaceholderText("000.000.000-00")
        self.cpf.setFixedWidth(CPF_W)
        self.cpf.setStyleSheet(input_style)
        form.addLayout(row("CPF:", self.cpf))
        
        # -------- RESPONSÁVEL (se for kids) --------
        self.resp_wrap = QWidget()
        resp_layout = QVBoxLayout(self.resp_wrap)
        resp_layout.setContentsMargins(0, 0, 0, 0)
        resp_layout.setSpacing(12)
        
        self.resp_nome = QLineEdit()
        self.resp_nome.setPlaceholderText("Nome do responsável *")
        self.resp_nome.setFixedWidth(INPUT_W)
        self.resp_nome.setStyleSheet(input_style)
        resp_layout.addLayout(row("Resp. Nome:", self.resp_nome))
        
        self.resp_cpf = QLineEdit()
        self.resp_cpf.setInputMask("000.000.000-00")
        self.resp_cpf.setPlaceholderText("CPF do responsável *")
        self.resp_cpf.setFixedWidth(CPF_W)
        self.resp_cpf.setStyleSheet(input_style)
        resp_layout.addLayout(row("Resp. CPF:", self.resp_cpf))
        
        # Mostrar responsável apenas se for kids
        if self.dados_aluno["tipo"] == "kids":
            self.resp_wrap.setVisible(True)
        else:
            self.resp_wrap.setVisible(False)
            
        form.addWidget(self.resp_wrap)
        
        # -------- EMAIL --------
        self.email = QLineEdit()
        self.email.setPlaceholderText("exemplo@email.com (opcional)")
        self.email.setFixedWidth(INPUT_W)
        self.email.setStyleSheet(input_style)
        form.addLayout(row("E-mail:", self.email))
        
        # -------- TELEFONE --------
        self.telefone = QLineEdit()
        self.telefone.setInputMask("(00) 00000-0000")
        self.telefone.setPlaceholderText("(00) 00000-0000 *")
        self.telefone.setFixedWidth(MINI_W)
        self.telefone.setStyleSheet(input_style)
        form.addLayout(row("Telefone:", self.telefone))
        
        # -------- CEP --------
        self.cep = QLineEdit()
        self.cep.setInputMask("00000-000")
        self.cep.setPlaceholderText("00000-000 *")
        self.cep.setFixedWidth(SMALL_W)
        self.cep.setStyleSheet(input_style)
        form.addLayout(row("CEP:", self.cep))
        
        # -------- ENDEREÇO --------
        self.endereco = QLineEdit()
        self.endereco.setPlaceholderText("Rua, número, bairro *")
        self.endereco.setFixedWidth(INPUT_W)
        self.endereco.setStyleSheet(input_style)
        form.addLayout(row("Endereço:", self.endereco))
        
        # -------- NASCIMENTO --------
        self.data_input = QDateEdit()
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setDisplayFormat("dd/MM/yyyy")
        self.data_input.setFixedWidth(SMALL_W)
        self.data_input.setStyleSheet(input_style)
        form.addLayout(row("Nascimento:", self.data_input))
        
        # -------- FAIXA / GRAU --------
        self.faixa = QComboBox()
        if self.dados_aluno["tipo"] == "adulto":
            self.faixa.addItems(self.faixas_adulto)
        else:
            self.faixa.addItems(self.faixas_kids)
        self.faixa.setFixedWidth(MINI_W)
        self.faixa.setStyleSheet(input_style)
        
        self.grau = QComboBox()
        self.grau.addItems(["Sem grau", "1 Grau", "2 Graus", "3 Graus", "4 Graus"])
        self.grau.setFixedWidth(MINI_W)
        self.grau.setStyleSheet(input_style)
        
        fw = QWidget()
        fw.setFixedWidth(INPUT_W)
        fl = QHBoxLayout(fw)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(12)
        fl.addWidget(self.faixa)
        fl.addWidget(self.grau)
        form.addLayout(row("Faixa / Grau:", fw))
        
        # -------- PESO / ALTURA --------
        self.peso = QLineEdit()
        self.peso.setPlaceholderText("Peso (kg)")
        self.peso.setFixedWidth(MINI_W)
        self.peso.setStyleSheet(input_style)
        
        self.altura = QLineEdit()
        self.altura.setPlaceholderText("Altura (cm)")
        self.altura.setFixedWidth(MINI_W)
        self.altura.setStyleSheet(input_style)
        
        pw = QWidget()
        pw.setFixedWidth(INPUT_W)
        pl = QHBoxLayout(pw)
        pl.setContentsMargins(0, 0, 0, 0)
        pl.setSpacing(12)
        pl.addWidget(self.peso)
        pl.addWidget(self.altura)
        form.addLayout(row("Peso / Altura:", pw))
        
        # -------- PLANO --------
        self.plano = QComboBox()
        self.plano.setEditable(True)
        self.carregar_planos_edicao()  # Carrega planos dinâmicos
        self.plano.setFixedWidth(INPUT_W)
        self.plano.setStyleSheet(input_style)
        self.plano.currentTextChanged.connect(self.toggle_plano_personalizado_edicao)
        form.addLayout(row("Plano:", self.plano))

        # Valor do plano personalizado (aparece só quando "Plano Personalizado")
        self.valor_personalizado = QLineEdit()
        self.valor_personalizado.setPlaceholderText("Digite o valor (ex: 99.90)")
        self.valor_personalizado.setFixedWidth(INPUT_W)
        self.valor_personalizado.setStyleSheet(input_style)
        self.valor_plano_wrap = QWidget()
        self.valor_plano_wrap.setStyleSheet("background: transparent;")
        _vpl = QHBoxLayout(self.valor_plano_wrap)
        _vpl.setContentsMargins(0, 0, 0, 0)
        _vpl.addLayout(row("Valor do Plano:", self.valor_personalizado))
        form.addWidget(self.valor_plano_wrap)
        self.valor_plano_wrap.setVisible(False)

        # Botão vincular a responsável (para adultos)
        self.btn_vincular_edicao = QPushButton("Vincular a Responsável")
        self.btn_vincular_edicao.setFixedHeight(34)
        self.btn_vincular_edicao.setCursor(Qt.PointingHandCursor)
        self.btn_vincular_edicao.setStyleSheet("""
            QPushButton {
                background: transparent; color: #b0b0b0;
                border: 1px solid #2a2a2a; border-radius: 7px;
                font-size: 12px; font-weight: 500; padding: 0 16px;
            }
            QPushButton:hover { color: #ffffff; border-color: #444444; background: #1a1a1a; }
        """)
        self.btn_vincular_edicao.clicked.connect(self.vincular_responsavel_edicao)
        self.btn_vincular_edicao.setVisible(self.dados_aluno.get("tipo") == "adulto")
        _vinc_row = QHBoxLayout()
        _vinc_row.addStretch()
        _vinc_row.addWidget(self.btn_vincular_edicao)
        form.addLayout(_vinc_row)

        # -------- ARQUIVOS & BIOMETRIA --------
        self.foto_label = QLabel()
        self.foto_label.setObjectName("fotoLabel")
        self.foto_label.setFixedSize(70, 70)
        self.foto_label.setStyleSheet("""
            #fotoLabel {
                background: #161616;
                border-radius: 6px;
                border: 1px solid #222222;
                color: #a0a0a0;
            }
        """)
        self.foto_label.setAlignment(Qt.AlignCenter)
        self.foto_label.setText("👤\nSem foto")
        self.foto_label.setScaledContents(True)
        
        btn_foto = QPushButton("📁 Selecionar Foto")
        btn_foto.setFixedSize(BTN_W + 20, BTN_H)
        btn_foto.setStyleSheet(red_btn())
        btn_foto.clicked.connect(self.selecionar_foto)
        
        btn_cert = QPushButton("📄 Certificado")
        btn_cert.setFixedSize(BTN_W, BTN_H)
        btn_cert.setStyleSheet(red_btn())
        btn_cert.clicked.connect(self.selecionar_certificado)
        
        # Status de biometria
        self.bio_status = QLabel("Sem biometria")
        self.bio_status.setObjectName("bioStatus")
        self.bio_status.setStyleSheet("""
            #bioStatus {
                background: rgba(204,30,30,0.1);
                color: #c04444;
                padding: 4px 8px;
                border-radius: 5px;
                font-size: 11px;
                border: none;
            }
        """)
        
        btn_bio = QPushButton("👆 Cadastrar Biometria")
        btn_bio.setFixedSize(BTN_W + 30, BTN_H)
        btn_bio.setStyleSheet(bio_btn())
        btn_bio.clicked.connect(self.cadastrar_biometria)
        
        btn_remove_bio = QPushButton("🗑️ Remover")
        btn_remove_bio.setFixedSize(80, BTN_H)
        btn_remove_bio.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border-radius: 6px;
                padding: 4px 8px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover { background-color: #c82333; }
        """)
        btn_remove_bio.clicked.connect(self.remover_biometria)
        
        # Widget arquivos
        aw = QWidget()
        al = QVBoxLayout(aw)
        al.setContentsMargins(0, 0, 0, 0)
        al.setSpacing(8)
        
        # Primeira linha: foto, botões de arquivo
        primeira_linha = QHBoxLayout()
        primeira_linha.setSpacing(10)
        primeira_linha.addWidget(self.foto_label)
        primeira_linha.addWidget(btn_foto)
        primeira_linha.addWidget(btn_cert)
        primeira_linha.addStretch()
        
        # Segunda linha: biometria
        segunda_linha = QHBoxLayout()
        segunda_linha.setSpacing(10)
        segunda_linha.addWidget(self.bio_status)
        segunda_linha.addWidget(btn_bio)
        segunda_linha.addWidget(btn_remove_bio)
        segunda_linha.addStretch()
        
        al.addLayout(primeira_linha)
        al.addLayout(segunda_linha)
        
        form.addLayout(row("Arquivos:", aw))
        
        # -------- BOTÕES --------
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        btn_cancelar_edicao = QPushButton("Cancelar")
        btn_cancelar_edicao.setFixedSize(120, 38)
        btn_cancelar_edicao.setStyleSheet("""
            QPushButton {
                background: #1e1e1e; color: #888888;
                border: 1px solid #2a2a2a; border-radius: 7px;
                font-size: 12px; font-weight: 500;
            }
            QPushButton:hover { background: #252525; color: #cccccc; }
        """)
        btn_cancelar_edicao.clicked.connect(self.cancelar_edicao)

        btn_salvar = QPushButton("Salvar Alterações")
        btn_salvar.setFixedSize(160, 38)
        btn_salvar.setStyleSheet("""
            QPushButton {
                background: #cc1e1e; color: #ffffff;
                border: none; border-radius: 7px;
                font-size: 12px; font-weight: 600;
            }
            QPushButton:hover  { background: #e02020; }
            QPushButton:pressed{ background: #a01515; }
        """)
        btn_salvar.clicked.connect(self.salvar)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancelar_edicao)
        btn_layout.addWidget(btn_salvar)

        # Conteúdo rolável (formulário) e rodapé fixo com os botões,
        # para que "Salvar" fique sempre visível.
        scroll_area.setWidget(wrapper)
        main_layout.addWidget(scroll_area, 1)
        main_layout.addLayout(btn_layout)
        
    def preencher_dados(self):
        """Preenche os campos com os dados atuais do aluno"""
        dados = self.dados_aluno
        
        # Dados pessoais
        self.nome.setText(dados.get("nome", ""))
        self.cpf.setText(dados.get("cpf", ""))
        self.email.setText(dados.get("email", ""))
        self.telefone.setText(dados.get("telefone", ""))
        self.cep.setText(dados.get("cep", ""))
        self.endereco.setText(dados.get("endereco", ""))
        
        # Data de nascimento
        if dados.get("data_nascimento"):
            from datetime import datetime
            try:
                dt = datetime.strptime(dados["data_nascimento"], "%Y-%m-%d")
                self.data_input.setDate(QDate(dt.year, dt.month, dt.day))
            except:
                pass
        
        # Dados do responsável (se for kids)
        if dados["tipo"] == "kids":
            self.resp_nome.setText(dados.get("responsavel", ""))
            self.resp_cpf.setText(dados.get("responsavel_cpf", ""))
        
        # Academia
        faixa = dados.get("faixa", "")
        if faixa:
            index = self.faixa.findText(faixa)
            if index >= 0:
                self.faixa.setCurrentIndex(index)
        
        # Grau - agora é QComboBox
        grau = dados.get("grau", "Sem grau")
        # Converter valores antigos para o novo formato
        if grau == "0" or grau == "":
            grau = "Sem grau"
        elif grau.isdigit():
            if grau == "1":
                grau = "1 Grau"
            else:
                grau = f"{grau} Graus"
        
        index = self.grau.findText(str(grau))
        if index >= 0:
            self.grau.setCurrentIndex(index)
        else:
            self.grau.setCurrentIndex(0)  # Default para "Sem grau"
            
        self.peso.setText(dados.get("peso", ""))
        self.altura.setText(dados.get("altura", ""))
        
        # Plano
        plano = dados.get("plano", "")
        if plano:
            index = self.plano.findText(plano)
            if index >= 0:
                self.plano.setCurrentIndex(index)
            else:
                self.plano.setEditText(plano)
        
        # Foto
        if dados.get("foto") and os.path.exists(dados["foto"]):
            pixmap = QPixmap(dados["foto"])
            if not pixmap.isNull():
                self.foto_label.setPixmap(pixmap.scaled(
                    70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))
            self.foto_path = dados["foto"]
        
    def selecionar_foto(self):
        """Escolhe foto do aluno"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Escolher Foto",
            "",
            "Imagens (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.foto_label.setPixmap(pixmap.scaled(
                    70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))
                self.foto_path = file_path
            else:
                show_error(self, "Erro", "Arquivo de imagem inválido!")
                
    def selecionar_certificado(self):
        """Escolhe certificado do aluno"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Escolher Certificado",
            "",
            "Documentos (*.pdf *.jpg *.jpeg *.png)"
        )
        
        if file_path:
            self.certificado_path = file_path
            show_info(self, "Sucesso", f"📄 Certificado selecionado: {os.path.basename(file_path)}")
            
    def cadastrar_biometria(self):
        """Simula cadastro de biometria"""
        resultado = show_question(
            self,
            "Cadastrar Biometria",
            "📱 Conecte o leitor biométrico e posicione o dedo.\n\nSimular cadastro de biometria?",
            "Sim", "Cancelar"
        )
        
        if resultado:
            import random
            self.biometria_data = {
                "template": f"BIO_{random.randint(1000,9999)}",
                "quality": random.randint(85, 98)
            }
            
            self.bio_status.setText(f"✅ Biometria {self.biometria_data['quality']}%")
            self.bio_status.setStyleSheet("""
                QLabel {
                    background: rgba(40,167,69,0.1);
                    color: #28a745;
                    padding: 4px 8px;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: bold;
                    margin: 2px;
                }
            """)
            
            show_info(self, "Sucesso", f"🎉 Biometria cadastrada!\n\nQualidade: {self.biometria_data['quality']:.0f}%")
            
    def remover_biometria(self):
        """Remove biometria cadastrada"""
        if self.biometria_data:
            resultado = show_question(
                self,
                "Remover Biometria",
                "⚠️ Remover a biometria cadastrada?",
                "Sim", "Não"
            )
            
            if resultado:
                self.biometria_data = None
                self.bio_status.setText("❌ Sem biometria")
                self.bio_status.setStyleSheet("""
                    QLabel {
                        background: rgba(220,53,69,0.1);
                        color: #dc3545;
                        padding: 4px 8px;
                        border-radius: 6px;
                        font-size: 11px;
                        font-weight: bold;
                        margin: 2px;
                    }
                """)
                show_info(self, "Removido", "🗑️ Biometria removida!")
        else:
            show_info(self, "Aviso", "ℹ️ Não há biometria cadastrada.")
            
    def validar_campos(self):
        """Valida todos os campos obrigatórios"""
        erros = []
        
        if not self.nome.text().strip():
            erros.append("• Nome é obrigatório")
            
        # Para adultos, CPF é obrigatório
        if self.dados_aluno["tipo"] == "adulto":
            if not self.cpf.text().strip():
                erros.append("• CPF é obrigatório")
            elif len(self.cpf.text().replace(".", "").replace("-", "").replace(" ", "")) != 11:
                erros.append("• CPF deve ter 11 dígitos")
        # Para kids, CPF é opcional (igual ao cadastro)
            
        if not self.telefone.text().strip():
            erros.append("• Telefone é obrigatório")
            
        if not self.cep.text().strip():
            erros.append("• CEP é obrigatório")
            
        if not self.endereco.text().strip():
            erros.append("• Endereço é obrigatório")
            
        if not self.grau.currentText().strip():
            erros.append("• Grau é obrigatório")
            
        if not self.plano.currentText().strip():
            erros.append("• Plano é obrigatório")
            
        # Campos específicos para kids (apenas responsável obrigatório)
        if self.dados_aluno["tipo"] == "kids":
            if not self.resp_nome.text().strip():
                erros.append("• Nome do responsável é obrigatório")
                
            if not self.resp_cpf.text().strip():
                erros.append("• CPF do responsável é obrigatório")
            elif len(self.resp_cpf.text().replace(".", "").replace("-", "").replace(" ", "")) != 11:
                erros.append("• CPF do responsável deve ter 11 dígitos")
        
        return erros
        
    def verificar_duplicatas(self):
        """Verifica CPFs duplicados"""
        erros = []
        
        cpf = self.cpf.text().replace(".", "").replace("-", "").replace(" ", "")
        
        if self.dados_aluno["tipo"] == "adulto":
            if cpf_existe(cpf, self.dados_aluno["id"]):
                erros.append("• CPF já está cadastrado para outro aluno adulto")
        else:
            # Para kids, só verifica CPF se foi preenchido (igual ao cadastro)
            if cpf and cpf_kid_existe(cpf, self.dados_aluno["id"]):
                erros.append("• CPF já está cadastrado para outra criança")
                
        email = self.email.text().strip()
        if email and self.dados_aluno["tipo"] == "adulto":
            if email_existe(email, self.dados_aluno["id"]):
                erros.append("• Email já está cadastrado para outro aluno")
                    
        return erros
        
    def toggle_plano_personalizado_edicao(self, texto):
        """Mostra o campo de valor quando o plano é 'Plano Personalizado'."""
        if hasattr(self, "valor_plano_wrap"):
            self.valor_plano_wrap.setVisible(texto == "Plano Personalizado")

    def vincular_responsavel_edicao(self):
        """Vincula este aluno (o que está sendo editado) a um responsável.

        Não pede o CPF do dependente — é o próprio aluno em edição.
        """
        from utils.vincular_utils import vincular_dependente
        if vincular_dependente(self, self.dados_aluno.get("id"), self.dados_aluno.get("nome")):
            self.accept()

    def salvar(self):
        """Salva as alterações"""
        erros_validacao = self.validar_campos()
        if erros_validacao:
            show_error(self, "Campos Obrigatórios", "\n".join(erros_validacao))
            return
            
        erros_duplicata = self.verificar_duplicatas()
        if erros_duplicata:
            show_error(self, "Dados Duplicados", "\n".join(erros_duplicata))
            return
            
        try:
            nome = self.nome.text().strip()
            cpf = self.cpf.text().replace(".", "").replace("-", "").replace(" ", "")
            email = self.email.text().strip()
            telefone = self.telefone.text().strip()
            cep = self.cep.text().strip()
            endereco = self.endereco.text().strip()
            data_nasc = self.data_input.date().toString("yyyy-MM-dd")
            faixa = self.faixa.currentText()
            grau = self.grau.currentText().strip()
            peso = self.peso.text().strip()
            altura = self.altura.text().strip()
            plano = self.plano.currentText().strip()
            if plano == "Plano Personalizado":
                valor = self.valor_personalizado.text().strip()
                if not valor:
                    show_error(self, "Plano personalizado", "Informe o valor do plano personalizado.")
                    return
                plano = f"Personalizado - R${valor}"

            import json
            biometria_json = json.dumps(self.biometria_data) if self.biometria_data else None
            
            if self.dados_aluno["tipo"] == "adulto":
                atualizar_aluno(
                    self.dados_aluno["id"],
                    nome, cpf, email, telefone, cep, endereco, data_nasc,
                    faixa, grau, peso, altura, plano,
                    self.foto_path, self.certificado_path,
                    biometria_json
                )
                # Ao trocar o plano, atualiza as mensalidades pendentes (mês atual em diante)
                atualizar_mensalidades_por_plano(self.dados_aluno["id"], plano)
            else:
                resp_nome = self.resp_nome.text().strip()
                resp_cpf = self.resp_cpf.text().replace(".", "").replace("-", "").replace(" ", "")
                
                atualizar_kid(
                    self.dados_aluno["id"],
                    nome, cpf, resp_nome, resp_cpf, email, telefone, cep, endereco, data_nasc,
                    faixa, grau, peso, altura, plano,
                    self.foto_path, self.certificado_path,
                    biometria_json
                )
                # Ao trocar o plano, atualiza as mensalidades pendentes (kids: id negativo)
                atualizar_mensalidades_por_plano(-self.dados_aluno["id"], plano)
            
            show_info(self, "Sucesso", f"✅ Aluno {nome} atualizado com sucesso!")
            self.accept()
            
        except Exception as e:
            show_error(self, "Erro", f"Erro ao salvar: {str(e)}")

    def vincular_responsavel(self):
        """Vincula um aluno existente a um responsável (usando função utilitária)"""
        from utils.vincular_utils import vincular_dependente

        if vincular_dependente(self, self.dados_aluno.get("id"), self.dados_aluno.get("nome")):
            # Recarregar dados
            self.load()

    def cancelar_edicao(self):
        """Cancela a edição com confirmação se houver alterações"""
        resultado = show_question(
            self,
            "Cancelar Edição",
            "⚠️ Tem certeza que deseja cancelar a edição?\n\nTodas as alterações não salvas serão perdidas.",
            "Sim, Cancelar", "Não"
        )
        
        if resultado:
            show_info(self, "Edição Cancelada", "✅ Edição cancelada. Nenhuma alteração foi salva.")
            self.reject()
