#!/usr/bin/env python3
"""Extract a .deb package to a directory."""

from __future__ import annotations

import io
import shutil
import sys
import tarfile
from pathlib import Path


def extract_deb(deb_path: Path, out_dir: Path) -> None:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    with deb_path.open("rb") as handle:
        assert handle.read(8) == b"!<arch>\n"
        while True:
            header = handle.read(60)
            if len(header) < 60:
                break
            name = header[:16].decode().strip()
            size = int(header[48:58].decode().strip())
            data = handle.read(size)
            if size % 2:
                handle.read(1)
            if name == "debian-binary":
                (out_dir / "debian-binary").write_bytes(data)
            elif name.startswith("control"):
                tarfile.open(fileobj=io.BytesIO(data)).extractall(out_dir / "control")
            elif name.startswith("data"):
                tarfile.open(fileobj=io.BytesIO(data)).extractall(out_dir / "data")

    print(f"Extracted {deb_path.name} -> {out_dir}")


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: extract_deb.py <package.deb> <output_dir>")
        raise SystemExit(1)
    extract_deb(Path(sys.argv[1]), Path(sys.argv[2]))


if __name__ == "__main__":
    main()
