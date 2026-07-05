import sys
import os
import platform
import urllib.request
import urllib.error
import json
import tempfile
import subprocess

from PySide6.QtCore import QThread, Signal


def _parse_version(v: str) -> tuple:
    return tuple(int(x) for x in v.lstrip("v").split("."))


class UpdateChecker(QThread):
    """Background thread: checks GitHub Releases for a newer version."""
    update_available = Signal(str, str)  # (new_version, download_url)
    check_failed     = Signal()

    def __init__(self, current_version: str, repo: str, parent=None):
        super().__init__(parent)
        self._version = current_version
        self._repo    = repo
        self.release_notes = ""   # preenchido com o corpo da release ao detectar update

    def run(self):
        try:
            url = f"https://api.github.com/repos/{self._repo}/releases/latest"
            req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                                        "User-Agent": "LegacyBJJ-updater"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())

            tag = data.get("tag_name", "")
            if not tag:
                return

            if _parse_version(tag) > _parse_version(self._version):
                self.release_notes = data.get("body", "") or ""
                asset_url = self._find_asset(data.get("assets", []))
                self.update_available.emit(tag.lstrip("v"), asset_url or "")
        except Exception:
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

            def _report(count, block, total):
                if total > 0:
                    self.progress.emit(int(count * block * 100 / total))

            urllib.request.urlretrieve(self._url, tmp.name, _report)
            self.progress.emit(100)
            self.finished.emit(tmp.name)
        except Exception as e:
            self.failed.emit(str(e))


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
