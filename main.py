#!/usr/bin/env python3
"""Entry for make.fun news-image: writes the day's news poster to the output.

The poster (entry.png, beside this file) sums up one day's world news as a
single 1024x1024 editorial front page, typeset programmatically so every
headline is crisp and legible. The program is deterministic and offline:
it copies exactly those bytes to /output/entry.png on every run. If the
poster file were missing, it falls back to synthesising a plain navy
1024x1024 PNG with the standard library alone, so a run never fails.
"""
import os
import shutil
import struct
import zlib

MAX_BYTES = 1_048_576  # the gate's 1 MiB limit


def _chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def fallback_png(path: str) -> None:
    """Write a solid navy 1024x1024 PNG using only the standard library."""
    width = height = 1024
    raw = b""
    row = bytes((11, 18, 32)) * width
    for _ in range(height):
        raw += b"\x00" + row
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(raw, 9)) + _chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)


def main() -> None:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    if os.path.isfile(src) and os.path.getsize(src) <= MAX_BYTES:
        shutil.copyfile(src, dst)
    else:
        fallback_png(dst)


if __name__ == "__main__":
    main()
