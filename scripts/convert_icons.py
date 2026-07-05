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


def _quadrado(im, size, margem=0.06):
    """Ajusta a imagem num quadrado transparente, preservando a proporção.

    Evita distorção (esticar) e borrão. 'margem' deixa uma folga nas bordas.
    """
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    alvo = int(size * (1 - margem * 2))
    fitted = im.copy()
    fitted.thumbnail((alvo, alvo), Image.LANCZOS)
    x = (size - fitted.width) // 2
    y = (size - fitted.height) // 2
    canvas.paste(fitted, (x, y), fitted)
    return canvas


# ── Windows .ico ──────────────────────────────────────────────
ICO_SIZES = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
frames = [_quadrado(img, s) for s, _ in ICO_SIZES]
# Salva o maior frame com todos os tamanhos embutidos (nítido em cada resolução)
frames[-1].save(ICO, format="ICO", sizes=ICO_SIZES, append_images=frames[:-1])
print(f"Criado: {ICO}")

# ── Mac .icns (usa iconutil, disponível apenas no macOS) ──────
import platform
if platform.system() == "Darwin":
    iconset_dir = Path(tempfile.mkdtemp()) / "icon.iconset"
    iconset_dir.mkdir()
    for s in [16, 32, 64, 128, 256, 512, 1024]:
        _quadrado(img, s).save(iconset_dir / f"icon_{s}x{s}.png")
        if s <= 512:
            _quadrado(img, s * 2).save(iconset_dir / f"icon_{s}x{s}@2x.png")
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

