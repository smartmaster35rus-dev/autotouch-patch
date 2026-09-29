#!/usr/bin/env python3
"""Download the latest successful crackATT-v2 artifact from GitHub Actions."""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

REPO = "smartmaster35rus-dev/autotouch-patch"
ARTIFACT_NAME = "crackATT-v2"


def github_token() -> str:
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        return tok.strip()
    git = os.environ.get("GIT", "git")
    proc = subprocess.run(
        [git, "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True,
        text=True,
        check=False,
    )
    for line in proc.stdout.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("Set GITHUB_TOKEN or authenticate git for github.com")


def api(path: str, token: str) -> dict:
    req = Request(
        f"https://api.github.com{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def main() -> None:
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist")
    out_dir.mkdir(parents=True, exist_ok=True)
    token = github_token()
    runs = api(f"/repos/{REPO}/actions/runs?per_page=10&status=completed&conclusion=success", token)
    run_id = None
    for run in runs.get("workflow_runs", []):
        if run.get("name") == "Build crackATT v2" and run.get("conclusion") == "success":
            run_id = run["id"]
            break
    if not run_id:
        raise SystemExit("No successful Build crackATT v2 run found")

    arts = api(f"/repos/{REPO}/actions/runs/{run_id}/artifacts", token)
    art = next((a for a in arts.get("artifacts", []) if a.get("name") == ARTIFACT_NAME), None)
    if not art:
        raise SystemExit(f"Artifact {ARTIFACT_NAME!r} not found on run {run_id}")

    req = Request(
        art["archive_download_url"],
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
    )
    with urlopen(req, timeout=120) as resp:
        zdata = resp.read()
    with zipfile.ZipFile(io.BytesIO(zdata)) as zf:
        zf.extractall(out_dir)
    print("[+] extracted to", out_dir.resolve())
    for p in sorted(out_dir.iterdir()):
        print("   ", p.name, p.stat().st_size)


if __name__ == "__main__":
    main()
