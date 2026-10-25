#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Remove hidden metadata (EXIF, XMP, IPTC, comments, GPS) from gallery images, losslessly.

    python tools/strip_metadata.py               # every .jpg/.png under gallery/
    python tools/strip_metadata.py FILE [FILE…]  # just these files

Metadata can carry camera serial numbers, GPS positions, editing history or other
people's personal details, none of which belongs in a heritage gallery. The picture
itself is not re-encoded: only the metadata blocks are dropped, so quality is untouched.
Colour profiles (ICC) are kept, so colours still look right.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# JPEG markers to drop: APP1 (EXIF/XMP), APP3–APP13 (incl. IPTC/Photoshop), APP15, COM.
# Kept: APP0 (JFIF), APP2 (ICC colour profile), APP14 (Adobe colour transform).
JPEG_DROP = {0xE1, *range(0xE3, 0xEE), 0xEF, 0xFE}
PNG_DROP = {b"tEXt", b"zTXt", b"iTXt", b"eXIf", b"tIME"}


def strip_jpeg(data: bytes) -> bytes:
    if data[:2] != b"\xff\xd8":
        raise ValueError("not a JPEG")
    out, i = bytearray(b"\xff\xd8"), 2
    while i < len(data):
        if data[i] != 0xFF:
            raise ValueError(f"bad marker at {i}")
        marker = data[i + 1]
        if marker == 0xDA:  # start of scan: the rest is image data
            out += data[i:]
            return bytes(out)
        if 0xD0 <= marker <= 0xD7 or marker == 0x01:  # markers without a length
            out += data[i:i + 2]
            i += 2
            continue
        length = struct.unpack(">H", data[i + 2:i + 4])[0]
        if marker not in JPEG_DROP:
            out += data[i:i + 2 + length]
        i += 2 + length
    raise ValueError("no image data found")


def strip_png(data: bytes) -> bytes:
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    out, i = bytearray(data[:8]), 8
    while i < len(data):
        length = struct.unpack(">I", data[i:i + 4])[0]
        kind = data[i + 4:i + 8]
        chunk = data[i:i + 12 + length]
        if kind not in PNG_DROP:
            out += chunk
        i += 12 + length
        if kind == b"IEND":
            break
    return bytes(out)


def strip(path: Path) -> bool:
    data = path.read_bytes()
    clean = strip_jpeg(data) if path.suffix.lower() in (".jpg", ".jpeg") else strip_png(data)
    if clean != data:
        path.write_bytes(clean)
        return True
    return False


if __name__ == "__main__":
    targets = [Path(a) for a in sys.argv[1:]] or sorted(
        p for p in (ROOT / "gallery").rglob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    changed = [p for p in targets if strip(p)]
    for p in changed:
        print("cleaned", p.relative_to(ROOT) if p.is_absolute() else p)
    print(f"{len(changed)} of {len(targets)} file(s) had metadata removed")
