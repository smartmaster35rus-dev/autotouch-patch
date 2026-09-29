#!/usr/bin/env python3
"""Build 8.0.11 hybrid .deb locally and publish GitHub Release 8.0.11-v1-hybrid."""

from __future__ import annotations

import json
import mimetypes
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

TAG = os.environ.get("RELEASE_TAG", "8.0.11-v1-hybrid")
DEB_NAME = f"me.autotouch.autotouch.ios8.inputtext_{TAG}_iphoneos-arm64_patched.deb"


def upload_asset(upload_url: str, path: Path) -> None:
    from github_api import request

    ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    data = path.read_bytes()
    qs = f"?name={path.name}"
    request(
        "POST",
        upload_url.replace("https://api.github.com", "") + qs,
        data=data,
        headers={"Content-Type": ctype, "Content-Length": str(len(data))},
    )


def main() -> None:
    from github_api import json_request

    crack = ROOT / "dist" / "crackATT-8011.dylib"
    if not crack.is_file():
        print("[*] dist/crackATT-8011.dylib missing — run scripts/download_ci_artifact.py or CI")
        subprocess.check_call([sys.executable, str(ROOT / "scripts" / "download_ci_artifact.py"), str(ROOT / "dist")])

    patch_dir = ROOT / "v8.0.11_inputtext" / "patch"
    patch_dir.mkdir(parents=True, exist_ok=True)
    import shutil

    shutil.copy2(crack, patch_dir / "crackATT.dylib")

    env = os.environ.copy()
    env["RELEASE_VERSION"] = TAG.replace("v", "") if TAG.startswith("8.0.11-") else TAG
    if env["RELEASE_VERSION"] == TAG:
        env["RELEASE_VERSION"] = "8.0.11-v1-hybrid"
    subprocess.check_call([sys.executable, str(ROOT / "scripts" / "build_hybrid_release_8011.py")], env=env)

    deb = ROOT / "releases" / DEB_NAME
    if not deb.is_file():
        deb = next((ROOT / "releases").glob(f"*inputtext*{TAG}*.deb"), None)
    if not deb or not deb.is_file():
        raise SystemExit("hybrid .deb not found under releases/")

    body = """## AutoTouch 8.0.11 inputtext — hybrid

- Binary-patched **ATTweak.dylib** (no 2-minute timer)
- **crackATT.dylib** — Licensed UI + auto-launch after respring

### Install (rootless, `/var/jb`)

```sh
export PATH=/var/jb/usr/bin:/var/jb/bin:/usr/bin:/bin
dpkg -i """ + deb.name + """
ldrestart
```

Expect **Licensed** in settings; auto-launch scripts without license alert.
"""
    try:
        rel = json_request("GET", f"/repos/smartmaster35rus-dev/autotouch-patch/releases/tags/{TAG}")
        print("[i] release exists:", rel.get("html_url"))
        upload_url = rel["upload_url"]
    except SystemExit:
        rel = json_request(
            "POST",
            "/repos/smartmaster35rus-dev/autotouch-patch/releases",
            {"tag_name": TAG, "name": TAG, "body": body, "draft": False, "make_latest": True},
        )
        upload_url = rel["upload_url"]
        print("[+] created release:", rel.get("html_url"))

    print("[*] uploading", deb.name)
    upload_asset(upload_url, deb)
    print("[+] published:", deb, "→", TAG)


if __name__ == "__main__":
    main()
