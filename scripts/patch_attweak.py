#!/usr/bin/env python3
"""Patch AutoTouch 8.5.5 ATTweak.dylib (FAT) — disable 120s license NSTimer setupTimer paths."""

from __future__ import annotations

import struct
import sys

PAT_TIMER = bytes.fromhex(
    "c80be8d20001679ee20313aa040080d205008052"
)  # mov x8,#0x405e..; fmov d0,x8; mov x2,x19; mov x4,#0; mov w5,#0
PROLOGUE = bytes.fromhex("f44fbea9fd7b01a9fd430091f30300aa")
RET = bytes.fromhex("c0035fd6")


def read_fat(data: bytes):
    magic, nfat = struct.unpack_from(">II", data, 0)
    if magic not in (0xCAFEBABE, 0xCAFEBABF):
        raise ValueError("not a FAT Mach-O: 0x%08x" % magic)
    archs = []
    for i in range(nfat):
        cputype, cpusub, offset, size, align = struct.unpack_from(">IIIII", data, 8 + i * 20)
        archs.append((cputype, cpusub, offset, size, align))
    return archs


def main() -> None:
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, "rb") as f:
        data = bytearray(f.read())
    archs = read_fat(data)
    print("FAT slices: %d" % len(archs))
    patches: list[int] = []
    for idx, (ct, cs, off, size, al) in enumerate(archs):
        sl = data[off : off + size]
        name = "arm64" if cs == 0 else ("arm64e" if cs == 0x80000002 else "cpu0x%x/0x%x" % (ct, cs))
        pos = 0
        found = 0
        while True:
            j = sl.find(PAT_TIMER, pos)
            if j < 0:
                break
            start = None
            k = j - 4
            while k >= max(0, j - 0x100):
                if sl[k : k + 16] == PROLOGUE:
                    start = k
                    break
                k -= 4
            if start is None:
                print("  [!] slice %d (%s): timer seq @0x%x but no prologue" % (idx, name, j))
            else:
                patches.append(off + start)
                found += 1
                print(
                    "  slice %d (%s): setupTimer @ VA 0x%x (file 0x%x) -> RET"
                    % (idx, name, start, off + start)
                )
            pos = j + 1
        if found == 0:
            print("  [!] slice %d (%s): NO timer sequence found" % (idx, name))
    if not patches:
        raise SystemExit("no patches applied")
    for p in patches:
        data[p : p + 4] = RET
    with open(dst, "wb") as f:
        f.write(data)
    print("patched %d function(s) -> %s" % (len(patches), dst))


if __name__ == "__main__":
    main()
