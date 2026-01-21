import os
from datetime import date, datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, 
    QDateEdit, QDialog, QFormLayout, QLineEdit, QTextEdit, QMessageBox, 
    QFrame, QScrollArea, QTabWidget
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap, QFont

from ui.base_tab import BaseTab
from database.db import (
    listar_mensalidades, criar_mensalidade, marcar_mensalidade_paga,
    obter_mensalidades_pendentes, listar_alunos, get_conn
)
from ui.app_dialog import show_info, show_warning, show_error, show_question


class FinanceiroTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.mensalidade_atual = None  # Mensalidade selecionada
        self.mensalidades_selecionadas = []  # Lista de mensalidades selecionadas
        self.build_ui()
        self.load()
        
    @property
    def cards_layout(self):
        """Propriedade para compatibilidade - retorna layout da aba atual"""
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            content_widget = current_tab.widget()
            if content_widget:
                return content_widget.layout()
        return None

    def build_ui(self):
        layout = self.layout()  # Usa o layout já disponível do BaseTab
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Título principal
        title = QLabel("💰 Gestão Financeira")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Barra de ações
        actions_layout = QHBoxLayout()
        
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)

        # Filtros
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Status:", styleSheet="color: white; font-weight: bold;"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Todos", "PENDENTE", "PAGO"])
        self.status_filter.setStyleSheet("""
            QComboBox {
                background-color: rgba(255,255,255,0.95);
                padding: 7px 10px;
                border-radius: 10px;
                border: 1.5px solid #ccc;
                font-size: 13px;
                color: #111;
                min-width: 150px;
            }
            QComboBox:focus {
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
        """)
        self.status_filter.currentTextChanged.connect(self.filtrar_dados)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Widget de abas para meses
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                background: transparent;
                border: none;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar {
                qproperty-drawBase: 0;
            }
            QTabBar::tab {
                background: rgba(255,255,255,0.1);
                color: white;
                padding: 10px 20px;
                margin-right: 2px;
                border-radius: 8px 8px 0px 0px;
                font-weight: bold;
                font-size: 13px;
                min-width: 80px;
                border: 2px solid transparent;
            }
            QTabBar::tab:hover:!selected {
                background: rgba(255,255,255,0.2);
                border: 2px solid rgba(255,255,255,0.3);
            }
            QTabBar::tab:pressed {
                background-color: rgba(229,9,20,0.6) !important;
                color: white !important;
                border: 2px solid rgba(229,9,20,0.8) !important;
            }
            QTabBar::tab:selected {
                background-color: rgba(229,9,20,0.8) !important;
                color: white !important;
                border: 2px solid rgba(229,9,20,1.0) !important;
            }
            QTabBar::tab:focus {
                outline: none;
                background-color: rgba(229,9,20,0.7);
            }
        """)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Criar abas para os últimos 6 meses
        self.criar_abas_meses()
        
        layout.addWidget(self.tab_widget)
        
        
        # Rodapé com botões de ação
        footer_widget = QWidget()
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(20, 10, 20, 10)
        footer_layout.setSpacing(15)
        
        # Botão Pagar
        self.btn_pagar = QPushButton("💰 Pagar")
        self.btn_pagar.setStyleSheet("""
            QPushButton {
                background: rgba(40,167,69,0.9);
                color: white;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: none;
                min-width: 120px;
            }
            QPushButton:hover {
                background: rgba(40,167,69,1);
            }
            QPushButton:disabled {
                background: rgba(108,117,125,0.5);
                color: rgba(255,255,255,0.5);
            }
        """)
        self.btn_pagar.clicked.connect(self.pagar_mensalidade)
        self.btn_pagar.setEnabled(False)
        
        # Botão Editar
        self.btn_editar = QPushButton("✏️ Editar")
        self.btn_editar.setStyleSheet("""
            QPushButton {
                background: rgba(229,9,20,0.9);
                color: white;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: none;
                min-width: 120px;
            }
            QPushButton:hover {
                background: rgba(229,9,20,1);
            }
            QPushButton:disabled {
                background: rgba(108,117,125,0.5);
                color: rgba(255,255,255,0.5);
            }
        """)
        self.btn_editar.clicked.connect(self.editar_mensalidade)
        self.btn_editar.setEnabled(False)
        
        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_pagar)
        footer_layout.addWidget(self.btn_editar)
        footer_layout.addStretch()
        
        layout.addWidget(footer_widget)

    def get_valor_por_plano(self, plano):
        """Retorna o valor baseado no plano do aluno"""
        if not plano:
            return 180.0  # Valor padrão Adulto
            
        plano_str = str(plano).lower()
        
        # Extrair valores dos planos conforme cadastro_aluno_tab.py
        if "adulto - r$180" in plano_str:
            return 180.0
        elif "kids (5–13) - r$150" in plano_str:
            return 150.0
        elif "família: 2 adultos - r$320" in plano_str:
            return 320.0
        elif "família: 1 adulto + 1 kids - r$300" in plano_str:
            return 300.0
        elif "família: 2 adultos + 1 kids - r$450" in plano_str:
            return 450.0
        elif "família: 1 adulto + 2 kids - r$430" in plano_str:
            return 430.0
        elif "família: 1 adulto + 3 kids - r$500" in plano_str:
            return 500.0
        elif "bolsista" in plano_str or "patrocinado" in plano_str:
            return 0.0  # Plano Bolsista
        elif "personalizado" in plano_str:
            # Para planos personalizados: "Personalizado - R$valor"
            import re
            match = re.search(r'r\$(\d+(?:\.\d{2})?)', plano_str)
            if match:
                return float(match.group(1))
            else:
                return 180.0  # Fallback se não conseguir extrair valor
        else:
            # Para planos desconhecidos, usar valor padrão
            return 180.0

    def create_mensalidade_card(self, dados):
        """Cria um card para uma mensalidade"""
        card = QFrame()
        card.setFixedHeight(180)
        # Removido hover para não conflitar com seleção
        card.setStyleSheet("""
            QFrame {
                background: transparent;
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.3);
                margin: 5px;
            }
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)
        
        # Lado esquerdo - Foto e informações principais
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)
        
        # Container para foto e nome
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Foto do aluno
        foto_label = QLabel()
        foto_label.setFixedSize(70, 70)
        foto_label.setStyleSheet("""
            QLabel {
                background: rgba(255,255,255,0.9);
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.5);
            }
        """)
        foto_label.setAlignment(Qt.AlignCenter)
        foto_label.setScaledContents(True)
        
        # Carregar foto do aluno (dados[7] = foto_path)
        if len(dados) > 7 and dados[7]:
            foto_path = dados[7]
            if os.path.exists(foto_path):
                from PySide6.QtGui import QPixmap
                pixmap = QPixmap(foto_path)
                foto_label.setPixmap(pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                foto_label.setText("👤")
                foto_label.setStyleSheet(foto_label.styleSheet() + "font-size: 28px;")
        else:
            foto_label.setText("👤")
            foto_label.setStyleSheet(foto_label.styleSheet() + "font-size: 28px;")
        
        header_layout.addWidget(foto_label)
        
        # Container para nome e valor
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        
        # Nome do aluno (dados[1] = nome)
        nome_aluno = dados[1] if dados[1] else "Nome não encontrado"
        nome_label = QLabel(nome_aluno)
        nome_label.setStyleSheet("""
            QLabel {
                background: rgba(255,255,255,0.9);
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
                border: 1px solid rgba(255,255,255,0.7);
            }
        """)
        info_layout.addWidget(nome_label)
        
        # Valor baseado no plano do aluno (dados[8] = plano)
        plano = dados[8] if len(dados) > 8 else None
        valor_plano = self.get_valor_por_plano(plano)
        valor_label = QLabel(f"💰 R$ {valor_plano:.2f}")
        valor_label.setStyleSheet("""
            QLabel {
                background: rgba(255,255,255,0.9);
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
                font-weight: bold;
                color: #28a745;
                border: 1px solid rgba(255,255,255,0.5);
                max-width: 120px;
            }
        """)
        info_layout.addWidget(valor_label)
        
        # Mostrar plano do aluno
        if plano:
            plano_label = QLabel(f"🏆 {plano}")
            plano_label.setStyleSheet("""
                QLabel {
                    background: rgba(255,255,255,0.7);
                    border-radius: 6px;
                    padding: 4px 8px;
                    font-size: 10px;
                    color: #666;
                    border: 1px solid rgba(255,255,255,0.4);
                    max-width: 200px;
                    min-width: 150px;
                }
            """)
            info_layout.addWidget(plano_label)
        
        header_layout.addLayout(info_layout)
        left_layout.addLayout(header_layout)
        left_layout.addStretch()
        
        # Lado direito - Datas e Status
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)  # Aumentando espaçamento vertical
        
        # Vencimento
        venc_text = "Não definido"
        if dados[3]:
            try:
                from datetime import datetime
                dt = datetime.strptime(dados[3], "%Y-%m-%d")
                venc_text = dt.strftime("%d/%m/%Y")
            except:
                venc_text = dados[3]
        
        venc_label = QLabel(f"📅 Vence: {venc_text}")
        venc_label.setStyleSheet("""
            QLabel {
                background: rgba(255,255,255,0.8);
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 11px;
                color: #666;
                border: 1px solid rgba(255,255,255,0.4);
            }
        """)
        right_layout.addWidget(venc_label)
        
        # Pagamento/Status de Atraso
        status = dados[5] or "PENDENTE"
        
        if status == "PAGO" and dados[4]:
            # Se pago, mostrar data do pagamento
            try:
                from datetime import datetime
                dt = datetime.strptime(dados[4], "%Y-%m-%d")
                pag_text = f"✅ Pago: {dt.strftime('%d/%m/%Y')}"
                pag_color = "#28a745"  # Verde para pago
            except:
                pag_text = f"✅ Pago: {dados[4]}"
                pag_color = "#28a745"
        else:
            # Se pendente, calcular dias de atraso
            try:
                from datetime import datetime, date
                if dados[3]:  # data_vencimento
                    venc_date = datetime.strptime(dados[3], "%Y-%m-%d").date()
                    today = date.today()
                    if venc_date < today:
                        dias_atraso = (today - venc_date).days
                        pag_text = f"⚠️ Em atraso há {dias_atraso} dia{'s' if dias_atraso > 1 else ''}"
                        pag_color = "#dc3545"  # Vermelho para atraso
                    else:
                        pag_text = "🟡 Pendente"
                        pag_color = "#ffc107"  # Amarelo para pendente sem atraso
                else:
                    pag_text = "🟡 Pendente"
                    pag_color = "#ffc107"
            except:
                pag_text = "🟡 Pendente"
                pag_color = "#ffc107"
        
        pag_label = QLabel(pag_text)
        pag_label.setStyleSheet(f"""
            QLabel {{
                background: rgba(255,255,255,0.8);
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 11px;
                color: {pag_color};
                font-weight: bold;
                border: 1px solid rgba(255,255,255,0.4);
            }}
        """)
        right_layout.addWidget(pag_label)
        
        right_layout.addStretch()
        
        # Status e Botão de ação
        status_layout = QHBoxLayout()
        
        # Status com estilo igual ao das faixas/graus do cadastro
        status = dados[5] or "PENDENTE"
        
        status_label = QLabel(status)
        status_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255,255,255,0.95);
                padding: 7px 10px;
                border-radius: 10px;
                border: 1.5px solid #ccc;
                font-size: 13px;
                color: #111;
                font-weight: bold;
                min-width: 80px;
            }
        """)
        status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(status_label)
        
        status_layout.addStretch()
        right_layout.addLayout(status_layout)
        
        # Adicionar layouts ao card
        layout.addLayout(left_layout, 2)
        layout.addLayout(right_layout, 1)
        
        # Sistema de seleção do card
        self.adicionar_selecao_card(card, dados)
        
        return card

    def load(self):
        """Carrega os dados das mensalidades"""
        try:
            # Verificar se precisa resetar para novo mês
            self.verificar_reset_mensal()
            
            # Carregar mensalidades da aba atual (mês atual)
            mes_atual = self.tab_widget.currentIndex() + 1  # +1 porque mês começa em 1
            self.carregar_mensalidades_mes(mes_atual)
            
        except Exception as e:
            show_error(self, "Erro ao carregar dados", f"Erro: {str(e)}")

    def filtrar_dados(self):
        """Filtra dados por status na aba atual"""
        try:
            # Recarregar mensalidades da aba atual com filtro aplicado
            mes_atual = self.tab_widget.currentIndex() + 1  # +1 porque mês começa em 1
            self.carregar_mensalidades_mes(mes_atual)
        except Exception as e:
            show_error(self, "Erro ao filtrar", f"Erro: {str(e)}")

    def gerar_mensalidades(self):
        """Gera mensalidades automáticas"""
        try:
            criadas = gerar_mensalidades_automaticas()
            show_info(self, "Mensalidades Geradas", f"Foram criadas {criadas} mensalidades automáticas.")
            self.load()
        except Exception as e:
            show_error(self, "Erro ao gerar mensalidades", f"Erro: {str(e)}")

    def adicionar_selecao_card(self, card, dados):
        """Adiciona sistema de seleção ao card"""
        # Estado inicial - não selecionado
        card.selecionado = False
        card.dados_mensalidade = dados
        
        # Estilo original do card SEM hover para evitar conflitos
        estilo_original = """
            QFrame {
                background: rgba(255,255,255,0.1);
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.3);
                margin: 5px;
            }
        """
        
        # Estilo selecionado com !important para sobrepor hover
        estilo_selecionado = """
            QFrame {
                background: rgba(229,9,20,0.1) !important;
                border-radius: 12px !important;
                border: 3px solid #e50914 !important;
                margin: 5px !important;
            }
        """
        
        def selecionar_card():
            if card.selecionado:
                # Desselecionar se já está selecionado
                card.selecionado = False
                card.setStyleSheet(estilo_original)
                
                # Remover da lista de selecionados
                if dados in self.mensalidades_selecionadas:
                    self.mensalidades_selecionadas.remove(dados)
            else:
                # Marcar este card como selecionado
                card.selecionado = True
                
                # Aplicar estilo de selecionado imediatamente
                card.setStyleSheet(estilo_selecionado)
                
                # Adicionar à lista de selecionados
                if dados not in self.mensalidades_selecionadas:
                    self.mensalidades_selecionadas.append(dados)
            
            # Atualizar botões baseado nas seleções
            self.toggle_botoes(len(self.mensalidades_selecionadas) > 0)
            
            # Definir mensalidade atual como a última selecionada
            if self.mensalidades_selecionadas:
                self.mensalidade_atual = self.mensalidades_selecionadas[-1]
            else:
                self.mensalidade_atual = None
        
        def deselecionar_card():
            card.selecionado = False
            card.setStyleSheet(estilo_original)
            if dados in self.mensalidades_selecionadas:
                self.mensalidades_selecionadas.remove(dados)
        
        # Definir estilo inicial
        card.setStyleSheet(estilo_original)
        
        # Adicionar evento de clique
        card.mousePressEvent = lambda event: selecionar_card()
        card.deselecionar = deselecionar_card
        
        # Cursor de mão para indicar que é clicável
        from PySide6.QtCore import Qt
        card.setCursor(Qt.PointingHandCursor)
    
    def limpar_selecoes_cards(self):
        """Remove seleção de todos os cards"""
        def limpar_recursivo(layout):
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item.widget() and hasattr(item.widget(), 'selecionado') and hasattr(item.widget(), 'deselecionar'):
                    if item.widget().selecionado:
                        item.widget().deselecionar()
        
        limpar_recursivo(self.cards_layout)
        self.mensalidade_atual = None
        self.mensalidades_selecionadas = []
        self.toggle_botoes(False)
    
    def toggle_botoes(self, enabled):
        """Ativa/desativa botões baseado na seleção"""
        self.btn_pagar.setEnabled(enabled)
        self.btn_editar.setEnabled(enabled)
        

    def nova_mensalidade(self):
        """Abre diálogo para nova mensalidade"""
        dialog = NovaMensalidadeDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.limpar_selecoes_cards()
            self.load()

    def pagar_mensalidade(self):
        """Marca mensalidades selecionadas como pagas"""
        if not self.mensalidades_selecionadas:
            show_error(self, "Erro", "Nenhuma mensalidade selecionada!")
            return
        
        # Confirmar pagamento múltiplo
        count = len(self.mensalidades_selecionadas)
        if count > 1:
            resposta = show_question(self, "Confirmar Pagamento", 
                                   f"Deseja marcar {count} mensalidades como pagas?")
            if not resposta:
                return
        
        sucessos = 0
        erros = 0
        
        try:
            hoje = date.today().isoformat()
            for mensalidade in self.mensalidades_selecionadas:
                mensalidade_id = mensalidade[0]
                try:
                    marcar_mensalidade_paga(mensalidade_id, hoje, "Pagamento confirmado via sistema")
                    sucessos += 1
                except Exception as e:
                    erros += 1
                    print(f"Erro ao pagar mensalidade {mensalidade_id}: {str(e)}")
            
            if sucessos > 0:
                if erros == 0:
                    show_info(self, "Pagamento Confirmado", 
                             f"{sucessos} mensalidade(s) marcada(s) como paga(s) com sucesso!")
                else:
                    show_info(self, "Pagamento Parcial", 
                             f"{sucessos} mensalidade(s) paga(s) com sucesso, {erros} erro(s).")
                self.load()
            else:
                show_error(self, "Erro", "Nenhuma mensalidade pôde ser paga.")
                
        except Exception as e:
            show_error(self, "Erro ao confirmar pagamento", f"Erro: {str(e)}")
    
    def editar_mensalidade(self):
        """Edita mensalidade selecionada"""
        if not self.mensalidade_atual:
            show_error(self, "Erro", "Nenhuma mensalidade selecionada!")
            return
            
        mensalidade_id = self.mensalidade_atual[0]
        # Obter dados completos da mensalidade
        from database.db import get_conn
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.*, a.nome, a.plano 
            FROM mensalidades m
            JOIN alunos a ON m.aluno_id = a.id 
            WHERE m.id=?
        """, (mensalidade_id,))
        dados = cur.fetchone()
        conn.close()
        
        if dados:
            dialog = EditarMensalidadeDialog(self, dados)
            if dialog.exec() == QDialog.Accepted:
                self.limpar_selecoes_cards()
                self.load()
    
    def marcar_pago(self, mensalidade_id):
        """Marca mensalidade como paga - função antiga"""
        try:
            hoje = date.today().isoformat()
            marcar_mensalidade_paga(mensalidade_id, hoje, "Pagamento confirmado via sistema")
            show_info(self, "Pagamento Confirmado", "Mensalidade marcada como paga com sucesso!")
            self.load()
        except Exception as e:
            show_error(self, "Erro ao confirmar pagamento", f"Erro: {str(e)}")
            
    def verificar_reset_mensal(self):
        """Verifica se precisa resetar status mensais"""
        try:
            hoje = date.today()
            mes_atual = hoje.month
            ano_atual = hoje.year
            
            # Verificar se já foi processado este mês
            conn = get_conn()
            cur = conn.cursor()
            
            # Criar tabela de configurações se não existir
            cur.execute("""
                CREATE TABLE IF NOT EXISTS configuracoes (
                    chave TEXT PRIMARY KEY,
                    valor TEXT
                )
            """)
            
            # Verificar último reset registrado
            cur.execute("""SELECT valor FROM configuracoes WHERE chave = 'ultimo_reset_mensal'""")
            resultado = cur.fetchone()
            
            ultimo_reset = None
            if resultado:
                try:
                    ultimo_reset = resultado[0]
                except:
                    pass
            
            reset_atual = f"{ano_atual}-{mes_atual:02d}"
            
            if ultimo_reset != reset_atual:
                # Resetar status das mensalidades para o novo mês
                self.resetar_status_mensalidades()
                
                # Atualizar registro do último reset
                cur.execute("""INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES (?, ?)""", 
                           ('ultimo_reset_mensal', reset_atual))
                conn.commit()
                print(f"Reset mensal executado para {reset_atual}")
            
            conn.close()
            
        except Exception as e:
            print(f"Erro ao verificar reset mensal: {e}")
    
    def resetar_status_mensalidades(self):
        """Reseta status das mensalidades para pendente no novo mês usando planos corretos do projeto"""
        try:
            conn = get_conn()
            cur = conn.cursor()
            
            from datetime import date
            hoje = date.today()
            
            # Criar novas mensalidades baseadas nos planos existentes dos alunos (excluir dependentes)
            cur.execute("""
                SELECT a.id, a.nome, a.plano 
                FROM alunos a 
                WHERE a.ativo = 1 AND a.plano IS NOT NULL AND a.plano != '' 
                AND a.responsavel_id IS NULL
            """)
            alunos = cur.fetchall()
            
            mensalidades_criadas = 0
            
            for aluno_id, nome, plano in alunos:
                # Verificar se já existe mensalidade para este mês
                cur.execute("""
                    SELECT id FROM mensalidades 
                    WHERE aluno_id = ? 
                    AND strftime('%m', data_vencimento) = ? 
                    AND strftime('%Y', data_vencimento) = ?
                """, (aluno_id, f"{hoje.month:02d}", str(hoje.year)))
                
                if not cur.fetchone():  # Se não existe, criar
                    # Usar função existente para determinar valor correto baseado no plano
                    valor = self.get_valor_por_plano(plano)
                    
                    # Data de vencimento (dia 10 do mês)
                    try:
                        data_vencimento = date(hoje.year, hoje.month, 10)
                    except ValueError:
                        data_vencimento = date(hoje.year, hoje.month, 28)
                    
                    # Criar mensalidade pendente
                    cur.execute("""
                        INSERT INTO mensalidades (aluno_id, valor, data_vencimento, status, observacoes)
                        VALUES (?, ?, ?, 'PENDENTE', ?)
                    """, (aluno_id, valor, data_vencimento.isoformat(), f"Mensalidade {hoje.month:02d}/{hoje.year} - {plano}"))
                    
                    mensalidades_criadas += 1
            
            conn.commit()
            conn.close()
            
            if mensalidades_criadas > 0:
                print(f"Criadas {mensalidades_criadas} mensalidades para o mês {hoje.month:02d}/{hoje.year}")
            
        except Exception as e:
            print(f"Erro ao resetar mensalidades: {e}")

    def criar_abas_meses(self):
        """Cria abas para cada mês do ano"""
        meses = [
            ("01", "Janeiro"),
            ("02", "Fevereiro"), 
            ("03", "Março"),
            ("04", "Abril"),
            ("05", "Maio"),
            ("06", "Junho"),
            ("07", "Julho"),
            ("08", "Agosto"),
            ("09", "Setembro"),
            ("10", "Outubro"),
            ("11", "Novembro"),
            ("12", "Dezembro")
        ]
        
        for mes_num, mes_nome in meses:
            # Criar scroll area para o mês
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll_area.setStyleSheet("""
                QScrollArea {
                    border: none;
                    background: transparent;
                }
                QScrollBar:vertical {
                    background-color: rgba(0,0,0,0.2);
                    width: 10px;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical {
                    background-color: rgba(229,9,20,0.7);
                    border-radius: 5px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: rgba(229,9,20,0.9);
                }
            """)
            
            # Widget de conteúdo para cada mês
            content_widget = QWidget()
            content_widget.setStyleSheet("background: transparent;")
            layout = QVBoxLayout(content_widget)
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            layout.setSpacing(10)
            layout.setContentsMargins(10, 10, 10, 10)
            
            scroll_area.setWidget(content_widget)
            self.tab_widget.addTab(scroll_area, mes_nome)
        
        # Definir mês atual como selecionado
        mes_atual = datetime.now().month - 1  # -1 porque índice começa em 0
        self.tab_widget.setCurrentIndex(mes_atual)
        
    def on_tab_changed(self, index):
        """Chamado quando a aba é alterada"""
        # Forçar atualização visual da tab
        self.tab_widget.repaint()
        # Carregar mensalidades do mês
        self.carregar_mensalidades_mes(index + 1)  # +1 porque mês começa em 1
        
    def carregar_mensalidades_mes(self, mes):
        """Carrega mensalidades do mês específico"""
        try:
            # Obter scroll area da aba atual
            current_tab = self.tab_widget.currentWidget()
            if not current_tab:
                return
                
            content_widget = current_tab.widget()
            if not content_widget:
                return
                
            layout = content_widget.layout()
            
            # Limpar layout atual
            self.clear_layout(layout)
            
            # Aplicar filtro de status
            status = self.status_filter.currentText()
            if status == "Todos":
                mensalidades = listar_mensalidades()
            else:
                mensalidades = listar_mensalidades(status)
            
            mensalidades_mes = []
            
            for mensalidade in mensalidades:
                # Verificar se a mensalidade é do mês desejado
                # dados[3] = data_vencimento
                data_venc = mensalidade[3] if len(mensalidade) > 3 else ''
                if data_venc and len(data_venc) >= 7:  # YYYY-MM-DD
                    mes_mensalidade = int(data_venc.split('-')[1])
                    if mes_mensalidade == mes:
                        mensalidades_mes.append(mensalidade)
            
            if mensalidades_mes:
                for mensalidade in mensalidades_mes:
                    card = self.create_mensalidade_card(mensalidade)
                    layout.addWidget(card)
            else:
                # Mostrar mensagem quando não há mensalidades
                label = QLabel(f"Nenhuma mensalidade encontrada para este mês")
                label.setStyleSheet("""
                    QLabel {
                        color: #666;
                        font-size: 14px;
                        padding: 20px;
                        text-align: center;
                        font-style: italic;
                    }
                """)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(label)
                
        except Exception as e:
            print(f"Erro ao carregar mensalidades do mês: {e}")
    

class FinanceiroDialog(QDialog):
    """Dialog base para o sistema financeiro seguindo o padrão do projeto"""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.clicked = None
        self.setupBaseUI()
    
    def setupBaseUI(self):
        self.setStyleSheet("QDialog { background-color: #1e1e1e; }")
        
        main = QVBoxLayout(self)
        main.setAlignment(Qt.AlignCenter)
        
        # Card principal
        self.card = QFrame()
        self.card.setStyleSheet("background:white;border-radius:18px;")
        
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(25, 25, 25, 25)
        self.card_layout.setSpacing(16)
        
        # Logo
        logo = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
        logo_path = os.path.abspath(logo_path)
        
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(pix)
        
        logo.setAlignment(Qt.AlignCenter)
        self.card_layout.addWidget(logo)
        
        # Container para conteúdo personalizado
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.card_layout.addWidget(self.content_widget)
        
        # Container para botões
        self.button_widget = QWidget()
        self.button_layout = QHBoxLayout(self.button_widget)
        self.button_layout.setSpacing(12)
        self.button_layout.setAlignment(Qt.AlignCenter)
        self.card_layout.addWidget(self.button_widget)
        
        main.addWidget(self.card)
    
    def add_button(self, text, callback, is_primary=True):
        """Adiciona botão com estilo do projeto"""
        btn = QPushButton(text)
        btn.setFixedHeight(45)
        btn.setCursor(Qt.PointingHandCursor)
        
        if is_primary:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #b00020;
                    color: white;
                    border-radius: 12px;
                    font-size: 15px;
                    font-weight: bold;
                    padding: 8px 16px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #8c001a;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #666;
                    color: white;
                    border-radius: 12px;
                    font-size: 15px;
                    font-weight: bold;
                    padding: 8px 16px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #555;
                }
            """)
        
        btn.clicked.connect(callback)
        self.button_layout.addWidget(btn)
        return btn


class NovaMensalidadeDialog(FinanceiroDialog):
    def __init__(self, parent):
        super().__init__("💰 Nova Mensalidade", parent)
        self.setFixedSize(500, 600)
        self.build_ui()

    def build_ui(self):
        # Título
        title = QLabel("Criar Nova Mensalidade")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-bottom: 20px;")
        self.content_layout.addWidget(title)
        
        # Formulário
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)
        
        # Estilo dos campos
        field_style = """
            QComboBox, QLineEdit, QDateEdit, QTextEdit {
                padding: 10px;
                font-size: 14px;
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: #f9f9f9;
            }
            QComboBox:focus, QLineEdit:focus, QDateEdit:focus, QTextEdit:focus {
                border-color: #b00020;
                background-color: white;
            }
        """
        
        # Aluno
        self.combo_aluno = QComboBox()
        self.combo_aluno.setStyleSheet(field_style)
        try:
            alunos = listar_alunos()
            for aluno in alunos:
                self.combo_aluno.addItem(f"👤 {aluno[1]} (ID: {aluno[0]})", aluno[0])
        except:
            pass
        
        label_aluno = QLabel("Selecione o Aluno:")
        label_aluno.setStyleSheet("font-weight: bold; color: #333;")
        form_layout.addRow(label_aluno, self.combo_aluno)

        # Valor
        self.valor_input = QLineEdit()
        self.valor_input.setPlaceholderText("Ex: 180.00")
        self.valor_input.setStyleSheet(field_style)
        
        label_valor = QLabel("Valor (R$):")
        label_valor.setStyleSheet("font-weight: bold; color: #333;")
        form_layout.addRow(label_valor, self.valor_input)

        # Data de vencimento
        self.data_venc = QDateEdit()
        self.data_venc.setDate(QDate.currentDate())
        self.data_venc.setStyleSheet(field_style)
        
        label_data = QLabel("Data de Vencimento:")
        label_data.setStyleSheet("font-weight: bold; color: #333;")
        form_layout.addRow(label_data, self.data_venc)

        # Observações
        self.obs_input = QTextEdit()
        self.obs_input.setMaximumHeight(80)
        self.obs_input.setPlaceholderText("Observações adicionais (opcional)...")
        self.obs_input.setStyleSheet(field_style)
        
        label_obs = QLabel("Observações:")
        label_obs.setStyleSheet("font-weight: bold; color: #333;")
        form_layout.addRow(label_obs, self.obs_input)
        
        self.content_layout.addWidget(form_widget)
        
        # Botões
        self.add_button("Cancelar", self.reject, False)
        self.add_button("💰 Criar Mensalidade", self.criar_mensalidade, True)

    def criar_mensalidade(self):
        """Cria nova mensalidade"""
        try:
            aluno_id = self.combo_aluno.currentData()
            valor = float(self.valor_input.text().replace(",", "."))
            data_venc = self.data_venc.date().toString("yyyy-MM-dd")
            obs = self.obs_input.toPlainText() or "Mensalidade criada manualmente"
            
            criar_mensalidade(aluno_id, valor, data_venc, obs)
            show_info("Sucesso", "Mensalidade criada com sucesso!")
            self.accept()
            
        except ValueError:
            show_error(self, "Erro", "Valor inválido. Use apenas números (ex: 180.00)")
        except Exception as e:
            show_error(self, "Erro ao criar mensalidade", f"Erro: {str(e)}")


class EditarMensalidadeDialog(FinanceiroDialog):
    def __init__(self, parent, dados):
        super().__init__("✏️ Editar Mensalidade", parent)
        self.dados = dados
        self.setFixedSize(500, 700)
        self.build_ui()
        self.preencher_campos()

    def build_ui(self):
        # Título
        title = QLabel("Editar Mensalidade")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-bottom: 20px;")
        self.content_layout.addWidget(title)
        
        # Info do aluno (read-only)
        info_aluno = QLabel(f"📝 Aluno: {self.dados[9]}")  # Nome do aluno
        info_aluno.setStyleSheet("""
            QLabel {
                background: rgba(229,9,20,0.1);
                color: #333;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                border: 2px solid rgba(229,9,20,0.3);
            }
        """)
        self.content_layout.addWidget(info_aluno)
        
        # Formulário
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)
        
        # Estilo dos campos (cor preta como no resto do projeto)
        field_style = """
            QComboBox, QLineEdit, QDateEdit, QTextEdit {
                background-color: rgba(255,255,255,0.95);
                padding: 7px 10px;
                border-radius: 10px;
                border: 1.5px solid #ccc;
                font-size: 13px;
                color: #111;
            }
            QComboBox:focus, QLineEdit:focus, QDateEdit:focus, QTextEdit:focus {
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

        # Plano
        self.plano_combo = QComboBox()
        self.plano_combo.setEditable(True)
        self.carregar_planos()
        self.plano_combo.setStyleSheet(field_style)
        
        label_plano = QLabel("Plano:")
        label_plano.setStyleSheet("font-weight: bold; color: #333;")
        form_layout.addRow(label_plano, self.plano_combo)

        # Valor
        self.valor_input = QLineEdit()
        self.valor_input.setPlaceholderText("Digite o valor da mensalidade")
        self.valor_input.setStyleSheet(field_style)
        
        label_valor = QLabel("Valor (R$):")
        label_valor.setStyleSheet("font-weight: bold; color: #333;")
        form_layout.addRow(label_valor, self.valor_input)

        # Data de vencimento
        self.data_venc = QDateEdit()
        self.data_venc.setCalendarPopup(True)
        self.data_venc.setDisplayFormat("dd/MM/yyyy")
        self.data_venc.setStyleSheet(field_style)
        
        label_data = QLabel("Data de Vencimento:")
        label_data.setStyleSheet("font-weight: bold; color: #333;")
        form_layout.addRow(label_data, self.data_venc)

        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["PENDENTE", "PAGO", "VENCIDO"])
        self.status_combo.setStyleSheet(field_style)
        
        label_status = QLabel("Status:")
        label_status.setStyleSheet("font-weight: bold; color: #333;")
        form_layout.addRow(label_status, self.status_combo)

        # Observações
        self.obs_input = QTextEdit()
        self.obs_input.setMaximumHeight(80)
        self.obs_input.setPlaceholderText("Digite observações sobre esta mensalidade (opcional)")
        self.obs_input.setStyleSheet(field_style)
        
        label_obs = QLabel("Observações:")
        label_obs.setStyleSheet("font-weight: bold; color: #333;")
        form_layout.addRow(label_obs, self.obs_input)
        
        self.content_layout.addWidget(form_widget)
        
        # Área de botões adicionais
        buttons_area = QHBoxLayout()
        
        # Botão Vincular (igual ao do cadastro)
        btn_vincular = QPushButton("Vincular a Responsável")
        btn_vincular.setFixedSize(200, 44)
        btn_vincular.setStyleSheet("""
            QPushButton {
                background-color: #2E86AB;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1e5f7a;
            }
        """)
        btn_vincular.clicked.connect(self.vincular_mensalidade)
        
        buttons_area.addWidget(btn_vincular)
        buttons_area.addStretch()
        
        self.content_layout.addLayout(buttons_area)
        
        # Botões principais
        self.add_button("Cancelar", self.reject, False)
        self.add_button("💾 Salvar Alterações", self.salvar_alteracoes, True)

    def carregar_planos(self):
        """Carrega planos do banco de dados"""
        try:
            from database.db import get_planos_formatados
            planos = get_planos_formatados()
            self.plano_combo.addItems(planos)
        except Exception:
            # Fallback para planos padrão
            self.plano_combo.addItems([
                "Adulto - R$180",
                "Kids (5–13) - R$150", 
                "Plano Personalizado"
            ])

    def preencher_campos(self):
        """Preenche os campos com os dados atuais da mensalidade"""
        # Plano (se disponível nos dados)
        try:
            plano_atual = self.dados[10] if len(self.dados) > 10 else "Adulto - R$180"
            index = self.plano_combo.findText(plano_atual)
            if index >= 0:
                self.plano_combo.setCurrentIndex(index)
            else:
                self.plano_combo.setEditText(plano_atual)
        except:
            pass
            
        # Valor
        self.valor_input.setText(str(self.dados[2]))  # valor
        
        # Data de vencimento
        try:
            data_venc = datetime.strptime(self.dados[3], "%Y-%m-%d").date()
            self.data_venc.setDate(QDate(data_venc.year, data_venc.month, data_venc.day))
        except:
            self.data_venc.setDate(QDate.currentDate())
        
        # Status
        status = self.dados[4].upper() if self.dados[4] else "PENDENTE"
        index = self.status_combo.findText(status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        
        # Observações
        obs = self.dados[7] or ""  # observacoes
        self.obs_input.setPlainText(obs)

    def vincular_mensalidade(self):
        """Vincula um aluno existente a um responsável (usando função utilitária)"""
        from utils.vincular_utils import vincular_aluno_responsavel
        
        if vincular_aluno_responsavel(self):
            # Recarregar dados se possível
            if hasattr(self, 'load'):
                self.load()

    def salvar_alteracoes(self):
        """Salva as alterações da mensalidade"""
        try:
            plano_texto = self.plano_combo.currentText()
            valor = float(self.valor_input.text().replace(",", "."))
            data_venc = self.data_venc.date().toString("yyyy-MM-dd")
            status = self.status_combo.currentText()
            obs = self.obs_input.toPlainText()
            
            mensalidade_id = self.dados[0]  # id
            
            # Atualizar no banco de dados
            from database.db import get_conn
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                UPDATE mensalidades 
                SET valor=?, data_vencimento=?, status=?, observacoes=?
                WHERE id=?
            """, (valor, data_venc, status, obs, mensalidade_id))
            conn.commit()
            conn.close()
            
            show_info(self, "Sucesso", f"Mensalidade atualizada com sucesso!\n\nPlano: {plano_texto}\nValor: R$ {valor:.2f}")
            self.accept()
            
        except ValueError:
            show_error(self, "Erro", "Valor inválido. Use apenas números (ex: 180.00)")
        except Exception as e:
            show_error(self, "Erro ao salvar alterações", f"Erro: {str(e)}")


