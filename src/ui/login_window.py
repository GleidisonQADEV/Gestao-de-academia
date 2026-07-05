from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QHBoxLayout
)
from .app_dialog import show_warning, show_question, show_info
from PySide6.QtGui import QPixmap, QIcon, QPainter
from PySide6.QtCore import Qt, QSize
import os

from database.db import validar_login, get_conn


_EYE_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            ' stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>')
_EYE_OFF_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
                ' stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
                '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>'
                '<line x1="1" y1="1" x2="23" y2="23"/></svg>')


def _eye_icon(mostrar: bool, color="#888888", size=18):
    """Gera um QIcon de olho (aberto=senha visível / cortado=oculta)."""
    try:
        from PySide6.QtSvg import QSvgRenderer
        svg = _EYE_SVG if mostrar else _EYE_OFF_SVG
        renderer = QSvgRenderer(bytearray(svg.replace("currentColor", color).encode("utf-8")))
        pix = QPixmap(size, size)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)
        renderer.render(painter)
        painter.end()
        return QIcon(pix)
    except Exception:
        return QIcon()


class LoginWindow(QWidget):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.setWindowTitle("Centro de Treinamento Legacy BJJ")
        self.setFixedSize(420, 600)
        self.build_ui()

    def build_ui(self):
        # ----- Fundo geral -----
        self.setStyleSheet("QWidget { background-color: #111111; }")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # ----- Card central -----
        card = QFrame()
        card.setObjectName("card")
        card.setFixedSize(360, 520)
        card.setStyleSheet("""
            QFrame#card {
                background-color: #161616;
                border-radius: 14px;
                border: 1px solid #222222;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 24, 28, 24)
        card_layout.setSpacing(14)
        card_layout.setAlignment(Qt.AlignTop)

        # ----- Área da logo -----
        logo_frame = QFrame()
        logo_frame.setStyleSheet("QFrame { background: transparent; }")
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

        # Olho para mostrar/ocultar a senha
        self._senha_visivel = False
        self._eye_action = self.pass_input.addAction(
            _eye_icon(False), QLineEdit.TrailingPosition
        )
        self._eye_action.setToolTip("Mostrar senha")
        self._eye_action.triggered.connect(self._toggle_senha)

        input_style = """
            QLineEdit {
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #1e1e1e;
                background-color: #0e0e0e;
                font-size: 14px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #cc1e1e;
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
                background-color: #cc1e1e;
                color: white;
                border-radius: 6px;
                font-size: 15px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover  { background-color: #e02020; }
            QPushButton:pressed{ background-color: #a01515; }
        """)
        btn_login.clicked.connect(self.login)

        # Permite logar pressionando Enter em qualquer um dos campos.
        self.user_input.returnPressed.connect(self.login)
        self.pass_input.returnPressed.connect(self.login)
        
        # ----- Botão Restaurar Senha -----
        btn_restaurar = QPushButton("🔄 Restaurar Senha Padrão")
        btn_restaurar.setFixedHeight(35)
        btn_restaurar.setCursor(Qt.PointingHandCursor)
        btn_restaurar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #555555;
                border-radius: 6px;
                font-size: 12px;
                border: 1px solid #2a2a2a;
                margin-top: 6px;
            }
            QPushButton:hover {
                color: #888888;
                border-color: #444444;
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

    def _toggle_senha(self):
        """Alterna entre mostrar e ocultar a senha."""
        self._senha_visivel = not self._senha_visivel
        self.pass_input.setEchoMode(
            QLineEdit.Normal if self._senha_visivel else QLineEdit.Password
        )
        self._eye_action.setIcon(_eye_icon(self._senha_visivel))
        self._eye_action.setToolTip(
            "Ocultar senha" if self._senha_visivel else "Mostrar senha"
        )

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
