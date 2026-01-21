import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout, QLineEdit
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class AppDialog(QDialog):
    def __init__(self, title, message, buttons=("OK",), parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(420, 420)
        self.setModal(True)
        self.clicked = None
        self.build_ui(message, buttons)

    def build_ui(self, message, buttons):
        self.setStyleSheet("QDialog { background-color: #1e1e1e; }")

        main = QVBoxLayout(self)
        main.setAlignment(Qt.AlignCenter)

        # ----- CARD -----
        card = QFrame()
        card.setStyleSheet("background:white;border-radius:18px;")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(16)
        card_layout.setAlignment(Qt.AlignCenter)

        # ----- LOGO -----
        logo = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
        logo_path = os.path.abspath(logo_path)

        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(pix)

        logo.setAlignment(Qt.AlignCenter)

        # ----- TEXTO -----
        text = QLabel(message)
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignCenter)
        text.setStyleSheet("font-size:14px;color:#111;line-height:1.5;padding:15px;")
        text.setMinimumWidth(350)
        text.setMaximumWidth(500)

        # ----- BOTÕES -----
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setAlignment(Qt.AlignCenter)

        for b in buttons:
            btn = QPushButton(b)
            btn.setFixedHeight(45)  # Mesma altura do botão de login
            btn.setCursor(Qt.PointingHandCursor)
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
            btn.clicked.connect(lambda _, x=b: self._click(x))
            btn_layout.addWidget(btn)

        # ----- MONTAGEM -----
        card_layout.addWidget(logo)
        card_layout.addWidget(text)
        card_layout.addStretch()
        card_layout.addLayout(btn_layout)

        main.addWidget(card)
        
        # Redimensionamento simples e eficaz
        self.adjustSize()
        
        # Garantir tamanho mínimo adequate
        if self.width() < 450:
            self.resize(450, self.height())
        if self.height() < 200:
            self.resize(self.width(), 200)
            
        # Limitar tamanho máximo
        if self.width() > 700:
            self.resize(700, self.height())
        if self.height() > 600:
            self.resize(self.width(), 600)

    def _click(self, value):
        self.clicked = value
        self.accept()


class InputDialog(QDialog):
    def __init__(self, title, message, placeholder="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(450, 300)
        self.setModal(True)
        self.input_text = ""
        self.accepted_input = False
        self.build_ui(message, placeholder)

    def build_ui(self, message, placeholder):
        self.setStyleSheet("QDialog { background-color: #1e1e1e; }")

        main = QVBoxLayout(self)
        main.setAlignment(Qt.AlignCenter)

        # ----- CARD -----
        card = QFrame()
        card.setStyleSheet("background:white;border-radius:18px;")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(16)
        card_layout.setAlignment(Qt.AlignCenter)

        # ----- LOGO -----
        logo = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
        logo_path = os.path.abspath(logo_path)

        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(pix)

        logo.setAlignment(Qt.AlignCenter)

        # ----- TEXTO -----
        text = QLabel(message)
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignCenter)
        text.setStyleSheet("font-size:14px;color:#111;line-height:1.5;padding:10px;")

        # ----- CAMPO DE INPUT -----
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(placeholder)
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                background-color: white;
                color: #333;
            }
            QLineEdit:focus {
                border-color: #b00020;
                outline: none;
            }
        """)
        self.input_field.setFixedHeight(45)

        # ----- BOTÕES -----
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setAlignment(Qt.AlignCenter)

        # Botão Cancelar
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(45)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet("""
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
        btn_cancel.clicked.connect(self.reject)

        # Botão OK
        btn_ok = QPushButton("OK")
        btn_ok.setFixedHeight(45)
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.setStyleSheet("""
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
        btn_ok.clicked.connect(self.accept_input)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)

        # ----- MONTAGEM -----
        card_layout.addWidget(logo)
        card_layout.addWidget(text)
        card_layout.addWidget(self.input_field)
        card_layout.addStretch()
        card_layout.addLayout(btn_layout)

        main.addWidget(card)

        # Focar no campo de input
        self.input_field.setFocus()
        
        # Enter confirma
        self.input_field.returnPressed.connect(self.accept_input)

    def accept_input(self):
        self.input_text = self.input_field.text()
        self.accepted_input = True
        self.accept()

    def get_text(self):
        return self.input_text, self.accepted_input


# ================= FUNÇÕES AUXILIARES =================

def show_info(parent, title, message):
    """Mostra diálogo de informação"""
    dialog = AppDialog(title, message, ("OK",), parent)
    dialog.exec()
    return dialog.clicked

def show_warning(parent, title, message):
    """Mostra diálogo de aviso"""
    dialog = AppDialog(f"⚠️  {title}", message, ("OK",), parent)
    dialog.exec()
    return dialog.clicked

def show_error(parent, title, message):
    """Mostra diálogo de erro"""
    dialog = AppDialog(f"❌ {title}", message, ("OK",), parent)
    dialog.exec()
    return dialog.clicked

def show_question(parent, title, message, yes_text="Sim", no_text="Não"):
    """Mostra diálogo de pergunta com opções sim/não"""
    dialog = AppDialog(f"❓ {title}", message, (yes_text, no_text), parent)
    dialog.exec()
    return dialog.clicked == yes_text

def show_custom(parent, title, message, buttons):
    """Mostra diálogo customizado com botões específicos"""
    dialog = AppDialog(title, message, buttons, parent)
    dialog.exec()
    return dialog.clicked

def show_input(parent, title, message, placeholder=""):
    """Mostra diálogo de entrada de texto personalizado"""
    dialog = InputDialog(title, message, placeholder, parent)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_text()
    return "", False
