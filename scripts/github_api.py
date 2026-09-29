#!/usr/bin/env python3
"""Minimal GitHub REST helpers (token from GITHUB_TOKEN or git credential)."""

from __future__ import annotations

import json
import os
import subprocess
import ssl
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

REPO = "smartmaster35rus-dev/autotouch-patch"
CTX = ssl.create_default_context()


def token() -> str:
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        return tok.strip()
    git = os.environ.get("GIT")
    if not git:
        mingit = Path(__file__).resolve().parents[1] / ".tools" / "mingit" / "cmd" / "git.exe"
        git = str(mingit) if mingit.is_file() else "git"
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
    raise SystemExit("Need GITHUB_TOKEN or git credential for github.com")


def request(method: str, path: str, data: bytes | None = None, headers: dict | None = None) -> bytes:
    hdr = {
        "Authorization": f"Bearer {token()}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "autotouch-patch-release",
    }
    if headers:
        hdr.update(headers)
    req = Request(f"https://api.github.com{path}", data=data, method=method, headers=hdr)
    try:
        with urlopen(req, timeout=120, context=CTX) as resp:
            return resp.read()
    except HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        raise SystemExit(f"GitHub API {method} {path}: {e.code} {body}") from e


def json_request(method: str, path: str, payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode()
    raw = request(method, path, body, {"Content-Type": "application/json"} if payload else None)
    return json.loads(raw.decode()) if raw else {}
