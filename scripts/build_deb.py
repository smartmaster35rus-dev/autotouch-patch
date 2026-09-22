#!/usr/bin/env python3
"""Rebuild a patched .deb from extracted package contents."""

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


def base_tarinfo(arcname: str, mtime: int | None = None) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name=arcname)
    info.uid = MOBILE_UID
    info.gid = WHEEL_GID
    info.uname = UNAME
    info.gname = GNAME
    info.mtime = mtime if mtime is not None else int(time.time())
    return info


def tarinfo_for_dir(arcname: str) -> tarfile.TarInfo:
    info = base_tarinfo(arcname)
    info.type = tarfile.DIRTYPE
    info.mode = 0o755
    info.size = 0
    return info


def tarinfo_for_file(path: Path, arcname: str) -> tarfile.TarInfo:
    info = base_tarinfo(arcname, int(path.stat().st_mtime))
    info.type = tarfile.REGTYPE
    if arcname.endswith((".dylib", ".so")) or arcname.endswith(
        ("autotouch", "AutoTouch")
    ) or "/bin/" in arcname:
        info.mode = 0o755
    else:
        info.mode = 0o644
    info.size = path.stat().st_size
    return info


def tar_directory(source_dir: Path) -> bytes:
    buf = io.BytesIO()
    files: list[tuple[Path, str]] = []
    dirs: set[str] = set()

    for path in sorted(source_dir.rglob("*")):
        if path.is_dir():
            continue
        arcname = path.relative_to(source_dir).as_posix()
        files.append((path, arcname))
        parts = arcname.split("/")
        for i in range(len(parts) - 1):
            dirs.add("/".join(parts[: i + 1]))

    with tarfile.open(fileobj=buf, mode="w", format=tarfile.GNU_FORMAT) as tar:
        tar.addfile(tarinfo_for_dir("."))
        for dirname in sorted(dirs, key=lambda s: (s.count("/"), s)):
            tar.addfile(tarinfo_for_dir(dirname))
        for path, arcname in files:
            info = tarinfo_for_file(path, arcname)
            with path.open("rb") as handle:
                tar.addfile(info, handle)

    return lzma.compress(
        buf.getvalue(),
        format=lzma.FORMAT_ALONE,
        filters=[{"id": lzma.FILTER_LZMA1}],
    )


def tar_directory_gz(source_dir: Path) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz", format=tarfile.GNU_FORMAT) as tar:
        for path in sorted(source_dir.rglob("*")):
            if path.is_dir():
                continue
            arcname = path.relative_to(source_dir).as_posix()
            info = tarinfo_for_file(path, arcname)
            with path.open("rb") as handle:
                tar.addfile(info, handle)
    return buf.getvalue()


def build_ar_member(name: str, payload: bytes) -> bytes:
    header = bytearray(60)
    header[0:16] = name.encode("ascii").ljust(16)
    header[16:28] = str(int(time.time())).ljust(12)[:12].encode("ascii")
    header[28:34] = b"0     "
    header[34:40] = b"0     "
    header[40:48] = b"100644  "
    header[48:58] = str(len(payload)).encode("ascii").ljust(10)
    header[58:60] = b"`\n"
    out = bytes(header) + payload
    if len(out) % 2 == 1:
        out += b"\n"
    return out


def build_deb(extracted: Path, output: Path) -> None:
    debian_binary = (extracted / "debian-binary").read_bytes()
    control_tar = tar_directory_gz(extracted / "control")
    data_tar = tar_directory(extracted / "data")

    out = bytearray(b"!<arch>\n")
    out += build_ar_member("debian-binary", debian_binary)
    out += build_ar_member("control.tar.gz", control_tar)
    out += build_ar_member("data.tar.lzma", data_tar)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(out)
    print(f"Wrote {output} ({output.stat().st_size} bytes)")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    extracted = Path(sys.argv[1]) if len(sys.argv) > 1 else repo_root / "arm64" / "extracted"
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else repo_root / "releases" / (
        "me.autotouch.autotouch.ios8_8.5.5_iphoneos-arm64_patched.deb"
    )
    build_deb(extracted, output)


if __name__ == "__main__":
    main()
