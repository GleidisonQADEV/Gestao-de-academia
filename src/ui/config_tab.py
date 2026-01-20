import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from .base_tab import BaseTab
from .change_password_dialog import ChangePasswordDialog


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
