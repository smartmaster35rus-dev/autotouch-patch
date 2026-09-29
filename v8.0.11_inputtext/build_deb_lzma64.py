#!/usr/bin/env python3
"""Rebuild patched .deb with an LZMA1 64MB dictionary (matches the original
package's data.tar.lzma properties: props=0x5d, dict=0x4000000)."""
from __future__ import annotations

import io
import lzma
import sys
import tarfile
import time
from pathlib import Path

MOBILE_UID = 501
WHEEL_GID = 20
UNAME = "root"
GNAME = "wheel"
DICT = 0x4000000  # 64 MiB
_MAINT_SCRIPTS = {"preinst", "postinst", "prerm", "postrm", "extrainst_"}


def _base(arcname, mtime=None):
    info = tarfile.TarInfo(name=arcname)
    info.uid = MOBILE_UID
    info.gid = WHEEL_GID
    info.uname = UNAME
    info.gname = GNAME
    info.mtime = mtime if mtime is not None else int(time.time())
    return info


def _dir(arcname):
    info = _base(arcname)
    info.type = tarfile.DIRTYPE
    info.mode = 0o755
    info.size = 0
    return info


def _file(path: Path, arcname: str):
    info = _base(arcname, int(path.stat().st_mtime))
    info.type = tarfile.REGTYPE
    name = Path(arcname).name
    if (name in _MAINT_SCRIPTS or arcname.endswith((".dylib", ".so"))
            or arcname.endswith(("autotouch", "AutoTouch")) or "/bin/" in arcname):
        info.mode = 0o755
    else:
        info.mode = 0o644
    info.size = path.stat().st_size
    return info


def tar_directory(source: Path) -> bytes:
    buf = io.BytesIO()
    files, dirs = [], set()
    for p in sorted(source.rglob("*")):
        if p.is_dir():
            continue
        arcname = p.relative_to(source).as_posix()
        files.append((p, arcname))
        parts = arcname.split("/")
        for i in range(len(parts) - 1):
            dirs.add("/".join(parts[:i + 1]))
    with tarfile.open(fileobj=buf, mode="w", format=tarfile.GNU_FORMAT) as tar:
        tar.addfile(_dir("."))
        for d in sorted(dirs, key=lambda s: (s.count("/"), s)):
            tar.addfile(_dir(d))
        for p, arcname in files:
            with p.open("rb") as fh:
                tar.addfile(_file(p, arcname), fh)
    return lzma.compress(
        buf.getvalue(),
        format=lzma.FORMAT_ALONE,
        filters=[{"id": lzma.FILTER_LZMA1, "dict_size": DICT, "lc": 3, "lp": 0, "pb": 2}],
    )


def tar_directory_gz(source: Path) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz", format=tarfile.GNU_FORMAT) as tar:
        for p in sorted(source.rglob("*")):
            if p.is_dir():
                continue
            with p.open("rb") as fh:
                tar.addfile(_file(p, p.relative_to(source).as_posix()), fh)
    return buf.getvalue()


def ar_member(name: str, payload: bytes) -> bytes:
    h = bytearray(60)
    h[0:16] = name.encode("ascii").ljust(16)
    h[16:28] = str(int(time.time())).ljust(12)[:12].encode("ascii")
    h[28:34] = b"0     "
    h[34:40] = b"0     "
    h[40:48] = b"100644  "
    h[48:58] = str(len(payload)).encode("ascii").ljust(10)
    h[58:60] = b"`\n"
    out = bytes(h) + payload
    if len(out) % 2:
        out += b"\n"
    return out


def main():
    extracted = Path(sys.argv[1])
    output = Path(sys.argv[2])
    db = (extracted / "debian-binary").read_bytes()
    ctrl = tar_directory_gz(extracted / "control")
    data = tar_directory(extracted / "data")
    out = bytearray(b"!<arch>\n")
    out += ar_member("debian-binary", db)
    out += ar_member("control.tar.gz", ctrl)
    out += ar_member("data.tar.lzma", data)
    output.write_bytes(out)
    print(f"Wrote {output} ({output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
