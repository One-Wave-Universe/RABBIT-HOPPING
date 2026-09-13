#!/usr/bin/env bash
# Build a portable Linux AppImage for the RABBIT-HOPPING Physics Sandbox GUI.
# Run this on a Linux machine with Python 3 + pip.
set -euo pipefail

APP_NAME="RabbitHoppingSandbox"
APP_DIR="${APP_NAME}.AppDir"
BUILD_DIR="build_appimage"

cd "$(dirname "$0")/.."
ROOT="$(pwd)"

echo "[1/6] Cleaning previous build..."
rm -rf "${APP_DIR}" "${BUILD_DIR}" "${APP_NAME}.AppImage"
mkdir -p "${APP_DIR}/usr/bin" "${APP_DIR}/usr/lib" "${APP_DIR}/usr/share/applications" "${APP_DIR}/usr/share/icons/hicolor/256x256/apps"

echo "[2/6] Installing PyInstaller (if needed)..."
pip install --user pyinstaller numpy scipy 2>/dev/null || pip install pyinstaller numpy scipy

echo "[3/6] Bundling physics_app.py into one-file binary..."
pyinstaller --noconfirm --onefile --windowed \
  --name "${APP_NAME}" \
  --distpath "${BUILD_DIR}/dist" \
  --workpath "${BUILD_DIR}/work" \
  --specpath "${BUILD_DIR}/spec" \
  "sandbox/physics_app.py"

BIN_SRC="${BUILD_DIR}/dist/${APP_NAME}"
if [ ! -f "${BIN_SRC}" ]; then
  echo "Build failed: binary not found."
  exit 1
fi

echo "[4/6] Assembling AppDir..."
cp "${BIN_SRC}" "${APP_DIR}/usr/bin/${APP_NAME}"
chmod +x "${APP_DIR}/usr/bin/${APP_NAME}"

# Desktop entry
cat > "${APP_DIR}/usr/share/applications/${APP_NAME}.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Rabbit Hopping Physics Sandbox
Comment=Interactive physics sandbox: memristor, quadratic Hopfield, reinjection, cell stack
Exec=${APP_NAME}
Icon=${APP_NAME}
Categories=Science;Education;
Terminal=false
EOF
cp "${APP_DIR}/usr/share/applications/${APP_NAME}.desktop" "${APP_DIR}/${APP_NAME}.desktop"

# Simple icon (text-based placeholder; replace with real PNG if you have one)
cat > "${APP_DIR}/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.svg" <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
  <rect width="256" height="256" fill="#0a0a0f"/>
  <text x="128" y="150" font-family="monospace" font-size="90" fill="#00ff9f" text-anchor="middle" font-weight="bold">RH</text>
</svg>
SVG
cp "${APP_DIR}/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.svg" "${APP_DIR}/${APP_NAME}.svg"

echo "[5/6] Downloading appimagetool (if needed)..."
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
  curl -L -o appimagetool-x86_64.AppImage https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
  chmod +x appimagetool-x86_64.AppImage
fi

echo "[6/6] Creating AppImage..."
ARCH=x86_64 ./appimagetool-x86_64.AppImage "${APP_DIR}" "${APP_NAME}.AppImage"

echo ""
echo "DONE. Download: ${ROOT}/${APP_NAME}.AppImage"
echo "Make executable: chmod +x ${APP_NAME}.AppImage"
echo "Run: ./${APP_NAME}.AppImage"
echo ""
echo "If it complains about missing libs, install: sudo apt install libgl1 libglib2.0-0 libxkbcommon0"
