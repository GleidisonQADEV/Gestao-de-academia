# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

ROOT = Path(SPECPATH)

a = Analysis(
    [str(ROOT / 'src' / 'main.py')],
    pathex=[str(ROOT / 'src')],
    binaries=[],
    datas=[
        (str(ROOT / 'src' / 'assets'),   'assets'),
        (str(ROOT / 'src' / 'database'), 'database'),
        (str(ROOT / 'version.json'),     '.'),
    ],
    hiddenimports=[
        'PySide6.QtSvg',
        'PySide6.QtXml',
        'reportlab',
        'reportlab.graphics.barcode',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

if sys.platform == 'darwin':
    _icon = str(ROOT / 'src' / 'assets' / 'icon.icns')
elif sys.platform == 'win32':
    _icon = str(ROOT / 'src' / 'assets' / 'icon.ico')
else:
    _icon = None

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='LegacyBJJ',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon,
)

if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='LegacyBJJ.app',
        icon=str(ROOT / 'src' / 'assets' / 'icon.icns'),
        bundle_identifier='com.legacybjj.app',
        info_plist={
            'CFBundleShortVersionString': '1.2.0',
            'CFBundleVersion':            '1.2.0',
            'NSHighResolutionCapable':    True,
        },
    )
