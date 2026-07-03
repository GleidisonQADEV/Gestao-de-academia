"""
Testes para src/version.py e src/ui/updater.py
"""
import sys
import json
import urllib.error
import platform
from unittest.mock import patch, MagicMock


# ── Stub de QThread/Signal para evitar dependência do Qt ────────────────────

class _FakeSignal:
    """Signal fake que guarda os handlers e permite emit()."""
    def __init__(self, *types):
        self._handlers = []

    def connect(self, fn):
        self._handlers.append(fn)

    def emit(self, *args):
        for fn in self._handlers:
            fn(*args)


class _FakeQThread:
    def __init__(self, parent=None): pass
    def start(self): pass


# Injeta stubs ANTES de importar updater.
# Guardamos os módulos reais do PySide6 para restaurá-los logo após o import,
# evitando que o mock vaze para outros arquivos de teste (o que quebraria os
# testes que usam o Qt real e poderia causar segmentation fault).
_fake_qtcore = MagicMock()
_fake_qtcore.QThread = _FakeQThread
_fake_qtcore.Signal = _FakeSignal
_fake_qtcore.QObject = object

_PYSIDE_KEYS = ['PySide6', 'PySide6.QtCore']
_real_pyside_modules = {k: sys.modules.get(k) for k in _PYSIDE_KEYS}

sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtCore'] = _fake_qtcore

# Agora é seguro importar
from ui.updater import UpdateChecker, _parse_version  # noqa: E402

# Restaurar imediatamente os módulos reais do PySide6 para não poluir o estado
# global compartilhado entre os testes.
for _k, _v in _real_pyside_modules.items():
    if _v is not None:
        sys.modules[_k] = _v
    else:
        sys.modules.pop(_k, None)

import pytest


# ──────────────────────────────────────────────
# version.py
# ──────────────────────────────────────────────

class TestVersion:
    def test_importavel(self):
        import version
        assert hasattr(version, 'APP_VERSION')
        assert hasattr(version, 'GITHUB_REPO')

    def test_app_version_formato(self):
        from version import APP_VERSION
        parts = APP_VERSION.split('.')
        assert len(parts) == 3, "APP_VERSION deve ter formato X.Y.Z"
        assert all(p.isdigit() for p in parts)

    def test_github_repo_formato(self):
        from version import GITHUB_REPO
        assert '/' in GITHUB_REPO
        owner, repo = GITHUB_REPO.split('/', 1)
        assert owner and repo


# ──────────────────────────────────────────────
# _parse_version
# ──────────────────────────────────────────────

class TestParseVersion:
    def test_parse_simples(self):
        assert _parse_version("1.0.0") == (1, 0, 0)

    def test_parse_com_prefixo_v(self):
        assert _parse_version("v1.2.3") == (1, 2, 3)

    def test_versao_maior(self):
        assert _parse_version("1.1.0") > _parse_version("1.0.0")

    def test_versao_igual(self):
        assert _parse_version("1.0.0") == _parse_version("v1.0.0")

    def test_versao_menor(self):
        assert _parse_version("0.9.9") < _parse_version("1.0.0")


# ──────────────────────────────────────────────
# UpdateChecker
# ──────────────────────────────────────────────

class TestUpdateChecker:

    def _make_checker(self, current="1.0.0"):
        c = UpdateChecker(current, "owner/repo")
        # Substituir signals por FakeSignal para capturar emissões
        c.update_available = _FakeSignal(str, str)
        c.check_failed     = _FakeSignal()
        return c

    def _mock_response(self, payload: dict):
        data = json.dumps(payload).encode()
        resp = MagicMock()
        resp.read.return_value = data
        resp.__enter__ = lambda s: s
        resp.__exit__  = MagicMock(return_value=False)
        return resp

    def test_sem_atualizacao(self):
        checker = self._make_checker("1.0.0")
        emitted = []
        checker.update_available.connect(lambda v, u: emitted.append(v))

        with patch('urllib.request.urlopen', return_value=self._mock_response({"tag_name": "v1.0.0", "assets": []})):
            checker.run()

        assert emitted == []

    def test_com_atualizacao_disponivel(self):
        checker = self._make_checker("1.0.0")
        emitted = []
        checker.update_available.connect(lambda v, u: emitted.append((v, u)))

        payload = {
            "tag_name": "v2.0.0",
            "assets": [{"name": "LegacyBJJ-2.0.0-mac.dmg",
                        "browser_download_url": "https://example.com/file.dmg"}]
        }
        with patch('urllib.request.urlopen', return_value=self._mock_response(payload)), \
             patch('platform.system', return_value='Darwin'):
            checker.run()

        assert len(emitted) == 1
        assert emitted[0][0] == "2.0.0"
        assert "file.dmg" in emitted[0][1]

    def test_falha_de_rede(self):
        checker = self._make_checker("1.0.0")
        failed = []
        checker.check_failed.connect(lambda: failed.append(True))

        with patch('urllib.request.urlopen', side_effect=urllib.error.URLError("timeout")):
            checker.run()

        assert failed == [True]

    def test_tag_vazia_nao_emite(self):
        checker = self._make_checker("1.0.0")
        emitted = []
        checker.update_available.connect(lambda v, u: emitted.append(v))

        with patch('urllib.request.urlopen', return_value=self._mock_response({"tag_name": "", "assets": []})):
            checker.run()

        assert emitted == []

    def test_find_asset_mac(self):
        checker = self._make_checker()
        assets = [
            {"name": "LegacyBJJ-2.0.0-mac.dmg",          "browser_download_url": "http://mac"},
            {"name": "LegacyBJJ-2.0.0-windows-setup.exe", "browser_download_url": "http://win"},
        ]
        with patch('platform.system', return_value='Darwin'):
            assert checker._find_asset(assets) == "http://mac"

    def test_find_asset_windows(self):
        checker = self._make_checker()
        assets = [
            {"name": "LegacyBJJ-2.0.0-mac.dmg",          "browser_download_url": "http://mac"},
            {"name": "LegacyBJJ-2.0.0-windows-setup.exe", "browser_download_url": "http://win"},
        ]
        with patch('platform.system', return_value='Windows'):
            assert checker._find_asset(assets) == "http://win"

    def test_find_asset_sem_match(self):
        checker = self._make_checker()
        with patch('platform.system', return_value='Darwin'):
            assert checker._find_asset([]) == ""
