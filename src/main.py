import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget

from database.db import init_db
from ui.alunos_tab import AlunosTab
from ui.financeiro_tab import FinanceiroTab
from ui.alertas_tab import AlertasTab


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Academia Jiu-Jitsu - Sistema de Gestão")
        self.resize(900, 500)

        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.alertas_tab = AlertasTab()
        self.financeiro_tab = FinanceiroTab(refresh_callbacks=[self.alertas_tab.load])
        self.alunos_tab = AlunosTab(refresh_callbacks=[self.financeiro_tab.load, self.alertas_tab.load])

        self.tabs.addTab(self.alunos_tab, "Alunos")
        self.tabs.addTab(self.financeiro_tab, "Financeiro")
        self.tabs.addTab(self.alertas_tab, "Alertas")

        layout.addWidget(self.tabs)
        self.setLayout(layout)


if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
