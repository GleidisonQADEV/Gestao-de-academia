#!/usr/bin/env python3
"""
Converte src/assets/logo.png → icon.ico (Windows) e icon.icns (Mac).
Requisito: pip install pillow
Uso: python3 scripts/convert_icons.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Instalando Pillow...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image

ROOT   = Path(__file__).resolve().parent.parent
SRC    = ROOT / "src" / "assets" / "logo.png"
ICO    = ROOT / "src" / "assets" / "icon.ico"
ICNS   = ROOT / "src" / "assets" / "icon.icns"

if not SRC.exists():
    print(f"logo.png não encontrado em {SRC}")
    sys.exit(1)

img = Image.open(SRC).convert("RGBA")

# ── Windows .ico ──────────────────────────────────────────────
SIZES = [(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
frames = [img.resize(s, Image.LANCZOS) for s in SIZES]
frames[0].save(ICO, format="ICO", sizes=SIZES, append_images=frames[1:])
print(f"Criado: {ICO}")

# ── Mac .icns (usa iconutil, disponível apenas no macOS) ──────
import platform
if platform.system() == "Darwin":
    iconset_dir = Path(tempfile.mkdtemp()) / "icon.iconset"
    iconset_dir.mkdir()
    for s in [16, 32, 64, 128, 256, 512, 1024]:
        img.resize((s, s), Image.LANCZOS).save(iconset_dir / f"icon_{s}x{s}.png")
        if s <= 512:
            img.resize((s*2, s*2), Image.LANCZOS).save(iconset_dir / f"icon_{s}x{s}@2x.png")
    result = subprocess.run(
        ["iconutil", "-c", "icns", str(iconset_dir), "-o", str(ICNS)],
        capture_output=True
    )
    import shutil
    shutil.rmtree(iconset_dir.parent)
    if result.returncode == 0:
        print(f"Criado: {ICNS}")
    else:
        print(f"Erro ao criar .icns: {result.stderr.decode()}")
else:
    print("Pulando .icns — disponível apenas no macOS.")
