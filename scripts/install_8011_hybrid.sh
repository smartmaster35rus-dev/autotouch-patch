#!/bin/sh
# AutoTouch 8.0.11 inputtext — hybrid (patched ATTweak + crackATT)
set -e
export PATH=/var/jb/usr/bin:/var/jb/bin:/usr/bin:/bin:$PATH

DEB="${1:-me.autotouch.autotouch.ios8.inputtext_8.0.11-v1-hybrid_iphoneos-arm64_patched.deb}"

echo "[*] Installing $DEB"
dpkg -i "$DEB" || true
dpkg --configure -a 2>/dev/null || true

if command -v ldrestart >/dev/null 2>&1; then
  echo "[*] ldrestart (SSH may disconnect)"
  ldrestart
else
  echo "[!] ldrestart not found — respring manually (ElleKit)"
fi

echo "[+] Done. Open AutoTouch → Settings: expect Licensed; test auto-launch script."
