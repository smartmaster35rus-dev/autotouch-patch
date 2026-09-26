#!/usr/bin/env python3
"""Fail the build if the patched .deb is missing crackATT or AutoTouch bundle filter."""

from __future__ import annotations

import plistlib
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_BUNDLES = (
    "com.apple.backboardd",
    "com.apple.springboard",
    "me.autotouch.AutoTouch.ios8",
)
DYLIB_REL = Path("data/var/jb/Library/MobileSubstrate/DynamicLibraries")


def main() -> None:
    deb = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if deb is None or not deb.is_file():
        raise SystemExit("usage: verify_release_deb.py path/to/package.deb")

    sys.path.insert(0, str(ROOT / "scripts"))
    from extract_deb import extract_deb

    work = Path(tempfile.mkdtemp(prefix="verify_deb_"))
    extract_deb(deb, work)
    dl = work / DYLIB_REL
    errors: list[str] = []

    for name in ("crackATT.dylib", "crackATT.plist"):
        path = dl / name
        if not path.is_file():
            errors.append(f"missing {name} in .deb")
        elif name == "crackATT.dylib" and path.stat().st_size < 1000:
            errors.append(f"{name} too small ({path.stat().st_size} bytes)")

    plist_path = dl / "crackATT.plist"
    if plist_path.is_file():
        data = plistlib.load(plist_path.open("rb"))
        bundles = list(data.get("Filter", {}).get("Bundles", []))
        for req in REQUIRED_BUNDLES:
            if req not in bundles:
                errors.append(f"crackATT.plist missing bundle {req!r} (have {bundles})")

    attweak = dl / "ATTweak.plist"
    if attweak.is_file():
        att_b = plistlib.load(attweak.open("rb")).get("Filter", {}).get("Bundles", [])
        if "me.autotouch.AutoTouch.ios8" in att_b:
            print("[i] ATTweak.plist also lists AutoTouch (optional)")
        else:
            print("[i] ATTweak.plist has %d bundles (official) — injection is via crackATT.plist" % len(att_b))

    if errors:
        for err in errors:
            print("[!]", err)
        raise SystemExit(1)

    print("[+] deb OK:", deb.name)
    print("[+] crackATT.plist bundles:", bundles)


if __name__ == "__main__":
    main()
