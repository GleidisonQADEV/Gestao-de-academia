#!/bin/bash
# Build local para Mac — gera LegacyBJJ-{version}-mac.dmg
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VERSION=$(python3 -c "import sys; sys.path.insert(0,'src'); from version import APP_VERSION; print(APP_VERSION)")
echo "Build LegacyBJJ v$VERSION (Mac)"

# Ativar venv
source venv/bin/activate

# Converter ícones
python3 scripts/convert_icons.py

# Build com PyInstaller
pyinstaller LegacyBJJ.spec --noconfirm --clean

# Criar .dmg
DMG_NAME="LegacyBJJ-${VERSION}-mac.dmg"

if command -v create-dmg &> /dev/null; then
    create-dmg \
        --volname "Legacy BJJ ${VERSION}" \
        --volicon "src/assets/icon.icns" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "LegacyBJJ.app" 175 190 \
        --hide-extension "LegacyBJJ.app" \
        --app-drop-link 425 190 \
        "dist/${DMG_NAME}" \
        "dist/LegacyBJJ.app"
else
    # Fallback: DMG simples sem create-dmg
    hdiutil create -volname "Legacy BJJ ${VERSION}" \
        -srcfolder "dist/LegacyBJJ.app" \
        -ov -format UDZO \
        "dist/${DMG_NAME}"
fi

echo "Gerado: dist/${DMG_NAME}"
