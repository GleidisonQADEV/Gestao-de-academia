from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QHBoxLayout
)
from .app_dialog import show_warning, show_question, show_info
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os

from database.db import validar_login, get_conn


class LoginWindow(QWidget):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.setWindowTitle("Centro de Treinamento Legacy BJJ")
        self.setFixedSize(420, 600)
        self.build_ui()

    def build_ui(self):
        # ----- Fundo geral -----
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # ----- Card central -----
        card = QFrame()
        card.setObjectName("card")
        card.setFixedSize(360, 520)
        card.setStyleSheet("""
            QFrame#card {
                background-color: #ffffff;
                border-radius: 18px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(18)
        card_layout.setAlignment(Qt.AlignTop)

        # ----- Área branca da logo -----
        logo_frame = QFrame()
        logo_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
            }
        """)
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setAlignment(Qt.AlignCenter)

        # ----- LOGO GRANDE -----
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
        logo_path = os.path.abspath(logo_path)

        pixmap = QPixmap(logo_path)
        pixmap = pixmap.scaled(280, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        logo_layout.addWidget(logo_label)

        # ----- Inputs -----
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuário")

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Senha")
        self.pass_input.setEchoMode(QLineEdit.Password)

        input_style = """
            QLineEdit {
                padding: 12px;
                border-radius: 10px;
                border: 1px solid #cccccc;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #b00020;
            }
        """
        self.user_input.setStyleSheet(input_style)
        self.pass_input.setStyleSheet(input_style)

        # ----- Botão -----
        btn_login = QPushButton("Entrar")
        btn_login.setFixedHeight(45)
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_login.setStyleSheet("""
            QPushButton {
                background-color: #b00020;
                color: white;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8c001a;
            }
        """)
        btn_login.clicked.connect(self.login)
        
        # ----- Botão Restaurar Senha -----
        btn_restaurar = QPushButton("🔄 Restaurar Senha Padrão")
        btn_restaurar.setFixedHeight(35)
        btn_restaurar.setCursor(Qt.PointingHandCursor)
        btn_restaurar.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border-radius: 8px;
                font-size: 12px;
                font-weight: normal;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        btn_restaurar.clicked.connect(self.restaurar_senha)

        # ----- Montagem -----
        card_layout.addWidget(logo_frame)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.user_input)
        card_layout.addWidget(self.pass_input)
        card_layout.addSpacing(10)
        card_layout.addWidget(btn_login)
        card_layout.addWidget(btn_restaurar)

        main_layout.addWidget(card)

    # ---------------- LOGIN ----------------

    def login(self):
        user = self.user_input.text().strip()
        senha = self.pass_input.text().strip()

        if not user or not senha:
            show_warning(self, "Erro", "Informe usuário e senha.")
            return

        ok = validar_login(user, senha)

        if ok:
            self.on_success(ok[0])
            self.close()
        else:
            show_warning(self, "Erro", "Usuário ou senha inválidos.")
            
    def restaurar_senha(self):
        """Restaura as credenciais para o padrão admin/senha"""
        resultado = show_question(
            self,
            "Restaurar Senha",
            "🔄 Esta ação irá restaurar as credenciais do sistema\npara o usuário e senha padrão.\n\n" +
            "Deseja continuar?",
            "Sim", "Cancelar"
        )
        
        if resultado:
            try:
                conn = get_conn()
                cur = conn.cursor()
                
                # Atualizar ou inserir usuário admin com senha padrão
                cur.execute("DELETE FROM users WHERE username='admin'")
                cur.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    ("admin", "senha")
                )
                
                conn.commit()
                conn.close()
                
                # Limpar campos e preencher com padrão
                self.user_input.setText("admin")
                self.pass_input.setText("senha")
                
                show_info(self, "Sucesso", "✅ Credenciais restauradas com sucesso!\n\nFaça login com o usuário e senha padrão.")
                
            except Exception as e:
                show_warning(self, "Erro", f"Erro ao restaurar credenciais: {str(e)}")
