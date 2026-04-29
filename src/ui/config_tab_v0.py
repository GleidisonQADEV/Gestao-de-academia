import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QGroupBox,
    QLineEdit, QFormLayout, QDialog, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from .base_tab_v0 import BaseTab
from .change_password_dialog import ChangePasswordDialog
from .app_dialog import AppDialog, show_info, show_error, show_question
from database.db import listar_planos, criar_plano, atualizar_plano, excluir_plano, plano_existe


class ConfigTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.build_ui()
        
    def build_ui(self):
        layout = self.layout()
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(20)

        # Título
        titulo = QLabel("⚙️ Configurações do Sistema")
        titulo.setStyleSheet("""
            color: white;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 20px;
        """)
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Container centralizado
        container = QWidget()
        container.setMaximumWidth(600)
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        
        # Seção Segurança
        seguranca_group = QGroupBox("🔐 Segurança")
        seguranca_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid rgba(255,255,255,0.2);
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        seguranca_layout = QVBoxLayout(seguranca_group)
        seguranca_layout.setSpacing(15)
        
        # Botão Trocar Senha
        btn_trocar_senha = QPushButton("🔑 Trocar Senha")
        btn_trocar_senha.setFixedHeight(50)
        btn_trocar_senha.setStyleSheet("""
            QPushButton {
                background-color: #e50914;
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
                border: none;
                text-align: left;
                padding-left: 20px;
            }
            QPushButton:hover {
                background-color: #ff1a24;
            }
            QPushButton:pressed {
                background-color: #c41e3a;
            }
        """)
        btn_trocar_senha.clicked.connect(self.trocar_senha)
        seguranca_layout.addWidget(btn_trocar_senha)
        
        # Descrição
        desc_senha = QLabel("Altere a senha de acesso ao sistema")
        desc_senha.setStyleSheet("""
            color: #cccccc;
            font-size: 12px;
            margin-left: 20px;
            margin-bottom: 10px;
        """)
        seguranca_layout.addWidget(desc_senha)
        
        container_layout.addWidget(seguranca_group)

        # Seção Planos
        planos_group = QGroupBox("💰 Gerenciamento de Planos")
        planos_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid rgba(255,255,255,0.2);
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        planos_layout = QVBoxLayout(planos_group)
        planos_layout.setSpacing(15)
        
        # Botão de gerenciamento
        btn_layout = QHBoxLayout()
        
        btn_novo_plano = QPushButton("➕ Novo Plano")
        btn_novo_plano.setFixedHeight(45)
        btn_novo_plano.setStyleSheet("""
            QPushButton {
                background-color: #e50914;
                color: white;
                border-radius: 10px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff1a24;
            }
        """)
        btn_novo_plano.clicked.connect(self.novo_plano)
        
        btn_layout.addWidget(btn_novo_plano)
        btn_layout.addStretch()
        
        planos_layout.addLayout(btn_layout)
        
        # Container scrollável para cards de planos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(255,255,255,0.1);
                border-radius: 6px;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background: rgba(229,9,20,0.7);
                border-radius: 6px;
                min-height: 20px;
            }
        """)
        
        self.cards_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        
        scroll_area.setWidget(self.cards_widget)
        scroll_area.setMaximumHeight(300)
        
        planos_layout.addWidget(scroll_area)
        
        # Descrição
        desc_planos = QLabel("Gerencie os planos disponíveis para cadastro de alunos")
        desc_planos.setStyleSheet("""
            color: #cccccc;
            font-size: 12px;
            margin-left: 20px;
            margin-bottom: 10px;
        """)
        planos_layout.addWidget(desc_planos)
        
        container_layout.addWidget(planos_group)
        
        # Carregar dados
        self.carregar_planos()
        
        # Centralizar container
        wrapper = QWidget()
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.addStretch()
        wrapper_layout.addWidget(container)
        wrapper_layout.addStretch()
        
        layout.addWidget(wrapper)
        layout.addStretch()
        
    def trocar_senha(self):
        """Abre dialog para trocar senha"""
        dialog = ChangePasswordDialog("admin")
        dialog.exec()
        
    def notificar_atualizacao_planos(self):
        """Notifica outras abas sobre atualização nos planos"""
        try:
            # Buscar a janela principal através da hierarquia de parents
            parent = self.parent()
            while parent and not hasattr(parent, 'cadastro_tab'):
                parent = parent.parent()
                
            if parent and hasattr(parent, 'cadastro_tab'):
                # Atualizar aba de cadastro
                if hasattr(parent.cadastro_tab, 'carregar_planos'):
                    parent.cadastro_tab.carregar_planos()
                    
                # Atualizar aba de alunos se tiver algum dialog de edição aberto
                if hasattr(parent, 'alunos_tab'):
                    alunos_tab = parent.alunos_tab
                    # Tentar encontrar dialogs de edição abertos
                    for child in alunos_tab.findChildren(QDialog):
                        if hasattr(child, 'plano') and hasattr(child, 'carregar_planos_edicao'):
                            child.carregar_planos_edicao()
                            
        except Exception as e:
            print(f"Erro ao notificar atualização de planos: {e}")
        
    def carregar_planos(self):
        """Carrega a lista de planos em cards"""
        try:
            # Limpar cards existentes
            while self.cards_layout.count():
                child = self.cards_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            planos = listar_planos()
            
            if not planos:
                # Mostrar mensagem quando não há planos
                sem_planos = QLabel("📝 Nenhum plano cadastrado")
                sem_planos.setStyleSheet("""
                    QLabel {
                        color: #cccccc;
                        font-size: 14px;
                        font-style: italic;
                        padding: 20px;
                        text-align: center;
                    }
                """)
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
        """Abre dialog para criar novo plano"""
        dialog = PlanoDialog(self, "Novo Plano")
        if dialog.exec() == QDialog.Accepted:
            self.carregar_planos()
            self.notificar_atualizacao_planos()
    
    def editar_plano(self):
        """Método legacy - agora usa cards individuais"""
        show_error(self, "Info", "Use o botão 'Editar' no card do plano desejado")
    
    def excluir_plano(self):
        """Método legacy - agora usa cards individuais"""
        show_error(self, "Info", "Use o botão 'Excluir' no card do plano desejado")
        
    def editar_plano_card(self, plano_id, nome, valor):
        """Edita plano a partir do card"""
        dialog = PlanoDialog(self, "Editar Plano", plano_id, nome, valor)
        if dialog.exec() == QDialog.Accepted:
            self.carregar_planos()
            self.notificar_atualizacao_planos()
    
    def excluir_plano_card(self, plano_id, nome):
        """Exclui plano a partir do card"""
        if show_question(self, "Confirmar Exclusão", f"Deseja realmente excluir o plano '{nome}'?"):
            try:
                excluir_plano(plano_id)
                show_info(self, "Sucesso", "Plano excluído com sucesso!")
                self.carregar_planos()
                self.notificar_atualizacao_planos()
            except Exception as e:
                show_error(self, "Erro ao excluir plano", f"Erro: {str(e)}")


class PlanoDialog(QDialog):
    """Dialog para criar/editar planos"""
    
    def __init__(self, parent, titulo, plano_id=None, nome="", valor=0.0):
        super().__init__(parent)
        self.plano_id = plano_id
        self.nome_inicial = nome
        self.valor_inicial = valor
        
        self.setWindowTitle(titulo)
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        # Aplicar estilo
        self.setStyleSheet("QDialog { background-color: #1e1e1e; }")
        
        self.build_ui()
        
    def build_ui(self):
        """Constrói a interface do dialog"""
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Card principal
        card = QFrame()
        card.setStyleSheet("background:white;border-radius:18px;")
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(20)
        
        # Título
        titulo_label = QLabel("Informações do Plano")
        titulo_label.setAlignment(Qt.AlignCenter)
        titulo_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #222;
            margin-bottom: 10px;
        """)
        card_layout.addWidget(titulo_label)
        
        # Nome do plano
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Ex: Família Premium")
        self.nome_input.setText(self.nome_inicial)
        self.nome_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                background-color: #f9f9f9;
                color: #222;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #e50914;
                background-color: white;
                color: #222;
            }
        """)
        
        # Valor do plano
        self.valor_input = QLineEdit()
        self.valor_input.setPlaceholderText("Ex: 250.00")
        if self.valor_inicial > 0:
            self.valor_input.setText(str(self.valor_inicial))
        self.valor_input.setStyleSheet(self.nome_input.styleSheet())
        
        # Formulário
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)
        
        # Labels com estilo
        label_style = "color: #222; font-weight: bold; font-size: 14px;"
        
        nome_label = QLabel("Nome do Plano:")
        nome_label.setStyleSheet(label_style)
        form_layout.addRow(nome_label, self.nome_input)
        
        valor_label = QLabel("Valor (R$):")
        valor_label.setStyleSheet(label_style)
        form_layout.addRow(valor_label, self.valor_input)
        
        # Dica
        dica = QLabel("💡 Digite 0 para plano gratuito")
        dica.setStyleSheet("color: #555; font-size: 12px; font-style: italic; margin-top: 10px;")
        form_layout.addRow("", dica)
        
        card_layout.addWidget(form_widget)
        
        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setAlignment(Qt.AlignCenter)
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(45)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
                padding: 8px 16px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)
        
        if self.plano_id:
            btn_salvar = QPushButton("💾 Salvar Alterações")
        else:
            btn_salvar = QPushButton("➕ Criar Plano")
            
        btn_salvar.setFixedHeight(45)
        btn_salvar.setStyleSheet("""
            QPushButton {
                background-color: #e50914;
                color: white;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
                padding: 8px 16px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #c41e3a;
            }
        """)
        btn_salvar.clicked.connect(self.salvar)
        
        btn_layout.addWidget(btn_cancelar)
        btn_layout.addWidget(btn_salvar)
        
        card_layout.addLayout(btn_layout)
        
        main_layout.addWidget(card)
    
    def salvar(self):
        """Salva o plano"""
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
        
        # Verificar se nome já existe
        if plano_existe(nome, self.plano_id):
            show_error(self, "Erro", "Já existe um plano com este nome")
            return
        
        try:
            if self.plano_id:
                # Editar
                atualizar_plano(self.plano_id, nome, valor)
                show_info(self, "Sucesso", "Plano atualizado com sucesso!")
            else:
                # Criar
                criar_plano(nome, valor)
                show_info(self, "Sucesso", "Plano criado com sucesso!")
            
            self.accept()
            
        except Exception as e:
            show_error(self, "Erro ao salvar plano", f"Erro: {str(e)}")


class PlanoCard(QFrame):
    """Card para exibir planos no estilo dos cards de alunos"""
    
    def __init__(self, plano_id, nome, valor):
        super().__init__()
        self.plano_id = plano_id
        self.nome = nome
        self.valor = valor
        
        # Callbacks para comunicação com parent
        self.editar_clicked = None
        self.excluir_clicked = None
        
        self.build_ui()
    
    def build_ui(self):
        self.setFixedSize(350, 120)
        self.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.1);
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.3);
                margin: 5px;
            }
            QFrame:hover {
                background: rgba(255,255,255,0.15);
                border: 1px solid rgba(255,255,255,0.5);
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        # Informações do plano
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        # Nome
        nome_label = QLabel(self.nome)
        nome_label.setStyleSheet("""
            QLabel {
                background: rgba(255,255,255,0.9);
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
        """)
        nome_label.setWordWrap(True)
        info_layout.addWidget(nome_label)
        
        # Valor
        if self.valor == 0:
            valor_texto = "Gratuito"
            cor_valor = "#28a745"  # Verde
        else:
            valor_texto = f"R$ {self.valor:.2f}"
            cor_valor = "#e50914"  # Vermelho
            
        valor_label = QLabel(valor_texto)
        valor_label.setStyleSheet(f"""
            QLabel {{
                background: rgba(255,255,255,0.8);
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
                font-weight: bold;
                color: {cor_valor};
            }}
        """)
        info_layout.addWidget(valor_label)
        
        layout.addLayout(info_layout)
        
        # Botões de ação
        botoes_layout = QVBoxLayout()
        botoes_layout.setSpacing(8)
        
        btn_editar = QPushButton("✏️")
        btn_editar.setFixedSize(35, 35)
        btn_editar.setStyleSheet("""
            QPushButton {
                background-color: #e50914;
                color: white;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff1a24;
            }
        """)
        btn_editar.setToolTip("Editar plano")
        btn_editar.clicked.connect(self.editar)
        
        btn_excluir = QPushButton("🗑️")
        btn_excluir.setFixedSize(35, 35)
        btn_excluir.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        btn_excluir.setToolTip("Excluir plano")
        btn_excluir.clicked.connect(self.excluir)
        
        botoes_layout.addWidget(btn_editar)
        botoes_layout.addWidget(btn_excluir)
        
        layout.addLayout(botoes_layout)
    
    def editar(self):
        """Emite sinal para editar plano"""
        if self.editar_clicked:
            self.editar_clicked(self.plano_id, self.nome, self.valor)
        else:
            # Fallback: buscar parent que tenha o método
            parent = self.parent()
            while parent:
                if hasattr(parent, 'editar_plano_card'):
                    parent.editar_plano_card(self.plano_id, self.nome, self.valor)
                    break
                parent = parent.parent()
    
    def excluir(self):
        """Emite sinal para excluir plano"""
        if self.excluir_clicked:
            self.excluir_clicked(self.plano_id, self.nome)
        else:
            # Fallback: buscar parent que tenha o método
            parent = self.parent()
            while parent:
                if hasattr(parent, 'excluir_plano_card'):
                    parent.excluir_plano_card(self.plano_id, self.nome)
                    break
                parent = parent.parent()
                
    # Métodos de callback para conectar sinais
    def set_editar_callback(self, callback):
        self.editar_clicked = callback
        
    def set_excluir_callback(self, callback):
        self.excluir_clicked = callback
