import os
from datetime import date, datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, 
    QDateEdit, QDialog, QFormLayout, QLineEdit, QTextEdit, QMessageBox, 
    QFrame, QScrollArea, QTabWidget
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap, QFont

from ui.base_tab import BaseTab, SCROLLBAR_STYLE
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

        # ── TITLE ROW + FILTRO ──
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        title = QLabel("Gestão Financeira")
        title.setStyleSheet(
            "color:#ffffff; font-size:22px; font-weight:700;"
            " font-family:'Arial Black',sans-serif; background:transparent; border:none;"
        )
        top_row.addWidget(title)
        top_row.addStretch()

        _combo_style = """
            QComboBox {
                background-color: #0e0e0e;
                padding: 7px 10px;
                border-radius: 10px;
                border: 1px solid #1e1e1e;
                font-size: 13px;
                color: #ffffff;
                min-width: 120px;
            }
            QComboBox:focus { border: 1.5px solid #cc1e1e; }
            QComboBox QAbstractItemView {
                background-color: #0e0e0e;
                border: 2px solid #cc1e1e;
                border-radius: 8px;
                selection-background-color: #cc1e1e;
                selection-color: white;
                padding: 5px;
                font-size: 13px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                background-color: #0e0e0e; color: #aaaaaa;
                padding: 8px 12px; margin: 1px; border-radius: 5px;
            }
            QComboBox QAbstractItemView::item:hover { background-color: #1a1a1a; color: #ffffff; }
            QComboBox QAbstractItemView::item:selected {
                background-color: #cc1e1e; color: white; font-weight: bold;
            }
        """
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Todos", "PENDENTE", "PAGO"])
        self.status_filter.setStyleSheet(_combo_style)
        self.status_filter.currentTextChanged.connect(self.filtrar_dados)
        top_row.addWidget(self.status_filter)

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
        btn_export.clicked.connect(self.exportar_financeiro_pdf)
        top_row.addWidget(btn_export)

        layout.addLayout(top_row)

        # Widget de abas para meses
        self.tab_widget = QTabWidget()
        
        # Tornar as abas scrolláveis para telas menores
        self.tab_widget.tabBar().setUsesScrollButtons(True)
        self.tab_widget.tabBar().setElideMode(Qt.ElideNone)
        self.tab_widget.tabBar().setExpanding(False)
        
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
                qproperty-usesScrollButtons: true;
                qproperty-expanding: false;
            }
            QTabBar::tab {
                background: #161616;
                color: #444444;
                padding: 3px 10px;
                margin-right: 4px;
                border-radius: 5px;
                font-weight: 500;
                font-size: 11px;
                min-width: 36px;
                max-width: 60px;
                border: 1px solid #1e1e1e;
            }
            QTabBar::tab:hover:!selected {
                background: #1e1e1e;
                color: #888888;
                border: 1px solid #2a2a2a;
            }
            QTabBar::tab:selected {
                background: #cc1e1e;
                color: #ffffff;
                border: none;
                font-weight: 600;
            }
            QTabBar::tab:pressed {
                background: #a01515;
                color: #ffffff;
                border: none;
            }
            QTabBar::scroller {
                width: 22px;
                background: #161616;
                border-radius: 4px;
            }
            QTabBar QToolButton {
                background: #cc1e1e;
                color: white;
                border-radius: 3px;
                margin: 1px;
                font-weight: bold;
                width: 18px;
                height: 18px;
            }
            QTabBar QToolButton:hover {
                background: #e02020;
            }
            QTabBar QToolButton::left-arrow {
                image: none;
                border-left: 4px solid white;
                border-top: 4px solid transparent;
                border-bottom: 4px solid transparent;
            }
            QTabBar QToolButton::right-arrow {
                image: none;
                border-right: 4px solid white;
                border-top: 4px solid transparent;
                border-bottom: 4px solid transparent;
            }
        """)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Criar abas para os últimos 6 meses
        self.criar_abas_meses()
        
        layout.addWidget(self.tab_widget)
        
        
        # ── RODAPÉ: botões de ação ──
        footer_widget = QWidget()
        footer_widget.setObjectName("financeiroFooter")
        footer_widget.setStyleSheet("#financeiroFooter { background: transparent; }")
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(0, 8, 0, 0)
        footer_layout.setSpacing(10)

        _btn_disabled = """
            QPushButton:disabled {
                background: #1a1a1a; color: #333333; border: 1px solid #222222;
            }
        """
        self.btn_editar = QPushButton("Editar")
        self.btn_editar.setFixedHeight(34)
        self.btn_editar.setStyleSheet("""
            QPushButton {
                background: #1e1e1e; color: #888888;
                border: 1px solid #2a2a2a; border-radius: 7px;
                font-size: 12px; font-weight: 500; padding: 0 16px;
            }
            QPushButton:hover { background: #252525; color: #cccccc; }
        """ + _btn_disabled)
        self.btn_editar.clicked.connect(self.editar_mensalidade)
        self.btn_editar.setEnabled(False)

        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_editar)

        layout.addWidget(footer_widget)

    def get_valor_por_plano(self, plano):
        """Retorna o valor baseado no plano do aluno"""
        import re
        if not plano:
            return 180.0

        plano_str = str(plano).lower()

        if "bolsista" in plano_str or "patrocinado" in plano_str:
            return 0.0

        # Extrair valor numérico diretamente do nome do plano (ex: "Adulto - R$180")
        match = re.search(r'r\$(\d+(?:[.,]\d+)?)', plano_str)
        if match:
            return float(match.group(1).replace(',', '.'))

        return 180.0  # fallback

    def create_mensalidade_card(self, dados):
        """Cria um card de mensalidade com layout 3 colunas."""
        from datetime import datetime, date as date_type
        card = QFrame()
        card.setObjectName("mensalidadeCard")
        card.setStyleSheet("""
            QFrame#mensalidadeCard {
                background: #161616;
                border: 1px solid #1e1e1e;
                border-radius: 9px;
            }
        """)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        nome_aluno = dados[1] if dados[1] else "?"

        # ── Col 1: name, plan, amount, dates (flex 1) ──
        info = QVBoxLayout()
        info.setSpacing(0)
        info.setContentsMargins(0, 0, 0, 0)

        lbl_nome = QLabel(nome_aluno)
        lbl_nome.setStyleSheet(
            "font-size: 12px; font-weight: 500; color: #cccccc; background: transparent; margin-bottom: 3px;"
        )
        info.addWidget(lbl_nome)

        plano = dados[8] if len(dados) > 8 else ""
        if plano:
            lbl_plano = QLabel(plano)
            lbl_plano.setStyleSheet(
                "font-size: 10px; color: #333333; background: transparent; margin-bottom: 5px;"
            )
            info.addWidget(lbl_plano)

        valor_plano = self.get_valor_por_plano(plano)
        lbl_valor = QLabel(f"R$ {valor_plano:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        lbl_valor.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #ffffff; background: transparent;"
        )
        info.addWidget(lbl_valor)

        venc_text = "Não definido"
        if dados[3]:
            try:
                dt = datetime.strptime(dados[3], "%Y-%m-%d")
                venc_text = dt.strftime("%d/%m/%Y")
            except Exception:
                venc_text = dados[3]

        status = dados[5] or "PENDENTE"
        pg_text = ""
        if status == "PAGO" and dados[4]:
            try:
                dt = datetime.strptime(dados[4], "%Y-%m-%d")
                pg_text = f" · Pago: {dt.strftime('%d/%m/%Y')}"
            except Exception:
                pg_text = f" · Pago: {dados[4]}"

        date_color = "#2d8a52" if status == "PAGO" else "#333333"
        lbl_dates = QLabel(f"Vence: {venc_text}{pg_text}")
        lbl_dates.setStyleSheet(
            f"font-size: 10px; color: {date_color}; background: transparent; margin-top: 3px;"
        )
        info.addWidget(lbl_dates)
        layout.addLayout(info, 1)

        # ── Col 3: status badge + Registrar button ──
        right = QVBoxLayout()
        right.setSpacing(5)
        right.setContentsMargins(0, 0, 0, 0)

        from datetime import date as _date
        if status == "PAGO":
            status_lbl = QLabel("Pago")
            status_lbl.setStyleSheet(
                "background: rgba(26,122,60,0.12); color: #2d8a52;"
                " font-size: 10px; padding: 2px 7px; border-radius: 4px;"
            )
            is_atrasado = False
        else:
            try:
                venc_date = datetime.strptime(dados[3], "%Y-%m-%d").date()
                is_atrasado = venc_date < _date.today()
            except Exception:
                is_atrasado = True

            if is_atrasado:
                status_lbl = QLabel("Atrasado")
                status_lbl.setStyleSheet(
                    "background: rgba(204,30,30,0.12); color: #c04444;"
                    " font-size: 10px; padding: 2px 7px; border-radius: 4px;"
                )
            else:
                status_lbl = QLabel("A Vencer")
                status_lbl.setStyleSheet(
                    "background: rgba(184,124,14,0.12); color: #b87c0e;"
                    " font-size: 10px; padding: 2px 7px; border-radius: 4px;"
                )
        right.addWidget(status_lbl, 0, Qt.AlignRight)

        if status != "PAGO" and is_atrasado:
            btn_reg = QPushButton("Registrar Pgto")
            btn_reg.setFixedHeight(28)
            btn_reg.setStyleSheet("""
                QPushButton {
                    background: #cc1e1e; color: #ffffff; border: none;
                    padding: 4px 12px; border-radius: 5px; font-size: 11px; font-weight: 600;
                }
                QPushButton:hover { background: #e02020; }
                QPushButton:pressed { background: #a01515; }
            """)
            btn_reg.clicked.connect(lambda: self._registrar_pagamento_card(dados))
            right.addWidget(btn_reg, 0, Qt.AlignRight)

        right.addStretch()
        layout.addLayout(right)

        self.adicionar_selecao_card(card, dados)
        return card

    def _registrar_pagamento_card(self, dados):
        """Marca a mensalidade como paga diretamente do botão Registrar no card."""
        mensalidade_id = dados[0]
        self.marcar_pago(mensalidade_id)

    def load(self):
        """Carrega os dados das mensalidades"""
        try:
            # Verificar se precisa resetar para novo mês
            self.verificar_reset_mensal()

            # Garantir que todos os responsáveis ativos tenham mensalidade no mês atual
            self.garantir_mensalidades_mes_atual()

            # Carregar mensalidades da aba atual (mês atual)
            mes_atual = self.tab_widget.currentIndex() + 1  # +1 porque mês começa em 1
            self.carregar_mensalidades_mes(mes_atual)

        except Exception as e:
            show_error(self, "Erro ao carregar dados", f"Erro: {str(e)}")

    def exportar_financeiro_pdf(self):
        from ui.export_helpers import exportar_pdf_dialog
        exportar_pdf_dialog(self, "financeiro")

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
        
        estilo_original = """
            QFrame#mensalidadeCard {
                background: #161616;
                border-radius: 9px;
                border: 1px solid #1e1e1e;
            }
        """

        estilo_selecionado = """
            QFrame#mensalidadeCard {
                background: rgba(204,30,30,0.08);
                border-radius: 9px;
                border: 2px solid #cc1e1e;
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
            
    def garantir_mensalidades_mes_atual(self):
        """Cria mensalidades para responsáveis ativos que ainda não têm registro no mês atual."""
        try:
            from datetime import date as _date
            hoje = _date.today()
            conn = get_conn()
            cur = conn.cursor()

            cur.execute("""
                SELECT a.id, a.plano
                FROM alunos a
                WHERE a.ativo = 1
                  AND a.responsavel_id IS NULL
                  AND a.plano IS NOT NULL
                  AND a.plano != ''
                  AND a.plano NOT LIKE '%bolsist%'
            """)
            responsaveis = cur.fetchall()

            for aluno_id, plano in responsaveis:
                cur.execute("""
                    SELECT id FROM mensalidades
                    WHERE aluno_id = ?
                      AND strftime('%m', data_vencimento) = ?
                      AND strftime('%Y', data_vencimento) = ?
                """, (aluno_id, f"{hoje.month:02d}", str(hoje.year)))

                if not cur.fetchone():
                    valor = self.get_valor_por_plano(plano)
                    try:
                        data_venc = _date(hoje.year, hoje.month, 10)
                    except ValueError:
                        data_venc = _date(hoje.year, hoje.month, 28)
                    cur.execute("""
                        INSERT INTO mensalidades (aluno_id, valor, data_vencimento, status, observacoes)
                        VALUES (?, ?, ?, 'PENDENTE', ?)
                    """, (aluno_id, valor, data_venc.isoformat(),
                          f"Mensalidade {hoje.month:02d}/{hoje.year} - {plano}"))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erro ao garantir mensalidades: {e}")

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
        """Cria abas para cada mês do ano com nomes responsivos"""
        meses = [
            ("01", "Jan", "Janeiro"),
            ("02", "Fev", "Fevereiro"), 
            ("03", "Mar", "Março"),
            ("04", "Abr", "Abril"),
            ("05", "Mai", "Maio"),
            ("06", "Jun", "Junho"),
            ("07", "Jul", "Julho"),
            ("08", "Ago", "Agosto"),
            ("09", "Set", "Setembro"),
            ("10", "Out", "Outubro"),
            ("11", "Nov", "Novembro"),
            ("12", "Dez", "Dezembro")
        ]
        
        for mes_num, mes_curto, mes_completo in meses:
            # Criar scroll area para o mês com melhor responsividade
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll_area.setStyleSheet(
                f"QScrollArea {{ border: none; background: transparent; }} {SCROLLBAR_STYLE}"
            )
            
            # Widget de conteúdo para cada mês - Melhor centralização
            content_widget = QWidget()
            content_widget.setStyleSheet("background: transparent;")
            layout = QVBoxLayout(content_widget)
            layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            layout.setSpacing(10)  # Voltando ao espaçamento original
            layout.setContentsMargins(20, 15, 20, 15)  # Margens para melhor centralização
            
            # Garantir que os cards fiquem centralizados mesmo com largura limitada
            content_widget.setMinimumWidth(500)  # Largura mínima para centralização
            
            scroll_area.setWidget(content_widget)
            
            # Adicionar a aba com nome curto, mas tooltip com nome completo
            tab_index = self.tab_widget.addTab(scroll_area, mes_curto)
            self.tab_widget.tabBar().setTabToolTip(tab_index, mes_completo)
        
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
                label = QLabel("Nenhuma mensalidade encontrada para este mês.")
                label.setObjectName("emptyLabel")
                label.setStyleSheet(
                    "#emptyLabel { color: #333333; font-size: 13px; background: transparent; border: none; }"
                )
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
        self.setObjectName("financeiroDialog")
        self.setStyleSheet("#financeiroDialog { background: #111111; }")

        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # Card principal
        self.card = QFrame()
        self.card.setObjectName("financeiroCard")
        self.card.setStyleSheet(
            "#financeiroCard { background: #161616; border-radius: 10px; border: 1px solid #222222; }"
        )

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(24, 20, 24, 20)
        self.card_layout.setSpacing(14)

        # Container para conteúdo personalizado
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.card_layout.addWidget(self.content_widget)

        # Container para botões
        self.button_widget = QWidget()
        self.button_widget.setStyleSheet("background: transparent;")
        self.button_layout = QHBoxLayout(self.button_widget)
        self.button_layout.setSpacing(10)
        self.button_layout.setAlignment(Qt.AlignCenter)
        self.card_layout.addWidget(self.button_widget)

        main.addWidget(self.card)
    
    def add_button(self, text, callback, is_primary=True):
        btn = QPushButton(text)
        btn.setFixedHeight(38)
        btn.setCursor(Qt.PointingHandCursor)

        if is_primary:
            btn.setStyleSheet("""
                QPushButton {
                    background: #cc1e1e; color: #ffffff;
                    border: none; border-radius: 7px;
                    font-size: 13px; font-weight: 600; padding: 0 20px;
                }
                QPushButton:hover  { background: #e02020; }
                QPushButton:pressed{ background: #a01515; }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background: #1e1e1e; color: #888888;
                    border: 1px solid #2a2a2a; border-radius: 7px;
                    font-size: 13px; font-weight: 500; padding: 0 20px;
                }
                QPushButton:hover { background: #252525; color: #cccccc; }
            """)

        btn.clicked.connect(callback)
        self.button_layout.addWidget(btn)
        return btn


class NovaMensalidadeDialog(FinanceiroDialog):
    def __init__(self, parent):
        super().__init__("Nova Mensalidade", parent)
        self.setFixedSize(500, 580)
        self.build_ui()

    def build_ui(self):
        title = QLabel("Nova Mensalidade")
        title.setStyleSheet(
            "color:#ffffff; font-size:16px; font-weight:700;"
            " background:transparent; border:none; margin-bottom:8px;"
        )
        self.content_layout.addWidget(title)

        _label_style = "color:#888888; font-size:12px; font-weight:500; background:transparent; border:none;"
        _field_style = """
            QComboBox, QLineEdit, QDateEdit, QTextEdit {
                background-color: #0e0e0e; padding: 8px 10px;
                border-radius: 8px; border: 1px solid #1e1e1e;
                font-size: 13px; color: #cccccc;
            }
            QComboBox:focus, QLineEdit:focus, QDateEdit:focus, QTextEdit:focus {
                border: 1.5px solid #cc1e1e;
            }
            QComboBox QAbstractItemView {
                background-color: #0e0e0e; border: 2px solid #cc1e1e;
                border-radius: 8px; selection-background-color: #cc1e1e;
                selection-color: white; padding: 5px; font-size: 13px;
            }
            QComboBox QAbstractItemView::item {
                background-color: #0e0e0e; color: #aaaaaa;
                padding: 8px 12px; margin: 1px; border-radius: 5px;
            }
            QComboBox QAbstractItemView::item:hover { background-color: #1a1a1a; color: #ffffff; }
            QComboBox QAbstractItemView::item:selected {
                background-color: #cc1e1e; color: white; font-weight: bold;
            }
        """

        form_widget = QWidget()
        form_widget.setStyleSheet("background: transparent;")
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(12)

        self.combo_aluno = QComboBox()
        self.combo_aluno.setStyleSheet(_field_style)
        try:
            alunos = listar_alunos()
            for aluno in alunos:
                self.combo_aluno.addItem(f"{aluno[1]} (ID: {aluno[0]})", aluno[0])
        except Exception:
            pass
        label_aluno = QLabel("Aluno:")
        label_aluno.setStyleSheet(_label_style)
        form_layout.addRow(label_aluno, self.combo_aluno)

        self.valor_input = QLineEdit()
        self.valor_input.setPlaceholderText("Ex: 180.00")
        self.valor_input.setStyleSheet(_field_style)
        label_valor = QLabel("Valor (R$):")
        label_valor.setStyleSheet(_label_style)
        form_layout.addRow(label_valor, self.valor_input)

        self.data_venc = QDateEdit()
        self.data_venc.setDate(QDate.currentDate())
        self.data_venc.setStyleSheet(_field_style)
        label_data = QLabel("Data de Vencimento:")
        label_data.setStyleSheet(_label_style)
        form_layout.addRow(label_data, self.data_venc)

        self.obs_input = QTextEdit()
        self.obs_input.setMaximumHeight(70)
        self.obs_input.setPlaceholderText("Observações adicionais (opcional)...")
        self.obs_input.setStyleSheet(_field_style)
        label_obs = QLabel("Observações:")
        label_obs.setStyleSheet(_label_style)
        form_layout.addRow(label_obs, self.obs_input)

        self.content_layout.addWidget(form_widget)

        self.add_button("Cancelar", self.reject, False)
        self.add_button("Criar Mensalidade", self.criar_mensalidade, True)

    def criar_mensalidade(self):
        """Cria nova mensalidade"""
        try:
            aluno_id = self.combo_aluno.currentData()
            valor = float(self.valor_input.text().replace(",", "."))
            data_venc = self.data_venc.date().toString("yyyy-MM-dd")
            obs = self.obs_input.toPlainText() or "Mensalidade criada manualmente"
            
            criar_mensalidade(aluno_id, valor, data_venc, obs)
            show_info(self, "Sucesso", "Mensalidade criada com sucesso!")
            self.accept()
            
        except ValueError:
            show_error(self, "Erro", "Valor inválido. Use apenas números (ex: 180.00)")
        except Exception as e:
            show_error(self, "Erro ao criar mensalidade", f"Erro: {str(e)}")


class EditarMensalidadeDialog(FinanceiroDialog):
    def __init__(self, parent, dados):
        super().__init__("Editar Mensalidade", parent)
        self.dados = dados
        self.setFixedSize(500, 680)
        self.build_ui()
        self.preencher_campos()

    def build_ui(self):
        title = QLabel("Editar Mensalidade")
        title.setStyleSheet(
            "color:#ffffff; font-size:16px; font-weight:700;"
            " background:transparent; border:none; margin-bottom:4px;"
        )
        self.content_layout.addWidget(title)

        info_aluno = QLabel(f"Aluno: {self.dados[8]}")
        info_aluno.setObjectName("editInfoAluno")
        info_aluno.setStyleSheet(
            "#editInfoAluno {"
            " background: rgba(204,30,30,0.08); color: #cccccc;"
            " padding: 10px 12px; border-radius: 7px; font-size:12px;"
            " border: 1px solid rgba(204,30,30,0.2);"
            "}"
        )
        self.content_layout.addWidget(info_aluno)

        _label_style = "color:#888888; font-size:12px; font-weight:500; background:transparent; border:none;"
        _field_style = """
            QComboBox, QLineEdit, QDateEdit, QTextEdit {
                background-color: #0e0e0e; padding: 8px 10px;
                border-radius: 8px; border: 1px solid #1e1e1e;
                font-size: 13px; color: #cccccc;
            }
            QComboBox:focus, QLineEdit:focus, QDateEdit:focus, QTextEdit:focus {
                border: 1.5px solid #cc1e1e;
            }
            QComboBox QAbstractItemView {
                background-color: #0e0e0e; border: 2px solid #cc1e1e;
                border-radius: 8px; selection-background-color: #cc1e1e;
                selection-color: white; padding: 5px; font-size: 13px; outline: none;
            }
            QComboBox QAbstractItemView::item {
                background-color: #0e0e0e; color: #aaaaaa;
                padding: 8px 12px; margin: 1px; border-radius: 5px;
            }
            QComboBox QAbstractItemView::item:hover { background-color: #1a1a1a; color: #ffffff; }
            QComboBox QAbstractItemView::item:selected {
                background-color: #cc1e1e; color: white; font-weight: bold;
            }
        """

        form_widget = QWidget()
        form_widget.setStyleSheet("background: transparent;")
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(12)

        self.plano_combo = QComboBox()
        self.plano_combo.setEditable(True)
        self.carregar_planos()
        self.plano_combo.setStyleSheet(_field_style)
        label_plano = QLabel("Plano:")
        label_plano.setStyleSheet(_label_style)
        form_layout.addRow(label_plano, self.plano_combo)

        self.valor_input = QLineEdit()
        self.valor_input.setPlaceholderText("Digite o valor da mensalidade")
        self.valor_input.setStyleSheet(_field_style)
        label_valor = QLabel("Valor (R$):")
        label_valor.setStyleSheet(_label_style)
        form_layout.addRow(label_valor, self.valor_input)

        self.data_venc = QDateEdit()
        self.data_venc.setCalendarPopup(True)
        self.data_venc.setDisplayFormat("dd/MM/yyyy")
        self.data_venc.setStyleSheet(_field_style)
        label_data = QLabel("Data de Vencimento:")
        label_data.setStyleSheet(_label_style)
        form_layout.addRow(label_data, self.data_venc)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["PENDENTE", "PAGO", "VENCIDO"])
        self.status_combo.setStyleSheet(_field_style)
        label_status = QLabel("Status:")
        label_status.setStyleSheet(_label_style)
        form_layout.addRow(label_status, self.status_combo)

        self.obs_input = QTextEdit()
        self.obs_input.setMaximumHeight(70)
        self.obs_input.setPlaceholderText("Observações (opcional)")
        self.obs_input.setStyleSheet(_field_style)
        label_obs = QLabel("Observações:")
        label_obs.setStyleSheet(_label_style)
        form_layout.addRow(label_obs, self.obs_input)

        self.content_layout.addWidget(form_widget)

        btn_vincular = QPushButton("Vincular a Responsável")
        btn_vincular.setFixedHeight(34)
        btn_vincular.setStyleSheet("""
            QPushButton {
                background: #1e1e1e; color: #888888;
                border: 1px solid #2a2a2a; border-radius: 7px;
                font-size: 12px; font-weight: 500; padding: 0 14px;
            }
            QPushButton:hover { background: #252525; color: #cccccc; }
        """)
        btn_vincular.clicked.connect(self.vincular_mensalidade)
        buttons_area = QHBoxLayout()
        buttons_area.addWidget(btn_vincular)
        buttons_area.addStretch()
        self.content_layout.addLayout(buttons_area)

        self.add_button("Cancelar", self.reject, False)
        self.add_button("Salvar Alterações", self.salvar_alteracoes, True)

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
        # Mensalidades: id(0) aluno_id(1) valor(2) data_vencimento(3) data_pagamento(4)
        #               status(5) observacoes(6) criado_em(7) a.nome(8) a.plano(9)

        # Plano (índice 9 = a.plano da query)
        try:
            plano_atual = self.dados[9] if self.dados[9] else "Adulto - R$180"
            index = self.plano_combo.findText(plano_atual)
            if index >= 0:
                self.plano_combo.setCurrentIndex(index)
            else:
                self.plano_combo.setEditText(plano_atual)
        except Exception:
            pass

        # Valor
        self.valor_input.setText(str(self.dados[2]))  # valor

        # Data de vencimento
        try:
            data_venc = datetime.strptime(self.dados[3], "%Y-%m-%d").date()
            self.data_venc.setDate(QDate(data_venc.year, data_venc.month, data_venc.day))
        except Exception:
            self.data_venc.setDate(QDate.currentDate())

        # Status (índice 5)
        status = self.dados[5].upper() if self.dados[5] else "PENDENTE"
        index = self.status_combo.findText(status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)

        # Observações (índice 6)
        obs = self.dados[6] or ""
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


