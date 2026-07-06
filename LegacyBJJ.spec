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

# ── Metadados de versão do .exe (Windows) — reduz falsos-positivos de antivírus ──
_version_file = None
if sys.platform == 'win32':
    _v = "1.0.0"
    try:
        import re as _re
        _txt = (ROOT / 'src' / 'version.py').read_text(encoding='utf-8')
        _m = _re.search(r'APP_VERSION\s*=\s*["\']([\d.]+)["\']', _txt)
        if _m:
            _v = _m.group(1)
    except Exception:
        pass
    _parts = (_v.split('.') + ['0', '0', '0', '0'])[:4]
    _fv = ", ".join(str(int(p)) for p in _parts)
    _version_file = str(ROOT / '_version_info.txt')
    with open(_version_file, 'w', encoding='utf-8') as _f:
        _f.write(f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({_fv}), prodvers=({_fv}),
    mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040904B0', [
      StringStruct('CompanyName', 'Legacy BJJ'),
      StringStruct('FileDescription', 'Sistema de Gestao Legacy BJJ'),
      StringStruct('FileVersion', '{_v}'),
      StringStruct('InternalName', 'LegacyBJJ'),
      StringStruct('LegalCopyright', 'Legacy BJJ'),
      StringStruct('OriginalFilename', 'LegacyBJJ.exe'),
      StringStruct('ProductName', 'Legacy BJJ'),
      StringStruct('ProductVersion', '{_v}')])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
""")

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LegacyBJJ',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon,
    version=_version_file,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='LegacyBJJ',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='LegacyBJJ.app',
        icon=str(ROOT / 'src' / 'assets' / 'icon.icns'),
        bundle_identifier='com.legacybjj.app',
        info_plist={
            'CFBundleShortVersionString': '1.2.7',
            'CFBundleVersion':            '1.2.7',
            'NSHighResolutionCapable':    True,
        },
    )
