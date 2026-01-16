import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class BaseTab(QWidget):
    def __init__(self):
        super().__init__()

        # ----- ROOT LAYOUT -----
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(0)

        # ----- BACKGROUND LABEL -----
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)
        self.bg_label.lower()

        img_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "assets",
            "logobackground.png"
        )

        if os.path.exists(img_path):
            self.bg_label.setPixmap(QPixmap(img_path))

        # ----- CONTENT WIDGET (ON TOP OF BACKGROUND) -----
        self.content = QWidget(self)
        self.content.setAttribute(Qt.WA_TranslucentBackground)

        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(10)

        self.root.addWidget(self.content)

    # garante que o background sempre ocupe toda a aba
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())

    # permite usar: self.layout().addWidget(...)
    def layout(self):
        return self.content_layout
