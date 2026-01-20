from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QDialog, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPalette, QBrush

from ui.base_tab import BaseTab
from database.db import listar_alunos, inativar_aluno, excluir_aluno, listar_todos_alunos
from database.kids_db import get_conn
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
        self.setFixedSize(450, 320)  # Aumentado de 420x300 para 450x320
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
                    background-color: rgba(52, 152, 219, 0.15);
                    color: #2980b9;
                    border: 1px dashed #3498db;
                    border-radius: 6px;
                    padding: 2px 6px;
                    font-size: 9px;
                    margin: 1px 0px;
                    max-height: 16px;
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
        show_info(self, "Em breve", "Tela de edição completa será o próximo passo.")

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
