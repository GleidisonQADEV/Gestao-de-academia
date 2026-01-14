import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from database.db import init_db
from ui.login_window import LoginWindow
from ui.dashboard_tab import DashboardTab
from ui.alunos_tab import AlunosTab
from ui.cadastro_aluno_tab import CadastroAlunoTab
from ui.config_tab import ConfigTab


class MainWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Centro de Treinamento Legacy BJJ")
        self.resize(1200, 700)
        self.menu_buttons = []
        self.build_ui()

    def build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # -------- SIDEBAR --------
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(240)
        sidebar_widget.setStyleSheet("""
            background-color:#ffffff;
            border-right:1px solid #e5e7eb;
        """)

        sidebar = QVBoxLayout(sidebar_widget)
        sidebar.setAlignment(Qt.AlignTop)
        sidebar.setContentsMargins(10, 20, 10, 10)
        sidebar.setSpacing(8)

        # ----- LOGO -----
        logo = QLabel()
        pix = QPixmap("src/assets/logo.png")
        pix = pix.scaled(280, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pix)
        logo.setAlignment(Qt.AlignCenter)

        logo_wrap = QWidget()
        lw = QVBoxLayout(logo_wrap)
        lw.addWidget(logo)
        lw.setContentsMargins(0, 0, 0, 16)

        sidebar.addWidget(logo_wrap)

        # ----- MENU BUTTONS -----
        def menu_btn(text, idx):
            b = QPushButton(text)
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedHeight(42)
            b.setCheckable(True)
            b.setStyleSheet("""
                QPushButton{
                    border:none;
                    text-align:left;
                    padding-left:18px;
                    font-size:14px;
                    font-weight:600;
                    color:#111827;
                    border-radius:8px;
                }
                QPushButton:hover{
                    background:#f3f4f6;
                }
                QPushButton:checked{
                    background:#e5e7eb;
                    border-left:4px solid #111827;
                    padding-left:14px;
                }
            """)
            b.clicked.connect(lambda: self.change_page(idx, b))
            self.menu_buttons.append(b)
            return b

        sidebar.addWidget(menu_btn("Alunos", 0))
        sidebar.addWidget(menu_btn("Cadastrar Aluno", 1))
        sidebar.addWidget(menu_btn("Dashboard", 2))
        sidebar.addWidget(menu_btn("Configurações", 3))
        sidebar.addStretch()

        root.addWidget(sidebar_widget)

        # -------- CONTEÚDO --------
        self.stack = QStackedWidget()

        self.alunos_tab = AlunosTab()
        self.cadastro_tab = CadastroAlunoTab(refresh_callback=self.alunos_tab.load)
        self.dashboard_tab = DashboardTab()
        self.config_tab = ConfigTab()

        self.stack.addWidget(self.alunos_tab)
        self.stack.addWidget(self.cadastro_tab)
        self.stack.addWidget(self.dashboard_tab)
        self.stack.addWidget(self.config_tab)

        root.addWidget(self.stack)

        # página inicial
        self.menu_buttons[0].setChecked(True)

    def change_page(self, idx, btn):
        self.stack.setCurrentIndex(idx)
        for b in self.menu_buttons:
            b.setChecked(False)
        btn.setChecked(True)

    def show_window(self):
        self.show()


# --------- APP ---------

def abrir_sistema(user):
    global win
    win = MainWindow(user)
    win.show_window()


if __name__ == "__main__":
    init_db()

    app = QApplication(sys.argv)

    login = LoginWindow(on_success=abrir_sistema)
    login.show()

    sys.exit(app.exec())
