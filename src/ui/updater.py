import sys
import os
import platform
import ssl
import urllib.request
import urllib.error
import json
import tempfile
import subprocess

from PySide6.QtCore import QThread, Signal


def _ssl_context():
    """Cria um contexto SSL usando o pacote certifi quando disponível.

    Em builds empacotados (PyInstaller) o urllib pode não encontrar os
    certificados do sistema, causando falha de verificação SSL ao acessar o
    GitHub. O certifi garante um conjunto de certificados confiável.
    """
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def _parse_version(v: str) -> tuple:
    return tuple(int(x) for x in v.lstrip("v").split("."))


def mensagem_checagem_manual(update_found: bool, check_failed: bool, app_version: str,
                             detalhe: str = "") -> tuple:
    """Decide a mensagem da verificação manual de atualizações.

    Retorna (nivel, titulo, texto) onde nivel é 'info', 'error' ou None.
    - update_found: uma nova versão foi encontrada (nenhuma mensagem é necessária).
    - check_failed: a verificação falhou (rede/firewall).
    - caso contrário: já está na versão mais recente.
    - detalhe: mensagem técnica do erro (exibida para diagnóstico).
    """
    if update_found:
        return (None, "", "")
    if check_failed:
        texto = (
            "Não foi possível verificar atualizações.\n\n"
            "Verifique a conexão com a internet e se o antivírus/firewall "
            "não está bloqueando o acesso a github.com."
        )
        if detalhe:
            texto += f"\n\nDetalhes técnicos:\n{detalhe}"
        return ("error", "Atualizações", texto)
    return (
        "info", "Atualizações",
        f"Você já está na versão mais recente (v{app_version})."
    )


class UpdateChecker(QThread):
    """Background thread: checks GitHub Releases for a newer version."""
    update_available = Signal(str, str)  # (new_version, download_url)
    check_failed     = Signal()

    def __init__(self, current_version: str, repo: str, parent=None):
        super().__init__(parent)
        self._version = current_version
        self._repo    = repo
        self.release_notes = ""   # preenchido com o corpo da release ao detectar update
        self.error_detail  = ""   # mensagem técnica do último erro (para diagnóstico)

    def run(self):
        try:
            url = f"https://api.github.com/repos/{self._repo}/releases/latest"
            req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                                        "User-Agent": "LegacyBJJ-updater"})
            with urllib.request.urlopen(req, timeout=8, context=_ssl_context()) as resp:
                data = json.loads(resp.read().decode())

            tag = data.get("tag_name", "")
            if not tag:
                return

            if _parse_version(tag) > _parse_version(self._version):
                self.release_notes = data.get("body", "") or ""
                asset_url = self._find_asset(data.get("assets", []))
                self.update_available.emit(tag.lstrip("v"), asset_url or "")
        except Exception as e:
            self.error_detail = f"{type(e).__name__}: {e}"
            self.check_failed.emit()

    def _find_asset(self, assets: list) -> str:
        system = platform.system()
        for a in assets:
            name: str = a.get("name", "").lower()
            if system == "Darwin"  and name.endswith(".dmg"):
                return a["browser_download_url"]
            if system == "Windows" and name.endswith(".exe"):
                return a["browser_download_url"]
        return ""


class Downloader(QThread):
    """Background thread: downloads a file and reports progress."""
    progress   = Signal(int)          # 0-100
    finished   = Signal(str)          # local file path
    failed     = Signal(str)          # error message

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self._url = url

    def run(self):
        try:
            suffix = ".dmg" if self._url.endswith(".dmg") else ".exe"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.close()

            req = urllib.request.Request(
                self._url, headers={"User-Agent": "LegacyBJJ-updater"}
            )
            with urllib.request.urlopen(req, timeout=60, context=_ssl_context()) as resp, \
                    open(tmp.name, "wb") as out:
                total = int(resp.headers.get("Content-Length", 0) or 0)
                baixado = 0
                while True:
                    bloco = resp.read(65536)
                    if not bloco:
                        break
                    out.write(bloco)
                    baixado += len(bloco)
                    if total > 0:
                        self.progress.emit(int(baixado * 100 / total))

            self.progress.emit(100)
            self.finished.emit(tmp.name)
        except Exception as e:
            self.failed.emit(f"{type(e).__name__}: {e}")


def open_installer(path: str):
    """Abre o instalador baixado durante a atualização.

    No Windows, roda o instalador do Inno Setup em modo silencioso para não
    repetir o assistente (pasta, ícone na área de trabalho, etc.) a cada
    atualização — apenas atualiza os arquivos e recria os atalhos.
    """
    system = platform.system()
    if system == "Darwin":
        subprocess.Popen(["open", path])
    elif system == "Windows":
        try:
            subprocess.Popen([
                path,
                "/SILENT",             # sem páginas do assistente (mostra só o progresso)
                "/SUPPRESSMSGBOXES",   # não exibe caixas de confirmação
                "/NORESTART",          # não reinicia o Windows
                "/NOCANCEL",
            ])
        except Exception:
            os.startfile(path)
    else:
        subprocess.Popen(["xdg-open", path])
