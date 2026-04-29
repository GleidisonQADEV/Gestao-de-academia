from PySide6.QtWidgets import QWidget, QVBoxLayout


SCROLLBAR_STYLE = """
    QScrollBar:vertical {
        background: #111111;
        width: 6px;
        border-radius: 3px;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background: #333333;
        border-radius: 3px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover { background: #cc1e1e; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0; border: none; background: none;
    }
    QScrollBar:horizontal {
        background: #111111;
        height: 6px;
        border-radius: 3px;
        margin: 0;
    }
    QScrollBar::handle:horizontal {
        background: #333333;
        border-radius: 3px;
        min-width: 20px;
    }
    QScrollBar::handle:horizontal:hover { background: #cc1e1e; }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0; border: none; background: none;
    }
"""


class BaseTab(QWidget):
    def __init__(self):
        super().__init__()

        # ROOT LAYOUT
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(0)

        # CONTENT WIDGET (preenche tudo, fundo escuro)
        self.content = QWidget(self)
        self.content.setStyleSheet("background: #111111;")

        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(10)

        self.root.addWidget(self.content)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.content.setGeometry(0, 0, self.width(), self.height())

    def layout(self):
        return self.content_layout

    def get_button_style(self, width=120, height=36):
        return f"""
            QPushButton {{
                font-size: 12px;
                font-weight: bold;
                padding: 8px 16px;
                min-width: {width}px;
                max-width: {width}px;
                min-height: {height}px;
                max-height: {height}px;
                background-color: #cc1e1e;
                color: #ffffff;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{ background-color: #e02020; }}
            QPushButton:pressed {{ background-color: #a01515; }}
        """

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def clear_layout_recursive(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout_recursive(child.layout())
