#!/bin/bash
# Install patched AutoTouch from GitHub repo
# Usage: curl -fsSL https://raw.githubusercontent.com/smartmaster35rus-dev/autotouch-patch/main/scripts/install.sh | bash

set -euo pipefail

REPO="smartmaster35rus-dev/autotouch-patch"
BRANCH="main"
VERSION="8.5.5-v3"
PKG="me.autotouch.autotouch.ios8"
DEB="${PKG}_${VERSION}_iphoneos-arm64_patched.deb"

# Prefer GitHub Release; fallback to releases/ on main branch
RELEASE_URL="https://github.com/${REPO}/releases/download/v${VERSION}/${DEB}"
RAW_URL="https://github.com/${REPO}/raw/${BRANCH}/releases/${DEB}"

WORKDIR="${TMPDIR:-/tmp}/autotouch-patch-$$"
mkdir -p "$WORKDIR"
cd "$WORKDIR"

echo "[*] Downloading ${DEB}..."
if curl -fL --progress-bar -o "$DEB" "$RELEASE_URL" 2>/dev/null; then
  echo "[+] Downloaded from GitHub Release"
elif curl -fL --progress-bar -o "$DEB" "$RAW_URL"; then
  echo "[+] Downloaded from repository releases/"
else
  echo "[!] Failed to download package"
  exit 1
fi

echo "[*] Removing previous package (if installed)..."
dpkg -r "$PKG" >/dev/null 2>&1 || true

echo "[*] Installing ${DEB}..."
dpkg -i "$DEB"

echo "[*] Respringing SpringBoard..."
killall -9 SpringBoard 2>/dev/null || sbreload 2>/dev/null || uicache -a 2>/dev/null || true

echo "[+] Done. AutoTouch ${VERSION} (patched) installed."
rm -f "$DEB"
