import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout, QLineEdit, QComboBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


_BTN_PRIMARY = """
    QPushButton {
        background: #cc1e1e; color: #ffffff; border: none;
        border-radius: 6px; font-size: 13px; font-weight: 600;
        padding: 6px 16px; min-width: 90px;
    }
    QPushButton:hover  { background: #e02020; }
    QPushButton:pressed{ background: #a01515; }
"""

_BTN_SECONDARY = """
    QPushButton {
        background: #1e1e1e; color: #888888;
        border: 1px solid #2a2a2a; border-radius: 6px;
        font-size: 13px; font-weight: 500;
        padding: 6px 16px; min-width: 90px;
    }
    QPushButton:hover { background: #252525; color: #cccccc; }
"""


class AppDialog(QDialog):
    def __init__(self, title, message, buttons=("OK",), parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.clicked = None
        self.build_ui(title, message, buttons)

    def build_ui(self, title, message, buttons):
        self.setObjectName("appDialog")
        self.setStyleSheet("#appDialog { background: #111111; }")

        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("appDialogCard")
        card.setStyleSheet(
            "#appDialogCard { background: #161616; border-radius: 12px; border: 1px solid #222222; }"
        )

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 24, 28, 24)
        card_layout.setSpacing(14)
        card_layout.setAlignment(Qt.AlignCenter)

        # Logo
        logo = QLabel()
        logo_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
        )
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(pix)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("background: transparent; border: none;")
        card_layout.addWidget(logo)

        # Título
        lbl_title = QLabel(title)
        lbl_title.setWordWrap(True)
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet(
            "font-size:15px; font-weight:700; color:#ffffff;"
            " background:transparent; border:none; padding: 0 10px;"
        )
        card_layout.addWidget(lbl_title)

        # Mensagem
        lbl_msg = QLabel(message)
        lbl_msg.setWordWrap(True)
        lbl_msg.setAlignment(Qt.AlignCenter)
        lbl_msg.setStyleSheet(
            "font-size:13px; color:#888888; line-height:1.5;"
            " background:transparent; border:none; padding: 0 10px;"
        )
        lbl_msg.setMinimumWidth(300)
        lbl_msg.setMaximumWidth(480)
        card_layout.addWidget(lbl_msg)

        card_layout.addStretch()

        # Botões — primeiro é primário, demais são secundários
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.setAlignment(Qt.AlignCenter)

        for i, b in enumerate(buttons):
            btn = QPushButton(b)
            btn.setFixedHeight(38)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(_BTN_PRIMARY if i == 0 else _BTN_SECONDARY)
            btn.clicked.connect(lambda _, x=b: self._click(x))
            btn_layout.addWidget(btn)

        card_layout.addLayout(btn_layout)
        main.addWidget(card)

        self.adjustSize()
        w, h = max(self.width(), 420), max(self.height(), 220)
        self.resize(min(w, 620), min(h, 560))

    def _click(self, value):
        self.clicked = value
        self.accept()


class InputDialog(QDialog):
    def __init__(self, title, message, placeholder="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.input_text = ""
        self.accepted_input = False
        self.build_ui(message, placeholder)

    def build_ui(self, message, placeholder):
        self.setObjectName("inputDialog")
        self.setStyleSheet("#inputDialog { background: #111111; }")

        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("inputDialogCard")
        card.setStyleSheet(
            "#inputDialogCard { background: #161616; border-radius: 12px; border: 1px solid #222222; }"
        )

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 24, 28, 24)
        card_layout.setSpacing(14)
        card_layout.setAlignment(Qt.AlignCenter)

        # Logo
        logo = QLabel()
        logo_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
        )
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(pix)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("background: transparent; border: none;")
        card_layout.addWidget(logo)

        lbl_msg = QLabel(message)
        lbl_msg.setWordWrap(True)
        lbl_msg.setAlignment(Qt.AlignCenter)
        lbl_msg.setStyleSheet(
            "font-size:13px; color:#cccccc; background:transparent; border:none; padding: 0 10px;"
        )
        card_layout.addWidget(lbl_msg)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(placeholder)
        self.input_field.setFixedHeight(42)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #0e0e0e; padding: 8px 10px;
                border-radius: 8px; border: 1px solid #1e1e1e;
                font-size: 13px; color: #cccccc;
            }
            QLineEdit:focus { border: 1.5px solid #cc1e1e; }
        """)
        card_layout.addWidget(self.input_field)

        card_layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.setAlignment(Qt.AlignCenter)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet(_BTN_SECONDARY)
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("OK")
        btn_ok.setFixedHeight(38)
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.setStyleSheet(_BTN_PRIMARY)
        btn_ok.clicked.connect(self.accept_input)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        card_layout.addLayout(btn_layout)

        main.addWidget(card)

        self.input_field.setFocus()
        self.input_field.returnPressed.connect(self.accept_input)
        self.adjustSize()
        self.resize(max(self.width(), 420), max(self.height(), 280))

    def accept_input(self):
        self.input_text = self.input_field.text()
        self.accepted_input = True
        self.accept()

    def get_text(self):
        return self.input_text, self.accepted_input


# ================= FUNÇÕES AUXILIARES =================

def show_info(parent, title, message):
    dialog = AppDialog(title, message, ("OK",), parent)
    dialog.exec()
    return dialog.clicked

def show_warning(parent, title, message):
    dialog = AppDialog(title, message, ("OK",), parent)
    dialog.exec()
    return dialog.clicked

def show_error(parent, title, message):
    dialog = AppDialog(title, message, ("OK",), parent)
    dialog.exec()
    return dialog.clicked

def show_question(parent, title, message, yes_text="Sim", no_text="Não"):
    # yes_text é primário (vermelho), no_text é secundário (cinza)
    dialog = AppDialog(title, message, (yes_text, no_text), parent)
    dialog.exec()
    return dialog.clicked == yes_text

def show_custom(parent, title, message, buttons):
    dialog = AppDialog(title, message, buttons, parent)
    dialog.exec()
    return dialog.clicked

def show_input(parent, title, message, placeholder=""):
    dialog = InputDialog(title, message, placeholder, parent)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_text()
    return "", False


class ComboDialog(QDialog):
    def __init__(self, title, message, options, default=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.selected = ""
        self.accepted_input = False

        self.setStyleSheet("#comboDialog { background: #111111; }")
        self.setObjectName("comboDialog")

        main = QVBoxLayout(self)
        main.setContentsMargins(24, 22, 24, 20)
        main.setSpacing(14)

        lbl = QLabel(message)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("font-size:13px; color:#cccccc; background:transparent; border:none;")
        main.addWidget(lbl)

        self.combo = QComboBox()
        self.combo.addItems(list(options))
        self.combo.setFixedHeight(40)
        self.combo.setStyleSheet("""
            QComboBox {
                background-color: #0e0e0e; padding: 8px 10px;
                border-radius: 8px; border: 1px solid #1e1e1e;
                font-size: 13px; color: #ffffff;
            }
            QComboBox:focus { border: 1.5px solid #cc1e1e; }
            QComboBox QAbstractItemView {
                background-color: #0e0e0e; border: 1px solid #cc1e1e;
                selection-background-color: #cc1e1e; selection-color: white;
                color: #cccccc; outline: none;
            }
        """)
        if default:
            idx = self.combo.findText(default)
            if idx >= 0:
                self.combo.setCurrentIndex(idx)
        main.addWidget(self.combo)

        btns = QHBoxLayout()
        btns.setSpacing(10)
        btns.addStretch()
        b_cancel = QPushButton("Cancelar")
        b_cancel.setCursor(Qt.PointingHandCursor)
        b_cancel.setStyleSheet(_BTN_SECONDARY)
        b_cancel.clicked.connect(self.reject)
        b_ok = QPushButton("OK")
        b_ok.setCursor(Qt.PointingHandCursor)
        b_ok.setStyleSheet(_BTN_PRIMARY)
        b_ok.clicked.connect(self._ok)
        btns.addWidget(b_cancel)
        btns.addWidget(b_ok)
        main.addLayout(btns)

        self.resize(420, 200)

    def _ok(self):
        self.selected = self.combo.currentText()
        self.accepted_input = True
        self.accept()


def show_combo(parent, title, message, options, default=None):
    """Mostra um seletor (combo). Retorna (valor, ok)."""
    dialog = ComboDialog(title, message, options, default, parent)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.selected, dialog.accepted_input
    return "", False
