"""Diálogo de atualização: mostra as novidades da versão e permite baixar/instalar."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser, QPushButton
)
from PySide6.QtCore import Qt


_FALLBACK = (
    "Uma nova versão do Legacy BJJ está disponível.\n\n"
    "Clique em **Baixar e instalar** para atualizar agora. O instalador será "
    "baixado e aberto automaticamente; basta seguir o assistente. Seus dados "
    "cadastrados são preservados."
)

_COMO_PROCEDER = (
    "\n\n---\n\n"
    "### Como atualizar\n"
    "1. Clique em **Baixar e instalar**.\n"
    "2. Aguarde o download concluir.\n"
    "3. O instalador abre sozinho — siga o assistente até o fim.\n"
    "4. Reabra o Legacy BJJ. Pronto! Seus dados continuam salvos.\n"
)


class UpdateDialog(QDialog):
    def __init__(self, version: str, notes: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Atualização disponível — v{version}")
        self.resize(620, 580)
        self.setStyleSheet("QDialog { background: #111111; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        titulo = QLabel(f"🚀 Nova versão v{version} disponível")
        titulo.setStyleSheet(
            "color:#ffffff; font-size:18px; font-weight:700; background:transparent;"
        )
        layout.addWidget(titulo)

        sub = QLabel("Veja o que mudou nesta atualização:")
        sub.setStyleSheet("color:#888888; font-size:12px; background:transparent;")
        layout.addWidget(sub)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        conteudo = (notes or _FALLBACK) + _COMO_PROCEDER
        try:
            browser.setMarkdown(conteudo)
        except Exception:
            browser.setPlainText(conteudo)
        browser.setStyleSheet(
            "QTextBrowser { background:#161616; color:#cfcfcf; border:1px solid #222222;"
            " border-radius:8px; padding:12px; font-size:13px; }"
        )
        layout.addWidget(browser, 1)

        btns = QHBoxLayout()
        btns.addStretch()

        btn_depois = QPushButton("Depois")
        btn_depois.setCursor(Qt.PointingHandCursor)
        btn_depois.setFixedHeight(38)
        btn_depois.setStyleSheet(
            "QPushButton { background:#1e1e1e; color:#cccccc; border:1px solid #2a2a2a;"
            " border-radius:7px; font-size:13px; font-weight:600; padding:0 20px; }"
            " QPushButton:hover { background:#252525; color:#ffffff; }"
        )
        btn_depois.clicked.connect(self.reject)
        btns.addWidget(btn_depois)

        btn_baixar = QPushButton("Baixar e instalar")
        btn_baixar.setCursor(Qt.PointingHandCursor)
        btn_baixar.setFixedHeight(38)
        btn_baixar.setStyleSheet(
            "QPushButton { background:#cc1e1e; color:#ffffff; border:none;"
            " border-radius:7px; font-size:13px; font-weight:700; padding:0 22px; }"
            " QPushButton:hover { background:#e02020; }"
        )
        btn_baixar.clicked.connect(self.accept)
        btns.addWidget(btn_baixar)

        layout.addLayout(btns)
