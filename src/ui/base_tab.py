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

    def get_button_style(self, width=120, height=36):
        """Retorna estilo padronizado para botões"""
        return f"""
            QPushButton {{
                font-size: 11px;
                font-weight: bold;
                padding: 8px 16px;
                min-width: {width}px;
                max-width: {width}px;
                min-height: {height}px;
                max-height: {height}px;
                background-color: rgba(52, 152, 219, 0.8);
                color: white;
                border: 2px solid transparent;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: rgba(52, 152, 219, 1.0);
            }}
            QPushButton:pressed {{
                background-color: rgba(41, 128, 185, 1.0);
                border: 2px solid rgba(52, 152, 219, 0.5);
            }}
        """

    def clear_layout(self, layout):
        """Limpa todos os widgets de um layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def clear_layout_recursive(self, layout):
        """Limpa recursivamente um layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout_recursive(child.layout())
