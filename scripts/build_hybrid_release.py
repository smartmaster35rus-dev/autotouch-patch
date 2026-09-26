#!/usr/bin/env python3
"""Build v3.5 hybrid .deb: binary-patched ATTweak.dylib + crackATT persistence layer."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH_DIR = ROOT / "patch"
EXTRACTED = ROOT / "arm64" / "extracted"
DYLIB_REL = Path("var/jb/Library/MobileSubstrate/DynamicLibraries")
ATTWEAK_REL = DYLIB_REL / "ATTweak.dylib"

POSTINST_APPEND = """
# autotouch-patch: re-sign tweaked dylibs so injection survives respring/reboot
if [ -d /var/jb ]; then
  JB="/var/jb"
else
  JB=""
fi
if command -v ldid >/dev/null 2>&1; then
  for f in ATTweak.dylib crackATT.dylib; do
    if [ -f "${JB}/Library/MobileSubstrate/DynamicLibraries/$f" ]; then
      ldid -S "${JB}/Library/MobileSubstrate/DynamicLibraries/$f" 2>/dev/null || true
    fi
  done
fi
if command -v ldrestart >/dev/null 2>&1; then
  ldrestart
fi
"""


def default_orig_deb() -> Path:
    env = os.environ.get("AUTOTOUCH_ORIG_DEB")
    if env:
        return Path(env)
    candidates = [
        Path(r"C:\Users\SmartMaster35Rus\Downloads\Telegram Desktop")
        / "me.autotouch.autotouch.ios8_8.5.5_iphoneos-arm64.deb",
        ROOT / "releases" / "me.autotouch.autotouch.ios8_8.5.5_iphoneos-arm64_patched.deb",
    ]
    for path in candidates:
        if path.is_file():
            return path
    raise SystemExit(
        "Set AUTOTOUCH_ORIG_DEB to the official AutoTouch 8.5.5 arm64 .deb"
    )


def run_py(script: str, *args: str) -> None:
    cmd = [sys.executable, str(ROOT / "scripts" / script), *args]
    subprocess.check_call(cmd)


def append_postinst(extracted: Path) -> None:
    postinst = extracted / "control" / "postinst"
    text = postinst.read_text(encoding="utf-8", errors="replace") if postinst.is_file() else "#!/bin/sh\n"
    if "autotouch-patch: re-sign" in text:
        return
    if not text.endswith("\n"):
        text += "\n"
    text += POSTINST_APPEND
    postinst.write_text(text, encoding="utf-8", newline="\n")
    postinst.chmod(0o755)


def main() -> None:
    version = os.environ.get("RELEASE_VERSION", "8.5.5-v3.5")
    orig = default_orig_deb()
    tmp_patched = ROOT / "patch" / "ATTweak_patched.dylib"

    if not (PATCH_DIR / "crackATT.dylib").is_file():
        raise SystemExit("Missing patch/crackATT.dylib — build tweak in CI or copy artifact")

    print("[*] Extracting %s" % orig)
    if EXTRACTED.exists():
        shutil.rmtree(EXTRACTED)
    sys.path.insert(0, str(ROOT / "scripts"))
    from extract_deb import extract_deb

    extract_deb(orig, EXTRACTED)

    attweak_in = EXTRACTED / "data" / ATTWEAK_REL
    if not attweak_in.is_file():
        raise SystemExit("ATTweak.dylib not found in package: %s" % attweak_in)

    print("[*] Binary-patching ATTweak.dylib (setupTimer -> RET)")
    run_py("patch_attweak.py", str(attweak_in), str(tmp_patched))
    shutil.copy2(tmp_patched, attweak_in)

    dest_dl = EXTRACTED / "data" / DYLIB_REL
    dest_dl.mkdir(parents=True, exist_ok=True)
    for name in ("crackATT.dylib", "crackATT.plist"):
        shutil.copy2(PATCH_DIR / name, dest_dl / name)
    print("[*] Injected crackATT into %s" % dest_dl)

    append_postinst(EXTRACTED)

    out_name = "me.autotouch.autotouch.ios8_%s_iphoneos-arm64_patched.deb" % version
    out = ROOT / "releases" / out_name
    run_py("build_deb.py", str(EXTRACTED), str(out))

    alias = ROOT / "releases" / "me.autotouch.autotouch.ios8_8.5.5_iphoneos-arm64_patched.deb"
    shutil.copy2(out, alias)
    print("[+] %s" % out)
    print("[+] %s" % alias)


if __name__ == "__main__":
    main()
