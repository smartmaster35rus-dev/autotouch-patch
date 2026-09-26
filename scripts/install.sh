#!/bin/bash
# Install patched AutoTouch from GitHub repo
# Usage: curl -fsSL https://raw.githubusercontent.com/smartmaster35rus-dev/autotouch-patch/main/scripts/install.sh | bash

set -euo pipefail

REPO="smartmaster35rus-dev/autotouch-patch"
BRANCH="main"
VERSION="8.5.5-v3.6"
PKG="me.autotouch.autotouch.ios8"
DEB="${PKG}_${VERSION}_iphoneos-arm64_patched.deb"

# Prefer GitHub Release; fallback to releases/ on main branch
RELEASE_URL="https://github.com/${REPO}/releases/download/v${VERSION}/${DEB}"
RAW_URL="https://github.com/${REPO}/raw/${BRANCH}/releases/${DEB}"

WORKDIR="${TMPDIR:-/tmp}/autotouch-patch-$$"
mkdir -p "$WORKDIR"
cd "$WORKDIR"

ensure_ellekit() {
  if dpkg -s ellekit >/dev/null 2>&1; then
    echo "[+] ElleKit package already installed"
    return 0
  fi
  echo "[*] Optional: dpkg package ellekit (injector may already be in the jailbreak)..."
  if command -v apt-get >/dev/null 2>&1; then
    apt-get update -qq || true
    apt-get install -y ellekit || true
  elif command -v apt >/dev/null 2>&1; then
    apt update -qq || true
    apt install -y ellekit || true
  fi
  if ! dpkg -s ellekit >/dev/null 2>&1; then
    echo "[i] Package ellekit is not installed. Continuing — this .deb does not hard-depend on it."
  fi
}

echo "[*] Downloading ${DEB}..."
if curl -fL --progress-bar -o "$DEB" "$RELEASE_URL" 2>/dev/null; then
  echo "[+] Downloaded from GitHub Release"
elif curl -fL --progress-bar -o "$DEB" "$RAW_URL"; then
  echo "[+] Downloaded from repository releases/"
else
  echo "[!] Failed to download package (tag v${VERSION} or releases/${DEB})"
  exit 1
fi

ensure_ellekit

echo "[*] Removing previous package (if installed, including half-configured)..."
dpkg -r --force-depends "$PKG" >/dev/null 2>&1 || true

echo "[*] Installing ${DEB}..."
if ! dpkg -i "$DEB"; then
  echo "[!] dpkg failed"
  exit 1
fi

echo "[*] Verifying crackATT patch files..."
DEST="/var/jb/Library/MobileSubstrate/DynamicLibraries"
if [ -f "$DEST/crackATT.plist" ]; then
  if grep -q "me.autotouch.AutoTouch.ios8" "$DEST/crackATT.plist" 2>/dev/null; then
    echo "[+] crackATT.plist includes AutoTouch bundle filter"
  else
    echo "[!] crackATT.plist is present but missing me.autotouch.AutoTouch.ios8 — use install-patch-only.sh"
  fi
else
  echo "[!] crackATT.plist not found under $DEST — package may be incomplete"
fi

echo "[*] Restarting tweak injection (backboardd + SpringBoard)..."
if command -v ldrestart >/dev/null 2>&1; then
  ldrestart
elif command -v sbreload >/dev/null 2>&1; then
  sbreload
else
  killall -9 backboardd SpringBoard 2>/dev/null || true
fi

echo "[+] Done. AutoTouch ${VERSION} (patched) installed."
echo "[i] ATTweak.plist has only backboardd + SpringBoard (official). Injection into AutoTouch uses crackATT.plist."
rm -f "$DEB"
