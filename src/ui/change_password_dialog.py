from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt
from .app_dialog import show_warning, show_info
from database.db import get_conn
import os


class ChangePasswordDialog(QDialog):
    def __init__(self, usuario="admin"):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Trocar Senha")
        self.resize(450, 320)
        self.setModal(True)
        
        # Estilo do dialog igual aos outros
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e,
                    stop:1 #16213e
                );
                background-image: url({os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logobackground.png')});
                background-repeat: no-repeat;
                background-position: center;
            }}
            QLabel {{
                color: white;
                font-size: 13px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            QLineEdit {{
                background-color: rgba(255,255,255,0.95);
                padding: 8px 12px;
                border-radius: 8px;
                border: 1.5px solid #ccc;
                font-size: 13px;
                color: #111;
                margin-bottom: 15px;
            }}
            QLineEdit:focus {{
                border: 1.5px solid #e50914;
            }}
            QPushButton {{
                background-color: #e50914;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #ff1a24;
            }}
            QPushButton:pressed {{
                background-color: #c41e3a;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = QLabel("🔐 Alterar Senha do Sistema")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: white; margin-bottom: 20px;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        layout.addWidget(QLabel("Senha Atual:"))
        self.atual = QLineEdit()
        self.atual.setEchoMode(QLineEdit.Password)
        self.atual.setPlaceholderText("Digite sua senha atual")
        layout.addWidget(self.atual)

        layout.addWidget(QLabel("Nova Senha:"))
        self.nova = QLineEdit()
        self.nova.setEchoMode(QLineEdit.Password)
        self.nova.setPlaceholderText("Digite a nova senha")
        layout.addWidget(self.nova)

        layout.addWidget(QLabel("Confirmar Nova Senha:"))
        self.conf = QLineEdit()
        self.conf.setEchoMode(QLineEdit.Password)
        self.conf.setPlaceholderText("Digite novamente a nova senha")
        layout.addWidget(self.conf)

        # Botões
        btn_layout = QHBoxLayout()
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)
        
        btn_alterar = QPushButton("Alterar Senha")
        btn_alterar.clicked.connect(self.alterar)
        
        btn_layout.addWidget(btn_cancelar)
        btn_layout.addWidget(btn_alterar)
        layout.addLayout(btn_layout)

    def alterar(self):
        # Validações
        if not self.atual.text().strip():
            show_warning(self, "Erro", "Digite a senha atual")
            return
            
        if not self.nova.text().strip():
            show_warning(self, "Erro", "Digite a nova senha")
            return
            
        if len(self.nova.text()) < 3:
            show_warning(self, "Erro", "Nova senha deve ter pelo menos 3 caracteres")
            return

        if self.nova.text() != self.conf.text():
            show_warning(self, "Erro", "As senhas não conferem")
            return

        conn = get_conn()
        cur = conn.cursor()

        # Verificar senha atual
        cur.execute(
            "SELECT id FROM users WHERE username=? AND password=?",
            (self.usuario, self.atual.text())
        )

        if not cur.fetchone():
            show_warning(self, "Erro", "Senha atual incorreta")
            conn.close()
            return

        # Atualizar senha
        cur.execute(
            "UPDATE users SET password=? WHERE username=?",
            (self.nova.text(), self.usuario)
        )

        conn.commit()
        conn.close()

        show_info(self, "Sucesso", "✅ Senha alterada com sucesso!")
        self.accept()
