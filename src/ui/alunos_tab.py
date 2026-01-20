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
from database.db import listar_alunos, inativar_aluno, excluir_aluno, listar_todos_alunos, atualizar_aluno, cpf_existe, email_existe
from database.kids_db import get_conn, atualizar_kid, cpf_kid_existe
from ui.app_dialog import show_info, show_warning, show_error, show_question, show_custom

# ================= ESTILOS CSS =================
campo_nome_style = """
QLabel {
    background: rgba(255,255,255,0.95);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
    font-weight: bold;
    color: #333;
    border: 1px solid rgba(255,255,255,0.7);
}
"""

campo_style = """
QLabel {
    background: rgba(255,255,255,0.9);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 11px;
    color: #444;
    border: 1px solid rgba(255,255,255,0.5);
    margin: 1px;
}
"""

# ================= CARD CRACHÁ =================
class AlunoCard(QFrame):
    def __init__(self):
        super().__init__()
        self.dados = None
        self.build_ui()

    def build_ui(self):
        self.setFixedSize(480, 320)  # Aumentado de 450x320 para 480x320 para melhor visualização
        self.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.1);
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.3);
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
        self.foto.setFixedSize(80, 80)  # Menor
        self.foto.setStyleSheet("""
            QLabel {
                background: rgba(255,255,255,0.9);
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.5);
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
                font-weight:bold;
                font-size:10px;
                border-radius:6px;
                padding:2px 6px;
                background:#0f5132;
                color:#00ff99;
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
        
        col1.addWidget(self.lbl_cpf)
        col1.addWidget(self.lbl_email)
        col1.addWidget(self.lbl_telefone)
        col1.addWidget(self.lbl_faixa)
        
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
        
        col2.addWidget(self.lbl_endereco)
        col2.addWidget(self.lbl_nascimento)
        col2.addWidget(self.lbl_plano)
        col2.addWidget(self.lbl_resp)
        
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
        
        self.lbl_plano.setText(f"💳 {dados['plano']}")

        # Responsável
        if dados.get("responsavel"):
            resp_info = f"👨‍👩‍👧‍👦 {dados['responsavel']}"
            if dados.get("responsavel_cpf"):
                resp_info += f" - {dados['responsavel_cpf']}"
            self.lbl_resp.setText(resp_info)
            self.lbl_resp.show()
        else:
            self.lbl_resp.hide()

        # Status
        if dados["status"]:
            self.status.setText("ATIVO")
            self.status.setStyleSheet("""
                QLabel { background:#0f5132;color:#00ff99;
                        border-radius:8px;padding:4px;font-weight:bold;font-size:10px;}
            """)
        else:
            self.status.setText("INATIVO")
            self.status.setStyleSheet("""
                QLabel { background:#5a1a1a;color:#ff6666;
                        border-radius:8px;padding:4px;font-weight:bold;font-size:10px;}
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
                self.foto.setText("🗄\nSem foto")
                self.foto.setStyleSheet(self.foto.styleSheet() + "color: #999; font-size: 11px; text-align: center;")
        else:
            self.foto.clear()
            self.foto.setText("🗄\nSem foto")
            self.foto.setStyleSheet(self.foto.styleSheet() + "color: #999; font-size: 11px; text-align: center;")
            
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
                    color: #e50914;
                    border: 1px dashed #e50914;
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
        self.build_ui()
        self.carregar_dados()

    # ---------------- UI ----------------

    def build_ui(self):
        # Usa o layout da BaseTab que já tem background
        root = self.layout()
        
        # Forçar margens mínimas para busca ficar no topo absoluto
        self.content_layout.setContentsMargins(15, 10, 15, 15)  # Margem superior bem pequena
        root.setSpacing(5)  # Espaçamento mínimo entre elementos

        # TÍTULO - no topo
        titulo = QLabel("Alunos")
        titulo.setStyleSheet("color:white;font-size:24px;font-weight:bold;margin:0px;padding:0px;")
        root.addWidget(titulo)

        # BUSCA - imediatamente após o título (sem espaçamento extra)
        busca_row = QHBoxLayout()
        busca_row.setSpacing(10)
        busca_row.setContentsMargins(0, 3, 0, 0)  # Margem mínima

        # Container para centralizar e limitar largura da busca
        busca_container = QWidget()
        busca_container.setMaximumWidth(600)  # Limitar largura máxima
        busca_container_layout = QHBoxLayout(busca_container)
        busca_container_layout.setContentsMargins(0, 0, 0, 0)
        busca_container_layout.setSpacing(10)

        self.busca = QLineEdit()
        self.busca.setPlaceholderText("🔍 Pesquisar: Nome, CPF, responsável ou digite 'todos' para listar todos")
        self.busca.setFixedHeight(40)
        self.busca.setStyleSheet("""
            QLineEdit {
                background:white;
                border-radius:14px;
                padding:10px 14px;
                font-size:13px;
                margin:0px;
                color: #222222;
                font-weight: 500;
            }
            QLineEdit::placeholder {
                color: #888888;
                font-style: italic;
            }
        """)

        btn_buscar = QPushButton("Buscar")
        btn_buscar.setFixedSize(120, 40)
        btn_buscar.setStyleSheet("""
            QPushButton {
                background:#e50914;color:white;border-radius:12px;
                font-weight:bold;
                margin:0px;
            }
            QPushButton:hover { background:#ff1a24; }
        """)
        btn_buscar.clicked.connect(self.buscar)

        busca_container_layout.addWidget(self.busca, 1)
        busca_container_layout.addWidget(btn_buscar)
        
        # Centralizar o container de busca
        busca_row.addStretch()
        busca_row.addWidget(busca_container)
        busca_row.addStretch()
        
        root.addLayout(busca_row)
        
        # Espaço antes do card
        root.addSpacing(15)

        # Área para cards (centralizada robustamente)
        self.cards_area = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_area)  # VBox para melhor controle
        self.cards_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)  # Topo e centro horizontal
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        
        root.addWidget(self.cards_area, 0)  # Não expandir verticalmente

        # -------- BOTÕES --------
        self.btns = QHBoxLayout()

        self.btn_edit = self._btn("Editar")
        self.btn_toggle = self._btn("Ativar / Inativar")
        self.btn_del = self._btn("Excluir")

        self.btn_edit.clicked.connect(self.editar)
        self.btn_toggle.clicked.connect(self.toggle_status)
        self.btn_del.clicked.connect(self.excluir)

        self.btns.addStretch()
        self.btns.addWidget(self.btn_edit)
        self.btns.addWidget(self.btn_toggle)
        self.btns.addWidget(self.btn_del)
        self.btns.addStretch()

        root.addLayout(self.btns)
        
        # Adicionar stretch no final para empurrar conteúdo para cima
        root.addStretch()  # Empurra todo conteúdo para cima
        
        self._toggle_acoes(False)

    def _btn(self, text):
        b = QPushButton(text)
        b.setFixedSize(160, 42)
        b.setStyleSheet("""
            QPushButton {
                background:#e50914;color:white;border-radius:14px;
                font-weight:bold;
            }
            QPushButton:hover { background:#ff1a24; }
        """)
        return b

    def _toggle_acoes(self, show):
        self.btn_edit.setVisible(show)
        self.btn_toggle.setVisible(show)
        self.btn_del.setVisible(show)

    # ---------------- DADOS ----------------

    def load(self):
        """Método para recarregar dados - usado como callback de refresh"""
        self.carregar_dados()
        # Limpar busca e esconder cards se estiverem visíveis
        self.busca.clear()
        self.esconder_cards()

    def carregar_dados(self):
        self.registros.clear()

        for a in listar_todos_alunos():  # Agora lista TODOS (ativos e inativos)
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
                "status": a[15],      # ativo
            })

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM kids")  # Kids já lista todos
        kids = cur.fetchall()
        conn.close()

        for k in kids:
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
            titulo_adultos.setStyleSheet("color:#e50914;font-size:14px;font-weight:bold;margin:10px 0px 5px 0px;")
            scroll_layout.addWidget(titulo_adultos)
            
            for aluno in adultos:
                item = self.criar_item_lista(aluno)
                scroll_layout.addWidget(item)
        
        if kids:
            # Seção Kids
            titulo_kids = QLabel(f"🧒 KIDS ({len(kids)})")
            titulo_kids.setStyleSheet("color:#e50914;font-size:14px;font-weight:bold;margin:10px 0px 5px 0px;")
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
                background:#e50914;color:white;border-radius:8px;
                padding:8px 20px;font-weight:bold;
            }
            QPushButton:hover { background:#ff1a24; }
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
        nome_label.setStyleSheet("font-size:13px;font-weight:bold;color:#333;")
        
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

    def mostrar_hierarquia_familiar(self, responsavel, dependentes):
        """Mostra responsável em cima centralizado e dependentes embaixo como organograma"""
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
        layout_principal.setSpacing(30)  # Espaço maior entre níveis
        layout_principal.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        
        # === RESPONSÁVEL NO TOPO ===
        layout_responsavel = QHBoxLayout()
        layout_responsavel.setAlignment(Qt.AlignHCenter)
        
        card_responsavel = AlunoCard()
        card_responsavel.set_dados(responsavel)
        card_responsavel.setVisible(True)
        # Adicionar seleção ao card responsável
        self.adicionar_selecao_card(card_responsavel, responsavel)
        
        # Adicionar indicador visual de que é o responsável
        card_responsavel.setStyleSheet(card_responsavel.styleSheet() + """
            QFrame {
                border: 2px solid #e50914;
                background: rgba(255,255,255,0.15);
            }
        """)
        
        layout_responsavel.addWidget(card_responsavel)
        layout_principal.addLayout(layout_responsavel)
        
        # === LINHA VISUAL DE CONEXÃO ===
        if dependentes:
            linha = QFrame()
            linha.setFrameShape(QFrame.HLine)
            linha.setFixedHeight(2)
            linha.setStyleSheet("background: #e50914; border: none;")
            layout_principal.addWidget(linha)
        
        # === DEPENDENTES EMBAIXO ===
        if dependentes:
            layout_dependentes = QHBoxLayout()
            layout_dependentes.setAlignment(Qt.AlignHCenter)
            layout_dependentes.setSpacing(20)
            
            for dependente in dependentes:
                card_dependente = AlunoCard()
                card_dependente.set_dados(dependente)
                card_dependente.setVisible(True)
                # Adicionar seleção ao card dependente
                self.adicionar_selecao_card(card_dependente, dependente)
                
                # Estilo diferenciado para dependentes
                card_dependente.setStyleSheet(card_dependente.styleSheet() + """
                    QFrame {
                        border: 1px solid rgba(255,200,0,0.6);
                        background: rgba(255,255,255,0.08);
                    }
                """)
                
                layout_dependentes.addWidget(card_dependente)
            
            layout_principal.addLayout(layout_dependentes)
        
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
                    border: 3px solid #e50914 !important;
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
        layout_horizontal.addStretch(1)  # Stretch à esquerda
        
        # Container do grid com largura fixa
        container_grid = QWidget()
        container_grid.setFixedWidth(960)  # Aumentado para acomodar cards de 450px
        container_grid.setStyleSheet("background: transparent;")
        
        # Layout em grid
        from PySide6.QtWidgets import QGridLayout
        grid = QGridLayout(container_grid)
        grid.setSpacing(25)  # Espaço entre cards
        grid.setAlignment(Qt.AlignCenter)
        grid.setContentsMargins(10, 10, 10, 10)
        
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
        
        # Verificar se algum adulto tem dependentes
        responsavel_com_dependentes = None
        dependentes = []
        
        for adulto in adultos_encontrados:
            # Procurar kids que têm este adulto como responsável
            kids_deste_adulto = []
            for registro in self.registros:
                if (registro["tipo"] == "kids" and 
                    registro.get("responsavel_cpf") == adulto["cpf"]):
                    kids_deste_adulto.append(registro)
            
            if kids_deste_adulto:
                responsavel_com_dependentes = adulto
                dependentes = kids_deste_adulto
                break
        
        if responsavel_com_dependentes and dependentes:
            # Mostrar hierarquia: responsável em cima, dependentes embaixo
            self.mostrar_hierarquia_familiar(responsavel_com_dependentes, dependentes)
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
                self.clear_layout(child.layout())
    
    def clear_layout(self, layout):
        """Limpa recursivamente um layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())
    
    def limpar_cards(self):
        """Remove todos os cards da tela (método legado)"""
        self.limpar_cards_completo()
    
    def esconder_cards(self):
        """Esconde a área dos cards"""
        self.cards_area.setVisible(False)
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
        layout_horizontal.addStretch(1)  # Stretch à esquerda
        
        # Container do grid com largura fixa
        container_grid = QWidget()
        container_grid.setFixedWidth(960)  # Aumentado para acomodar cards de 450px
        container_grid.setStyleSheet("background: transparent;")
        
        # Layout em grid
        from PySide6.QtWidgets import QGridLayout
        grid = QGridLayout(container_grid)
        grid.setSpacing(20)  # Espaçamento entre cards
        grid.setAlignment(Qt.AlignCenter)
        grid.setContentsMargins(10, 10, 10, 10)
        
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
        termo = self.busca.text().lower().strip()
        if not termo:
            return

        # SEMPRE limpar tudo primeiro
        self.esconder_cards()
        self.carregar_dados()

        # Se digitou "todos", mostrar todos os alunos em grid 2 colunas centralizado
        if termo == "todos":
            todos_alunos = sorted(self.registros, key=lambda x: x["nome"].lower())
            self.mostrar_todos_grid_centralizado(todos_alunos)
            return

        # Busca específica - procurar por nome, CPF ou responsável
        alunos_encontrados = []
        for r in self.registros:
            nome_match = termo in r["nome"].lower()
            cpf_match = termo in (r["cpf"] or "")
            resp_match = r.get("responsavel") and termo in r["responsavel"].lower()
            
            if nome_match or cpf_match or resp_match:
                alunos_encontrados.append(r)

        if alunos_encontrados:
            # Verificar se encontrou um responsável que tem dependentes
            self.organizar_resultado_hierarquico(alunos_encontrados)
        else:
            show_info(self, "Não encontrado", "Aluno não localizado.")
            self.esconder_cards()

    def toggle_status(self):
        if not self.aluno_atual:
            show_warning(self, "Erro", "Nenhum aluno selecionado!")
            return
            
        d = self.aluno_atual
        nome = d["nome"]
        status_atual = "ATIVO" if d["status"] else "INATIVO"
        novo_status_texto = "INATIVO" if d["status"] else "ATIVO"
        
        # REGRA DE NEGÓCIO: Verificar dependentes ao inativar responsável
        dependentes_afetados = []
        if d["tipo"] == "adulto" and d["status"]:  # Se está inativando um adulto que está ATIVO
            # Procurar dependentes deste responsável
            for registro in self.registros:
                if (registro["tipo"] == "kids" and 
                    registro.get("responsavel_cpf") == d["cpf"]):
                    dependentes_afetados.append(registro)
        
        # Confirmação diferenciada se há dependentes afetados
        if dependentes_afetados and novo_status_texto == "INATIVO":
            # ALERTA ESPECIAL PARA RESPONSÁVEL COM DEPENDENTES
            mensagem_dependentes = f"Este responsável possui {len(dependentes_afetados)} dependente(s).\n\n"
            mensagem_dependentes += "📋 IMPLICAÇÕES DA INATIVAÇÃO:\n"
            mensagem_dependentes += "• Os planos dos dependentes podem precisar ser ajustados\n"
            mensagem_dependentes += "• Considere transferir a responsabilidade para outro adulto\n"
            mensagem_dependentes += "• Ou revisar a situação financeira dos dependentes\n\n"
            mensagem_dependentes += "⚠️ Os dependentes permanecerão ATIVOS após esta inativação."
            
            # Confirmação simples com aviso
            if show_question(
                self,
                f"🚨 Inativação de Responsável - {nome}",
                mensagem_dependentes,
                "Inativar Responsável", "Cancelar"
            ):
                self.executar_inativacao(d)
                show_info(
                    self, 
                    "Responsável Inativado", 
                    f"✅ Responsável {nome} inativado.\n\n📝 Lembrete: Revisar planos dos {len(dependentes_afetados)} dependente(s)."
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
        
        # Recarregar dados e manter pesquisa
        termo_atual = self.busca.text()
        if termo_atual:
            self.buscar()
        else:
            self.esconder_cards()
    
    def executar_inativacao(self, dados_aluno):
        """Executa a inativação/ativação do aluno no banco de dados"""
        try:
            novo_status = 0 if dados_aluno["status"] else 1
            
            if dados_aluno["tipo"] == "adulto":
                # Alterar status no banco adultos
                inativar_aluno(dados_aluno["id"], novo_status)
            else:
                # Alterar status no banco kids
                conn = get_conn()
                cur = conn.cursor()
                cur.execute("UPDATE kids SET ativo=? WHERE id=?", (novo_status, dados_aluno["id"]))
                conn.commit()
                conn.close()
                
        except Exception as e:
            show_error(
                self, 
                "Erro", 
                f"Erro ao alterar status: {str(e)}"
            )

    def excluir(self):
        if not self.aluno_atual:
            show_warning(self, "Erro", "Nenhum aluno selecionado!")
            return
            
        d = self.aluno_atual
        nome = d["nome"]
        tipo = "Adulto" if d["tipo"] == "adulto" else "Criança"
        
        # Verificar se é responsável com dependentes
        tem_dependentes = False
        if d["tipo"] == "adulto":
            for registro in self.registros:
                if (registro["tipo"] == "kids" and 
                    registro.get("responsavel_cpf") == d["cpf"]):
                    tem_dependentes = True
                    break
        
        # Mensagem de confirmação mais detalhada
        mensagem = f"ATENÇÃO: Esta ação não pode ser desfeita!\n\n"
        mensagem += f"Aluno: {nome}\n"
        mensagem += f"Tipo: {tipo}\n"
        
        if tem_dependentes:
            mensagem += f"\n⚠️  CUIDADO: Este responsável possui dependentes cadastrados!\n"
            mensagem += f"A exclusão pode afetar os registros dos dependentes.\n"
        
        mensagem += f"\nDeseja realmente EXCLUIR este aluno?"
        
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
                # Excluir do banco kids
                conn = get_conn()
                cur = conn.cursor()
                cur.execute("DELETE FROM kids WHERE id=?", (d["id"],))
                conn.commit()
                conn.close()
            
            # Feedback de sucesso
            show_info(
                self, 
                "Sucesso", 
                f"Aluno {nome} foi excluído com sucesso!"
            )
            
            # Limpar seleção e esconder cards
            self.aluno_atual = None
            self.esconder_cards()
            
            # Se havia uma pesquisa, refazer para atualizar resultados
            termo_atual = self.busca.text()
            if termo_atual and termo_atual.lower() != "todos":
                self.buscar()
                
        except Exception as e:
            show_error(
                self, 
                "Erro", 
                f"Erro ao excluir aluno: {str(e)}"
            )

                
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
                background:#e50914;color:white;border-radius:10px;
                padding:8px 16px;font-weight:bold;font-size:11px;
            }
            QPushButton:hover { background:#ff1a24; }
        """)
        btn.setVisible(False)
        return btn

    def _toggle_acoes(self, show):
        """Mostra/esconde botões de ação"""
        self.btn_edit.setVisible(show)
        self.btn_toggle.setVisible(show)
        self.btn_del.setVisible(show)


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
        
    def setup_ui(self):
        self.setWindowTitle(f"Editar Aluno - {self.dados_aluno['nome']}")
        self.setModal(True)
        self.setFixedSize(950, 900)  # Tamanho aumentado para evitar cortes
        
        # Background igual ao das outras telas com logo
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e,
                    stop:1 #16213e
                );
                background-image: url({os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logobackground.png')});
                background-repeat: no-repeat;
                background-position: center center;
                background-attachment: fixed;
            }}
        """)
        
        # Layout principal 
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Título fixo no topo
        title = QLabel(f"✏️ Editar Aluno: {self.dados_aluno['nome']}")
        title.setStyleSheet("color:white;font-size:22px;font-weight:bold;")
        main_layout.addWidget(title, alignment=Qt.AlignLeft)
        
        # Área de scroll para o formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(255,255,255,0.1);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #e50914;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #ff1a24;
            }
        """)
        
        # Container centralizado igual ao cadastro
        container = QWidget()
        container.setMaximumWidth(760)
        
        form = QVBoxLayout(container)
        form.setSpacing(12)
        form.setAlignment(Qt.AlignTop)
        
        # Widget wrapper para centralizar o container  
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.addStretch()
        wrapper_layout.addWidget(container)
        wrapper_layout.addStretch()
        
        # -------- TAMANHOS (iguais ao cadastro) --------
        LABEL_W = 130
        INPUT_W = 420
        SMALL_W = 190
        MINI_W = 200
        CPF_W = 260
        BTN_W = 150
        BTN_H = 36
        
        # -------- ESTILOS (iguais ao cadastro) --------
        def row(label_text, widget):
            h = QHBoxLayout()
            h.setSpacing(12)
            
            label = QLabel(label_text)
            label.setFixedWidth(LABEL_W)
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            label.setStyleSheet("color: white; font-size: 13px;")
            
            h.addWidget(label)
            h.addWidget(widget)
            h.addStretch()
            return h
        
        input_style = """
            QLineEdit, QDateEdit, QComboBox {
                background-color: rgba(255,255,255,0.95);
                padding: 7px 10px;
                border-radius: 10px;
                border: 1.5px solid #ccc;
                font-size: 13px;
                color: #111;
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
                border: 1.5px solid #e50914;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #e50914;
                border-radius: 8px;
                selection-background-color: #e50914;
                selection-color: white;
                padding: 5px;
                font-size: 13px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                background-color: white;
                color: #333;
                padding: 8px 12px;
                margin: 1px;
                border-radius: 5px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #f8f9fa;
                color: #e50914;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #e50914;
                color: white;
                font-weight: bold;
            }
        """
        
        def red_btn():
            return """
                QPushButton {
                    background-color: #e50914;
                    color: white;
                    border-radius: 9px;
                    padding: 6px 10px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover { background-color: #ff1a24; }
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
        
        # -------- TÍTULO --------
        legenda = QLabel("* Campos obrigatórios")
        legenda.setStyleSheet("color:#ff6666;font-size:11px;font-style:italic;margin-bottom:10px;")
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
        self.plano.addItems([
            "Adulto - R$180",
            "Kids (5–13) - R$150", 
            "Família: 2 adultos - R$320",
            "Família: 1 adulto + 1 kids - R$300",
            "Família: 2 adultos + 1 kids - R$450",
            "Família: 1 adulto + 2 kids - R$430",
            "Família: 1 adulto + 3 kids - R$500",
            "Plano Personalizado",
            "Plano Bolsista (Patrocinado)"
        ])
        self.plano.setFixedWidth(INPUT_W)
        self.plano.setStyleSheet(input_style)
        form.addLayout(row("Plano:", self.plano))
        
        # -------- ARQUIVOS & BIOMETRIA --------
        self.foto_label = QLabel()
        self.foto_label.setFixedSize(70, 70)
        self.foto_label.setStyleSheet("""
            QLabel {
                background: rgba(255,255,255,0.1);
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.3);
                color: #999;
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
        self.bio_status = QLabel("❌ Sem biometria")
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
        
        btn_cancelar_edicao = QPushButton("Cancelar Edição")
        btn_cancelar_edicao.setFixedSize(160, 44)
        btn_cancelar_edicao.setStyleSheet(red_btn())
        btn_cancelar_edicao.clicked.connect(self.cancelar_edicao)
        
        btn_salvar = QPushButton("💾 Salvar Alterações")
        btn_salvar.setFixedSize(200, 44)
        btn_salvar.setStyleSheet(red_btn())
        btn_salvar.clicked.connect(self.salvar)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancelar_edicao)
        btn_layout.addWidget(btn_salvar)
        
        form.addLayout(btn_layout)
        
        # Adicionar wrapper centralizado ao scroll
        scroll_area.setWidget(wrapper)
        main_layout.addWidget(scroll_area)
        
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
            
            # Converter biometria para JSON se existir
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
                
            show_info(self, "Sucesso", f"✅ Aluno {nome} atualizado com sucesso!")
            self.accept()
            
        except Exception as e:
            show_error(self, "Erro", f"Erro ao salvar: {str(e)}")
            
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
