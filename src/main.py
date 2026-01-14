import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget
)

from database.db import init_db
from ui.dashboard_tab import DashboardTab
from ui.alunos_tab import AlunosTab
from ui.financeiro_tab import FinanceiroTab
from ui.config_tab import ConfigTab


class MainWindow(QMainWindow):
    def __init__(self, usuario=None):
        super().__init__()

        self.setWindowTitle("Centro de Treinamento Legacy BJJ")
        self.resize(1200, 720)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ===== SIDEBAR =====
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(10)
        sidebar_layout.setContentsMargins(16, 16, 16, 16)

        titulo = QLabel("LEGACY BJJ")
        titulo.setStyleSheet("color:#111827;font-weight:700;")

        btn_alunos = QPushButton("Alunos")
        btn_fin = QPushButton("Financeiro")
        btn_dash = QPushButton("Dashboard")
        btn_cfg = QPushButton("Configurações")

        for btn in [btn_alunos, btn_fin, btn_dash, btn_cfg]:
            btn.setCheckable(True)

        self.menu_buttons = [btn_alunos, btn_fin, btn_dash, btn_cfg]

        sidebar_layout.addWidget(titulo)
        sidebar_layout.addSpacing(30)
        sidebar_layout.addWidget(btn_alunos)
        sidebar_layout.addWidget(btn_fin)
        sidebar_layout.addWidget(btn_dash)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(btn_cfg)

        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setLayout(sidebar_layout)
        sidebar.setFixedWidth(220)

        # ===== STACK =====
        self.stack = QStackedWidget()

        self.alunos = AlunosTab(refresh_all=self.refresh_all)
        self.financeiro = FinanceiroTab()
        self.dashboard = DashboardTab()
        self.config = ConfigTab()

        self.stack.addWidget(self.alunos)
        self.stack.addWidget(self.financeiro)
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.config)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

        # ===== AÇÕES =====
        btn_alunos.clicked.connect(lambda: self.switch(btn_alunos, self.alunos))
        btn_fin.clicked.connect(lambda: self.switch(btn_fin, self.financeiro))
        btn_dash.clicked.connect(lambda: self.switch(btn_dash, self.dashboard))
        btn_cfg.clicked.connect(lambda: self.switch(btn_cfg, self.config))

        btn_alunos.setChecked(True)
        self.open_page(self.alunos)

    def open_page(self, widget):
        self.stack.setCurrentWidget(widget)

    def switch(self, btn, page):
        for b in self.menu_buttons:
            b.setChecked(False)
        btn.setChecked(True)
        self.open_page(page)

    def refresh_all(self):
        try:
            self.dashboard.load()
            self.financeiro.load()
        except:
            pass


if __name__ == "__main__":
    init_db()

    app = QApplication(sys.argv)

    try:
        with open("src/ui/style.qss", "r") as f:
            app.setStyleSheet(f.read())
    except:
        pass

    from ui.login_window import LoginWindow

    def abrir(usuario):
        win = MainWindow(usuario)
        win.show()

    login = LoginWindow(on_success=abrir)
    login.show()

    sys.exit(app.exec())
