#!/bin/bash
# Inject crackATT patch into an already installed AutoTouch (rootless /var/jb)
# Usage: curl -fsSL https://raw.githubusercontent.com/smartmaster35rus-dev/autotouch-patch/main/scripts/install-patch-only.sh | bash

set -euo pipefail

REPO="smartmaster35rus-dev/autotouch-patch"
BRANCH="main"
BASE="https://github.com/${REPO}/raw/${BRANCH}/patch"
DEST="/var/jb/Library/MobileSubstrate/DynamicLibraries"

if [ ! -d "/var/jb" ]; then
  echo "[!] /var/jb not found. This script is for rootless jailbreaks."
  exit 1
fi

mkdir -p "$DEST"

echo "[*] Downloading patch files..."
curl -fL --progress-bar -o "$DEST/crackATT.dylib" "$BASE/crackATT.dylib"
curl -fL --progress-bar -o "$DEST/crackATT.plist" "$BASE/crackATT.plist"
chmod 755 "$DEST/crackATT.dylib"
chmod 644 "$DEST/crackATT.plist"

echo "[*] Restarting tweak injection (backboardd + SpringBoard)..."
if command -v ldrestart >/dev/null 2>&1; then
  ldrestart
elif command -v sbreload >/dev/null 2>&1; then
  sbreload
else
  killall -9 backboardd SpringBoard 2>/dev/null || true
fi

echo "[+] Patch installed to $DEST"
