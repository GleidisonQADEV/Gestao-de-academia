from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class ConfigTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        lbl = QLabel("Configurações\n\n(Em breve)")
        lbl.setStyleSheet("font-size:22px;")
        layout.addWidget(lbl)
