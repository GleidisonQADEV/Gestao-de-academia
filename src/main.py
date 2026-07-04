import sys
import os

from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget, QFrame, QProgressDialog
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QPixmap, QColor, QIcon

from database.db import init_db
from database.kids_db import init_kids_db
from ui.updater import UpdateChecker, Downloader, open_installer
from ui.app_dialog import show_question, show_error, show_info
from version import APP_VERSION, GITHUB_REPO

from ui.login_window import LoginWindow

from ui.alunos_tab import AlunosTab
from ui.dashboard_tab import DashboardTab
from ui.cadastro_aluno_tab import CadastroAlunoTab
from ui.financeiro_tab import FinanceiroTab
from ui.config_tab import ConfigTab


_MENU_GROUPS = [
    ("PRINCIPAL", [
        ("Dashboard",       1),
        ("Alunos",          0),
        ("Cadastrar Aluno", 2),
    ]),
    ("GESTÃO", [
        ("Financeiro",      3),
        ("Configurações",   4),
    ]),
]

_SVG_ICONS = {
    "Dashboard":       '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
    "Alunos":          '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>',
    "Cadastrar Aluno": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/></svg>',
    "Financeiro":      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>',
    "Configurações":   '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>',
}


def _make_nav_icon(svg_str, color="#555555", size=14):
    try:
        from PySide6.QtSvg import QSvgRenderer
        from PySide6.QtGui import QPixmap, QPainter
        colored = svg_str.replace("currentColor", color)
        renderer = QSvgRenderer(bytearray(colored.encode("utf-8")))
        pix = QPixmap(size, size)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)
        renderer.render(painter)
        painter.end()
        return QIcon(pix)
    except Exception:
        return QIcon()


class MainWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Centro de Treinamento Legacy BJJ")
        self.resize(1200, 700)
        self.setStyleSheet("QWidget { background: #111111; }")
        self.menu_buttons = []
        self.build_ui()

    def build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ─────────── SIDEBAR ───────────
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebarWidget")
        sidebar_widget.setFixedWidth(200)
        sidebar_widget.setStyleSheet("""
            #sidebarWidget {
                background-color: #0e0e0e;
                border-right: 1px solid #1e1e1e;
            }
        """)

        sidebar = QVBoxLayout(sidebar_widget)
        sidebar.setAlignment(Qt.AlignTop)
        sidebar.setContentsMargins(0, 0, 0, 0)
        sidebar.setSpacing(0)

        # ── LOGO AREA ──
        logo_area = QWidget()
        logo_area.setObjectName("logoArea")
        logo_area.setStyleSheet("""
            #logoArea {
                background: transparent;
                border-bottom: 1px solid #1e1e1e;
            }
        """)
        logo_area_layout = QVBoxLayout(logo_area)
        logo_area_layout.setContentsMargins(16, 20, 16, 14)
        logo_area_layout.setSpacing(0)
        logo_area_layout.setAlignment(Qt.AlignCenter)

        _logo_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png"
        )
        logo_label = QLabel()
        pix = QPixmap(_logo_path)
        if not pix.isNull():
            logo_label.setPixmap(
                pix.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("background: transparent;")
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        from PySide6.QtGui import QColor as _QColor
        _shadow = QGraphicsDropShadowEffect()
        _shadow.setBlurRadius(8)
        _shadow.setOffset(0, 0)
        _shadow.setColor(_QColor(204, 30, 30, 77))
        logo_label.setGraphicsEffect(_shadow)

        title_label = QLabel("LEGACY BJJ")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: #ffffff;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 1.5px;
            background: transparent;
            margin-top: 8px;
        """)

        subtitle_label = QLabel("Centro de Treinamento")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            color: #444444;
            font-size: 10px;
            font-weight: 400;
            letter-spacing: 0.5px;
            background: transparent;
            margin-top: 1px;
        """)

        logo_area_layout.addWidget(logo_label)
        logo_area_layout.addWidget(title_label)
        logo_area_layout.addWidget(subtitle_label)
        sidebar.addWidget(logo_area)

        # ── MENU BUTTONS ──
        def section_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("""
                color: #2e2e2e;
                font-size: 10px;
                font-weight: 500;
                letter-spacing: 1.5px;
                background: transparent;
                padding: 12px 16px 5px 16px;
            """)
            return lbl

        def menu_btn(text, idx):
            b = QPushButton(f"  {text}")
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedHeight(38)
            b.setCheckable(True)
            if text in _SVG_ICONS:
                b.setIcon(_make_nav_icon(_SVG_ICONS[text]))
                b.setIconSize(QSize(14, 14))
            b.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-left: 2px solid transparent;
                    text-align: left;
                    padding: 9px 16px;
                    font-size: 13px;
                    font-weight: 400;
                    color: #555555;
                    background: transparent;
                    border-radius: 0px;
                }
                QPushButton:hover {
                    color: #cccccc;
                    background: #141414;
                }
                QPushButton:checked {
                    color: #ffffff;
                    background: #141414;
                    border-left: 2px solid #cc1e1e;
                    font-weight: 500;
                }
            """)
            b.clicked.connect(lambda: self.change_page(idx, b))
            self.menu_buttons.append(b)
            return b

        for section, items in _MENU_GROUPS:
            sidebar.addWidget(section_label(section))
            for label, idx in items:
                sidebar.addWidget(menu_btn(label, idx))

        sidebar.addStretch()

        # ── RODAPÉ: separador + sair ──
        footer = QWidget()
        footer.setObjectName("sidebarFooter")
        footer.setStyleSheet("""
            #sidebarFooter {
                background: transparent;
                border-top: 1px solid #1e1e1e;
            }
        """)
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(0)

        _sair_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>'
        btn_sair = QPushButton("  Sair")
        btn_sair.setIcon(_make_nav_icon(_sair_svg, color="#333333", size=14))
        btn_sair.setIconSize(QSize(14, 14))
        _icon_normal = _make_nav_icon(_sair_svg, color="#333333", size=14)
        _icon_hover  = _make_nav_icon(_sair_svg, color="#cc1e1e", size=14)
        btn_sair.enterEvent = lambda e: btn_sair.setIcon(_icon_hover)
        btn_sair.leaveEvent = lambda e: btn_sair.setIcon(_icon_normal)
        btn_sair.setCursor(Qt.PointingHandCursor)
        btn_sair.setFixedHeight(38)
        btn_sair.setStyleSheet("""
            QPushButton {
                border: none;
                border-left: 2px solid transparent;
                text-align: left;
                padding: 9px 16px;
                font-size: 12px;
                font-weight: 400;
                color: #333333;
                background: transparent;
                border-radius: 0px;
            }
            QPushButton:hover {
                color: #cc1e1e;
                background: transparent;
            }
        """)
        btn_sair.clicked.connect(self.confirmar_sair)

        # ── Botão de atualização (oculto até detectar nova versão) ──
        self._btn_update = QPushButton("  Nova versão disponível")
        self._btn_update.setFixedHeight(34)
        self._btn_update.setCursor(Qt.PointingHandCursor)
        self._btn_update.setVisible(False)
        self._btn_update.setStyleSheet("""
            QPushButton {
                background: rgba(26,122,60,0.12); color: #2d8a52;
                border: 1px solid rgba(26,122,60,0.3); border-radius: 6px;
                font-size: 11px; font-weight: 600;
                text-align: left; padding: 0 12px;
                margin: 4px 8px 0 8px;
            }
            QPushButton:hover { background: rgba(26,122,60,0.2); }
        """)
        self._btn_update.clicked.connect(self._iniciar_download_update)
        footer_layout.addWidget(self._btn_update)

        footer_layout.addWidget(btn_sair)
        sidebar.addWidget(footer)

        root.addWidget(sidebar_widget)

        # ─────────── CONTEÚDO ───────────
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: #111111;")

        self.alunos_tab     = AlunosTab()
        self.dashboard_tab  = DashboardTab()
        self.cadastro_tab   = CadastroAlunoTab(refresh_callback=self.alunos_tab.load)
        self.financeiro_tab = FinanceiroTab()
        self.config_tab     = ConfigTab()

        self.stack.addWidget(self.alunos_tab)
        self.stack.addWidget(self.dashboard_tab)
        self.stack.addWidget(self.cadastro_tab)
        self.stack.addWidget(self.financeiro_tab)
        self.stack.addWidget(self.config_tab)

        self.stack.setCurrentIndex(1)
        root.addWidget(self.stack)

        if self.menu_buttons:
            self.menu_buttons[0].setChecked(True)
            self.alunos_tab.nav_cadastro = lambda: self.change_page(2, self.menu_buttons[2])

        # Checar atualizações em background após 3 s (não bloqueia a inicialização)
        QTimer.singleShot(3000, self._iniciar_checagem_update)
        self._update_version = None

    def change_page(self, idx, btn):
        self.stack.setCurrentIndex(idx)
        for b in self.menu_buttons:
            b.setChecked(False)
        btn.setChecked(True)

        if idx == 0:
            self.alunos_tab.load()
        elif idx == 1:
            self.dashboard_tab.load()
        elif idx == 3:
            self.financeiro_tab.load()

    def _iniciar_checagem_update(self):
        self._checker = UpdateChecker(APP_VERSION, GITHUB_REPO, parent=self)
        self._checker.update_available.connect(self._on_update_disponivel)
        self._checker.start()

    def _on_update_disponivel(self, new_version: str, url: str):
        self._update_version = new_version
        self._update_url     = url
        self._btn_update.setText(f"  Atualizar para v{new_version}")
        self._btn_update.setVisible(True)

    def _iniciar_download_update(self):
        if not self._update_version:
            return
        if not show_question(
            self, "Atualizar Aplicativo",
            f"Nova versão v{self._update_version} disponível.\n\n"
            f"Deseja baixar e instalar agora?",
            "Baixar", "Depois"
        ):
            return

        if not getattr(self, '_update_url', ''):
            show_info(self, "Atualização",
                      f"Acesse o GitHub para baixar a v{self._update_version} manualmente.")
            return

        self._progress_dlg = QProgressDialog(
            f"Baixando v{self._update_version}...", "Cancelar", 0, 100, self
        )
        self._progress_dlg.setWindowTitle("Atualizando Legacy BJJ")
        self._progress_dlg.setModal(True)
        self._progress_dlg.setMinimumWidth(360)
        self._progress_dlg.show()

        self._downloader = Downloader(self._update_url, parent=self)
        self._downloader.progress.connect(self._progress_dlg.setValue)
        self._downloader.finished.connect(self._on_download_concluido)
        self._downloader.failed.connect(self._on_download_falhou)
        self._progress_dlg.canceled.connect(self._downloader.terminate)
        self._downloader.start()

    def _on_download_concluido(self, path: str):
        self._progress_dlg.close()
        if show_question(
            self, "Download Concluído",
            "O instalador foi baixado.\nO aplicativo será fechado para instalar a atualização.",
            "Instalar agora", "Cancelar"
        ):
            open_installer(path)
            QApplication.quit()

    def _on_download_falhou(self, error: str):
        self._progress_dlg.close()
        show_error(self, "Erro no Download",
                   f"Não foi possível baixar a atualização.\n\n{error}")

    def confirmar_sair(self):
        if show_question(self, "Confirmar Saída", "Deseja realmente sair do sistema?", "Sim", "Cancelar"):
            self.close()
            login = LoginWindow(on_success=abrir_sistema)
            login.show()

    def show_window(self):
        self.show()


# ───────── APP ─────────

def abrir_sistema(user):
    global win
    win = MainWindow(user)
    win.show_window()


if __name__ == "__main__":
    init_db()
    init_kids_db()

    app = QApplication(sys.argv)

    login = LoginWindow(on_success=abrir_sistema)
    login.show()

    sys.exit(app.exec())
