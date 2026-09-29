#!/usr/bin/env python3
"""Build 8.0.11 hybrid .deb: patched ATTweak.dylib + crackATT (license + auto-launch)."""

from __future__ import annotations

import os
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path

REQUIRED_CRACK_BUNDLES = (
    "com.apple.backboardd",
    "com.apple.springboard",
    "me.autotouch.AutoTouch.ios8",
)

ROOT = Path(__file__).resolve().parents[1]
INPUTTEXT = ROOT / "v8.0.11_inputtext"
EXTRACTED = INPUTTEXT / "hybrid_build"
DYLIB_REL = Path("var/jb/Library/MobileSubstrate/DynamicLibraries")
PATCH8011 = INPUTTEXT / "patch"

POSTINST_APPEND = """
# autotouch-patch 8.0.11: reload injectors after install
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
if command -v uicache >/dev/null 2>&1; then
  uicache -p "${JB}/Applications/AutoTouch.app" 2>/dev/null || uicache -a 2>/dev/null || true
fi
if command -v ldrestart >/dev/null 2>&1; then
  ldrestart
fi
"""


def default_orig_deb() -> Path:
    env = os.environ.get("AUTOTOUCH_8011_DEB")
    if env:
        return Path(env)
    for path in (
        ROOT / "vendor" / "me.autotouch.autotouch.ios8.inputtext_8.0.11_iphoneos-arm64.deb",
        INPUTTEXT / "me.autotouch.autotouch.ios8.inputtext_8.0.11_iphoneos-arm64.deb",
        INPUTTEXT / "me.autotouch.autotouch.ios8.inputtext_8.0.11_iphoneos-arm64_patched.deb",
    ):
        if path.is_file():
            return path
    raise SystemExit(
        "Set AUTOTOUCH_8011_DEB or place the official 8.0.11 inputtext .deb under v8.0.11_inputtext/"
    )


def crack_dylib_path() -> Path:
    env = os.environ.get("CRACKATT_8011_DYLIB")
    if env:
        return Path(env)
    for path in (
        PATCH8011 / "crackATT.dylib",
        ROOT / "dist" / "crackATT-8011.dylib",
        ROOT / "dist" / "crackATT.dylib",
    ):
        if path.is_file():
            return path
    raise SystemExit(
        "Missing crackATT for 8.0.11 — build tweak8011 (CI artifact) and copy to "
        "v8.0.11_inputtext/patch/crackATT.dylib or set CRACKATT_8011_DYLIB"
    )


def ensure_crackatt_plist(path: Path) -> None:
    src = ROOT / "tweak8011" / "crackATT.plist"
    shutil.copy2(src, path)
    data = plistlib.load(path.open("rb"))
    bundles = list(data.get("Filter", {}).get("Bundles", []))
    missing = [b for b in REQUIRED_CRACK_BUNDLES if b not in bundles]
    if missing:
        raise SystemExit("crackATT.plist missing bundles: %s" % ", ".join(missing))


def relax_ellekit_depends(extracted: Path) -> None:
    control = extracted / "control" / "control"
    text = control.read_text(encoding="utf-8")
    old = "Depends: firmware (>= 11.0), ellekit\n"
    new = "Depends: firmware (>= 11.0)\n"
    if old not in text:
        if "ellekit" in text and "Depends:" in text:
            lines = []
            for line in text.splitlines(keepends=True):
                if line.startswith("Depends:") and "ellekit" in line:
                    line = line.replace(", ellekit", "").replace("ellekit, ", "")
                lines.append(line)
            text = "".join(lines)
        else:
            raise SystemExit("unexpected Depends line in control:\n" + text)
    else:
        text = text.replace(old, new, 1)
    version = os.environ.get("RELEASE_VERSION", "8.0.11-v4.1-hybrid")
    text = text.replace("Version: 8.0.11\n", "Version: %s\n" % version, 1)
    control.write_text(text, encoding="utf-8", newline="\n")


def append_postinst(extracted: Path) -> None:
    postinst = extracted / "control" / "postinst"
    text = postinst.read_text(encoding="utf-8", errors="replace") if postinst.is_file() else "#!/bin/sh\n"
    if "autotouch-patch 8.0.11" in text and "uicache -p" in text:
        return
    if "autotouch-patch 8.0.11" in text and "uicache -p" not in text:
        text += "\nif command -v uicache >/dev/null 2>&1; then\n  uicache -p \"${JB}/Applications/AutoTouch.app\" 2>/dev/null || uicache -a 2>/dev/null || true\nfi\n"
        postinst.write_text(text, encoding="utf-8", newline="\n")
        postinst.chmod(0o755)
        return
    if not text.endswith("\n"):
        text += "\n"
    text += POSTINST_APPEND
    postinst.write_text(text, encoding="utf-8", newline="\n")
    postinst.chmod(0o755)


def main() -> None:
    version = os.environ.get("RELEASE_VERSION", "8.0.11-v4.1-hybrid")
    orig = default_orig_deb()
    crack = crack_dylib_path()
    tmp_patched = PATCH8011 / "ATTweak_patched.dylib"
    PATCH8011.mkdir(parents=True, exist_ok=True)

    print("[*] Extracting %s" % orig)
    if EXTRACTED.exists():
        shutil.rmtree(EXTRACTED)
    sys.path.insert(0, str(ROOT / "scripts"))
    from extract_deb import extract_deb

    extract_deb(orig, EXTRACTED)

    attweak_in = EXTRACTED / "data" / DYLIB_REL
    attweak_file = attweak_in / "ATTweak.dylib"
    if not attweak_file.is_file():
        raise SystemExit("ATTweak.dylib not found: %s" % attweak_file)

    print("[*] Binary-patching ATTweak.dylib (setupTimer -> RET)")
    subprocess.check_call(
        [
            sys.executable,
            str(INPUTTEXT / "patch_attweak_8011.py"),
            str(attweak_file),
            str(tmp_patched),
        ]
    )
    shutil.copy2(tmp_patched, attweak_file)

    attweak_in.mkdir(parents=True, exist_ok=True)
    shutil.copy2(crack, attweak_in / "crackATT.dylib")
    ensure_crackatt_plist(attweak_in / "crackATT.plist")
    print("[*] Injected crackATT from %s" % crack)

    relax_ellekit_depends(EXTRACTED)
    append_postinst(EXTRACTED)

    out_name = "me.autotouch.autotouch.ios8.inputtext_%s_iphoneos-arm64_patched.deb" % version
    out = ROOT / "releases" / out_name
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(
        [
            sys.executable,
            str(INPUTTEXT / "build_deb_lzma64.py"),
            str(EXTRACTED),
            str(out),
        ]
    )

    if (ROOT / "scripts" / "verify_release_deb.py").is_file():
        subprocess.check_call(
            [sys.executable, str(ROOT / "scripts" / "verify_release_deb.py"), str(out)]
        )

    alias = INPUTTEXT / "me.autotouch.autotouch.ios8.inputtext_8.0.11_iphoneos-arm64_hybrid.deb"
    shutil.copy2(out, alias)
    print("[+] %s" % out)
    print("[+] %s" % alias)


if __name__ == "__main__":
    main()
