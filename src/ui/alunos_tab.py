from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QMessageBox, QFrame, QDialog, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPalette, QBrush

from ui.base_tab import BaseTab
from database.db import listar_alunos, inativar_aluno, excluir_aluno
from database.kids_db import get_conn

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
        self.setFixedSize(400, 280)  # Tamanho fixo igual para todos os cards
        self.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.1);
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.3);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

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
        col1.setSpacing(4)
        
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
        col2.setSpacing(4)
        
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

        # Área para cards (centralizada)
        self.cards_area = QWidget()
        self.cards_layout = QHBoxLayout(self.cards_area)
        self.cards_layout.setAlignment(Qt.AlignCenter)
        self.cards_layout.setSpacing(20)
        
        # Container dos cards inicialmente vazio
        self.cards_container = QHBoxLayout()
        self.cards_container.setAlignment(Qt.AlignCenter)
        self.cards_container.setSpacing(20)
        
        self.cards_layout.addStretch()
        self.cards_layout.addLayout(self.cards_container)
        self.cards_layout.addStretch()
        
        root.addWidget(self.cards_area)

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

        for a in listar_alunos():
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
        cur.execute("SELECT * FROM kids")
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
        
        # Container principal
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        
        # Layout vertical para organizar responsável e dependentes
        layout_principal = QVBoxLayout(container)
        layout_principal.setSpacing(30)  # Espaço maior entre níveis
        layout_principal.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        
        # === RESPONSÁVEL NO TOPO ===
        layout_responsavel = QHBoxLayout()
        layout_responsavel.setAlignment(Qt.AlignHCenter)
        
        card_responsavel = AlunoCard()
        card_responsavel.set_dados(responsavel)
        card_responsavel.setVisible(True)
        
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
                
                # Estilo diferenciado para dependentes
                card_dependente.setStyleSheet(card_dependente.styleSheet() + """
                    QFrame {
                        border: 1px solid rgba(255,200,0,0.6);
                        background: rgba(255,255,255,0.08);
                    }
                """)
                
                layout_dependentes.addWidget(card_dependente)
            
            layout_principal.addLayout(layout_dependentes)
        
        # Adicionar à área de cards
        self.cards_layout.addWidget(container)
        
        # Mostrar área dos cards
        self.cards_area.setVisible(True)
        
        # Responsável como aluno atual para ações
        self.aluno_atual = responsavel
        self._toggle_acoes(True)

    def mostrar_todos_grid_centralizado(self, alunos_list):
        """Mostra todos os alunos em grid 2 colunas bem centralizado"""
        # Limpar completamente tudo
        self.limpar_cards_completo()
        
        # Container principal FIXO sem scroll desnecessário
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        
        # Layout em grid simples e centralizado
        from PySide6.QtWidgets import QGridLayout
        grid = QGridLayout(container)
        grid.setSpacing(25)  # Espaço maior e mais organizado
        grid.setAlignment(Qt.AlignCenter)  # Centralizado na tela
        grid.setContentsMargins(50, 20, 50, 20)  # Margens adequadas
        
        # Adicionar cards em grid 2 colunas
        row = 0
        col = 0
        
        for aluno in alunos_list:
            card = AlunoCard()
            card.set_dados(aluno)
            card.setVisible(True)
            
            grid.addWidget(card, row, col)
            
            col += 1
            if col >= 2:  # Máximo 2 colunas
                col = 0
                row += 1
        
        # Apenas adicionar scroll se REALMENTE necessário (muitos alunos)
        if len(alunos_list) > 8:  # Mais de 4 linhas
            scroll_area = QScrollArea()
            scroll_area.setStyleSheet("background: transparent; border: none;")
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setWidget(container)
            self.cards_layout.addWidget(scroll_area)
        else:
            # Direto sem scroll para poucos alunos
            self.cards_layout.addWidget(container)
        
        # Mostrar área dos cards
        self.cards_area.setVisible(True)
        
        # Primeiro aluno para ações
        if alunos_list:
            self.aluno_atual = alunos_list[0]
            self._toggle_acoes(True)

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
            
            # Adicionar no grid (2 colunas)
            grid.addWidget(card, row, col)
            
            col += 1
            if col >= 2:  # Máximo 2 colunas
                col = 0
                row += 1
        
        # Adicionar o container na área de cards
        self.cards_layout.addWidget(container)
        
        # Mostrar área dos cards
        self.cards_area.setVisible(True)
        
        # Atualizar botões de ação para o primeiro aluno
        if alunos_list:
            self.aluno_atual = alunos_list[0]
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
        
        # Recriar os stretches básicos
        self.cards_layout.addStretch()
        self.cards_layout.addStretch()
    
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
        
        # Container principal sem background
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        
        # Layout em grid
        from PySide6.QtWidgets import QGridLayout
        grid = QGridLayout(container)
        grid.setSpacing(15)  # Espaçamento entre cards
        grid.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        
        # Adicionar cards em grid 2 colunas
        row = 0
        col = 0
        
        for aluno in alunos_list:
            card = AlunoCard()
            card.set_dados(aluno)
            card.setVisible(True)
            
            # Adicionar no grid (2 colunas)
            grid.addWidget(card, row, col)
            
            col += 1
            if col >= 2:  # Máximo 2 colunas
                col = 0
                row += 1
        
        # Adicionar o container na área de cards
        self.cards_layout.addWidget(container)
        
        # Mostrar área dos cards
        self.cards_area.setVisible(True)
        
        # Atualizar botões de ação para o primeiro aluno
        if alunos_list:
            self.aluno_atual = alunos_list[0]
            self._toggle_acoes(True)

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
            QMessageBox.information(self, "Não encontrado", "Aluno não localizado.")
            self.esconder_cards()

    def toggle_status(self):
        if self.aluno_atual:
            d = self.aluno_atual
            novo = 0 if d["status"] else 1
            inativar_aluno(d["id"], novo)
            self.buscar()

    def excluir(self):
        if self.aluno_atual:
            d = self.aluno_atual
            if QMessageBox.question(self, "Confirmar", "Excluir aluno?") == QMessageBox.Yes:
                excluir_aluno(d["id"])
                self.esconder_cards()

    def editar(self):
        QMessageBox.information(self, "Em breve", "Tela de edição completa será o próximo passo.")

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
