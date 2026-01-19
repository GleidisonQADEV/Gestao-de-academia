import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout
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
        card.setFixedSize(360, 360)
        card.setStyleSheet("background:white;border-radius:18px;")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(16)

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
        text.setStyleSheet("font-size:14px;color:#111;")

        # ----- BOTÕES -----
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        for b in buttons:
            btn = QPushButton(b)
            btn.setFixedHeight(42)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color:#b00020;
                    color:white;
                    border-radius:12px;
                    font-weight:bold;
                }
                QPushButton:hover { background:#8c001a; }
            """)
            btn.clicked.connect(lambda _, x=b: self._click(x))
            btn_layout.addWidget(btn)

        # ----- MONTAGEM -----
        card_layout.addWidget(logo)
        card_layout.addWidget(text)
        card_layout.addStretch()
        card_layout.addLayout(btn_layout)

        main.addWidget(card)

    def _click(self, value):
        self.clicked = value
        self.accept()
