#!/usr/bin/env python3
"""Patch AutoTouch 8.0.11 ATTweak.dylib (FAT).

1) Disable 120s license NSTimer setup (suYYKTj6MHk -> RET).
2) Disable license alert / check handlers that block auto-launch (RET at method entry).

Analysed paths (arm64 VA, IDA/disasm):
  CommandServer licenseLimitTimeout, outputLicenseTimeout, check
  Spring licenseLimitTimeout
"""
from __future__ import annotations

import struct
import sys

PAT_TIMER = bytes.fromhex("c80be8d20001679ee20313aa040080d205008052")
PROLOGUE_TIMER = bytes.fromhex("f44fbea9fd7b01a9fd430091f30300aa")
RET = bytes.fromhex("c0035fd6")

# Unique in-function bytes -> rewind to function entry (max 0x24 bytes back)
SIGNATURES: list[tuple[str, bytes, int]] = [
    ("CommandServer.licenseLimitTimeout", bytes.fromhex("c8350090081d86b92900805209682838"), 0x10),
    ("CommandServer.outputLicenseTimeout", bytes.fromhex("a83500d0000d44f9272501948f400194"), 0x0C),
    (
        "CommandServer.check",
        bytes.fromhex("ff4301d1f44f03a9fd7b04a9fd030191c8350090081986b908686838"),
        0,
    ),
    ("Spring.licenseLimitTimeout", bytes.fromhex("953500f0a0a247f92b550194fd031daa"), 0x10),
]

PROLOGUE_MARKERS = (
    bytes.fromhex("f44fbea9"),  # stp x20, x19
    bytes.fromhex("f657bda9"),  # stp x23, x22 (Spring)
    bytes.fromhex("ff4301d1"),  # sub sp (check)
)


def read_fat(data: bytes):
    magic, nfat = struct.unpack_from(">II", data, 0)
    if magic not in (0xCAFEBABE, 0xCAFEBABF):
        raise ValueError("not a FAT Mach-O: 0x%08x" % magic)
    archs = []
    for i in range(nfat):
        cputype, cpusub, offset, size, align = struct.unpack_from(">IIIII", data, 8 + i * 20)
        archs.append((cputype, cpusub, offset, size, align))
    return archs


def find_entry(sl: bytes, idx: int, max_back: int) -> int | None:
    start = max(0, idx - max_back)
    for k in range(idx, start - 1, -4):
        if k + 4 > len(sl):
            continue
        w = sl[k : k + 4]
        if w in PROLOGUE_MARKERS or w == PROLOGUE_TIMER[:4]:
            return k
    return idx if max_back == 0 else None


def patch_signatures(data: bytearray, off: int, sl: bytes, slice_name: str) -> list[int]:
    out: list[int] = []
    for label, pat, back in SIGNATURES:
        idx = sl.find(pat)
        if idx < 0:
            print("  [!] %s: signature not found for %s" % (slice_name, label))
            continue
        entry = find_entry(sl, idx, back)
        if entry is None:
            print("  [!] %s: no entry for %s @ 0x%x" % (slice_name, label, idx))
            continue
        file_off = off + entry
        if file_off not in out:
            out.append(file_off)
            print("  %s: %s @ file 0x%x -> RET" % (slice_name, label, file_off))
    return out


# Verified file offsets (fallback if pattern scan misses after rebase)
TIMER_FALLBACK: dict[str, list[int]] = {
    "arm64": [0xF8744C, 0xF8A4C8],
    "arm64e": [0x26F9580, 0x26FC9A8],
}


def patch_timers(data: bytearray, off: int, sl: bytes, slice_name: str) -> list[int]:
    out: list[int] = []
    pos = 0
    while True:
        j = sl.find(PAT_TIMER, pos)
        if j < 0:
            break
        start = None
        k = j - 4
        while k >= max(0, j - 0x400):
            if sl[k : k + 16] == PROLOGUE_TIMER:
                start = k
                break
            k -= 4
        if start is not None:
            file_off = off + start
            if file_off not in out:
                out.append(file_off)
                print("  %s: setupTimer @ file 0x%x -> RET" % (slice_name, file_off))
        pos = j + 1
    if slice_name in TIMER_FALLBACK:
        for fo in TIMER_FALLBACK[slice_name]:
            file_off = off + fo
            if fo + 4 <= len(sl) and file_off not in out:
                out.append(file_off)
                print("  %s: setupTimer (canonical) @ file 0x%x -> RET" % (slice_name, file_off))
    return out


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
        print("[*] slice %d (%s)" % (idx, name))
        patches.extend(patch_timers(data, off, sl, name))
        patches.extend(patch_signatures(data, off, sl, name))
    if not patches:
        raise SystemExit("no patches applied")
    for p in sorted(set(patches)):
        data[p : p + 4] = RET
    with open(dst, "wb") as f:
        f.write(data)
    print("patched %d site(s) -> %s" % (len(set(patches)), dst))


if __name__ == "__main__":
    main()
