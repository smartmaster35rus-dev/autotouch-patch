#!/bin/bash
# Install patched AutoTouch 8.0.11 inputtext hybrid from GitHub Release
# Usage: curl -fsSL https://raw.githubusercontent.com/smartmaster35rus-dev/autotouch-patch/main/scripts/install_8011_hybrid.sh | bash

set -euo pipefail

export PATH="/var/jb/usr/bin:/var/jb/bin:/usr/bin:/bin:${PATH:-}"

REPO="smartmaster35rus-dev/autotouch-patch"
TAG="8.0.11-v4.2-hybrid"
PKG="me.autotouch.autotouch.ios8.inputtext"
DEB="${PKG}_${TAG}_iphoneos-arm64_patched.deb"
RELEASE_URL="https://github.com/${REPO}/releases/download/${TAG}/${DEB}"

WORKDIR="${TMPDIR:-/tmp}/autotouch-8011-$$"
mkdir -p "$WORKDIR"
cd "$WORKDIR"

echo "[*] Downloading ${DEB}..."
if ! curl -fL --progress-bar -o "$DEB" "$RELEASE_URL"; then
  echo "[!] Failed to download from GitHub Release ${TAG}"
  exit 1
fi

echo "[*] Removing previous inputtext package (if any)..."
dpkg -r --force-depends "$PKG" >/dev/null 2>&1 || true
dpkg -r --force-depends me.autotouch.autotouch.ios8 >/dev/null 2>&1 || true

echo "[*] Installing ${DEB}..."
if ! dpkg -i "$DEB"; then
  echo "[!] dpkg failed — check PATH and jailbreak root (/var/jb)"
  exit 1
fi

echo "[*] Verifying TweakInject..."
for f in /var/jb/usr/lib/TweakInject/ATTweak.dylib /var/jb/usr/lib/TweakInject/crackATT.dylib; do
  if [ -f "$f" ]; then
    echo "[+] OK: $f"
  else
    echo "[!] Missing: $f"
  fi
done

echo "[*] ldrestart (backboardd + SpringBoard)..."
if command -v ldrestart >/dev/null 2>&1; then
  ldrestart
elif command -v sbreload >/dev/null 2>&1; then
  sbreload
else
  killall -9 backboardd SpringBoard 2>/dev/null || true
fi

echo "[+] Done. AutoTouch ${TAG} installed."
dpkg -l | grep -i autotouch || true
rm -f "$DEB"
