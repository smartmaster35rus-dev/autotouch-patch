#!/usr/bin/env python3
"""Prepare arm64/extracted from current release and inject patched crackATT."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH_DIR = ROOT / "patch"
EXTRACTED = ROOT / "arm64" / "extracted"
RELEASE_DEB = ROOT / "releases" / "me.autotouch.autotouch.ios8_8.5.5_iphoneos-arm64_patched.deb"
CRACK_DEST = (
    EXTRACTED
    / "data"
    / "var"
    / "jb"
    / "Library"
    / "MobileSubstrate"
    / "DynamicLibraries"
)


def main() -> None:
    if not (PATCH_DIR / "crackATT.dylib").exists():
        print("Missing patch/crackATT.dylib — build tweak first")
        raise SystemExit(1)
    if not RELEASE_DEB.exists():
        print(f"Missing base release deb: {RELEASE_DEB}")
        raise SystemExit(1)

    tmp = ROOT / "tmp_prepare_extract"
    if tmp.exists():
        shutil.rmtree(tmp)

    sys.path.insert(0, str(ROOT / "scripts"))
    from extract_deb import extract_deb

    extract_deb(RELEASE_DEB, tmp)
    if EXTRACTED.exists():
        shutil.rmtree(EXTRACTED)
    shutil.copytree(tmp, EXTRACTED)
    shutil.rmtree(tmp)

    CRACK_DEST.mkdir(parents=True, exist_ok=True)
    for name in ("crackATT.dylib", "crackATT.plist"):
        shutil.copy2(PATCH_DIR / name, CRACK_DEST / name)

    dylib = CRACK_DEST / "crackATT.dylib"
    print(f"Injected {dylib} ({dylib.stat().st_size} bytes)")
    print(f"Ready: {EXTRACTED}")


if __name__ == "__main__":
    main()
