#!/usr/bin/env python3
"""Extract an iOS .deb (ar archive) into debian-binary, control/, and data/."""

from __future__ import annotations

import bz2
import gzip
import io
import lzma
import os
import sys
import tarfile
from pathlib import Path


def read_ar(path: Path) -> list[tuple[str, bytes]]:
    with path.open("rb") as f:
        magic = f.read(8)
        if magic != b"!<arch>\n":
            raise ValueError("Not an ar archive: %r" % magic)
        members: list[tuple[str, bytes]] = []
        while True:
            hdr = f.read(60)
            if len(hdr) < 60:
                break
            name = hdr[0:16].decode("ascii", "replace").strip().rstrip("/")
            size = int(hdr[48:58].decode("ascii", "replace").strip())
            data = f.read(size)
            if size % 2 == 1:
                f.read(1)
            members.append((name, data))
        return members


def decompress(name: str, data: bytes) -> bytes:
    low = name.lower()
    if low.endswith(".gz"):
        return gzip.decompress(data)
    if low.endswith(".bz2"):
        return bz2.decompress(data)
    if low.endswith(".xz"):
        return lzma.decompress(data, format=lzma.FORMAT_XZ)
    if low.endswith(".lzma"):
        return lzma.decompress(data, format=lzma.FORMAT_ALONE)
    return data


def extract_deb(deb_path: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    members = read_ar(deb_path)
    for name, payload in members:
        if name == "debian-binary":
            (out_dir / "debian-binary").write_bytes(payload)
        elif name.startswith("control.tar"):
            raw = decompress(name, payload)
            control_dir = out_dir / "control"
            control_dir.mkdir(parents=True, exist_ok=True)
            with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as tf:
                tf.extractall(control_dir)
        elif name.startswith("data.tar"):
            raw = decompress(name, payload)
            data_dir = out_dir / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as tf:
                tf.extractall(data_dir, filter="data")


def main() -> None:
    deb = Path(sys.argv[1])
    out = Path(sys.argv[2])
    extract_deb(deb, out)
    print("extracted -> %s" % out)


if __name__ == "__main__":
    main()
