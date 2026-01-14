from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        lbl = QLabel("Dashboard\n\n(Em desenvolvimento)")
        lbl.setStyleSheet("font-size:22px;")
        layout.addWidget(lbl)
