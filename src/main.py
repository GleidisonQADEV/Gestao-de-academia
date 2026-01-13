import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QMenuBar
)

from database.db import init_db
from ui.login_window import LoginWindow
from ui.change_password_dialog import ChangePasswordDialog
from ui.alunos_tab import AlunosTab
from ui.financeiro_tab import FinanceiroTab
from ui.alertas_tab import AlertasTab


class MainWindow(QMainWindow):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Academia Jiu-Jitsu - Sistema de Gestão")
        self.resize(900, 520)

        # -------- MENU --------
        menu = self.menuBar()
        config = menu.addMenu("Configurações")
        act_senha = config.addAction("Trocar senha")
        act_senha.triggered.connect(self.trocar_senha)

        # -------- CENTRAL WIDGET --------
        central = QWidget()
        self.setCentralWidget(central)

        self.tabs = QTabWidget(central)

        self.alertas_tab = AlertasTab()
        self.financeiro_tab = FinanceiroTab(refresh_callbacks=[self.alertas_tab.load])
        self.alunos_tab = AlunosTab(refresh_all=self.refresh_telas)

        self.tabs.addTab(self.alunos_tab, "Alunos")
        self.tabs.addTab(self.financeiro_tab, "Financeiro")
        self.tabs.addTab(self.alertas_tab, "Alertas")

        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(central)
        layout.addWidget(self.tabs)

    def refresh_telas(self):
        self.financeiro_tab.load()
        self.alertas_tab.load()

    def trocar_senha(self):
        dlg = ChangePasswordDialog(self.usuario)
        dlg.exec()


def main():
    init_db()
    app = QApplication(sys.argv)

    main_win = {"win": None}

    def abrir_sistema(usuario):
        main_win["win"] = MainWindow(usuario)
        main_win["win"].show()

    login = LoginWindow(on_success=abrir_sistema)
    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
