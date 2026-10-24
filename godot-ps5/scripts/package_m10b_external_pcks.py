#!/usr/bin/env python3
"""Create TWO data-only PS5 test ZIPs from host-tested Godot 4.7.2 PCKs.

The two fixtures are deliberately separate: a font regression cannot hide a
working physics test, and a tilemap regression cannot falsify font support.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import struct
import zipfile

TESTS = {
    "tilemap": ("m10b-tilemap.pck", "GodotPS5-M10b-TILEMAP-PS5-TEST.zip"),
    "font-ui": ("m10b-font-ui.pck", "GodotPS5-M10b-FONT-UI-PS5-TEST.zip"),
}


def check_pck(data: bytes) -> None:
    if len(data) < 64 or data[:4] != b"GDPC":
        raise ValueError("not a Godot PCK")
    pck_version, major, minor = struct.unpack_from("<III", data, 4)
    if not (2 <= pck_version <= 4 and major == 4 and minor == 7):
        raise ValueError(f"wrong Godot PCK format/version {pck_version}, {major}.{minor}")


def bundle(name: str, pack: Path, output: Path) -> tuple[Path, str]:
    if name not in TESTS:
        raise ValueError("unknown test")
    pck_name, zip_name = TESTS[name]
    assert pack.name == pck_name, (pack, pck_name)
    data = pack.read_bytes()
    check_pck(data)
    output.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(data).hexdigest()
    instructions = (
        "GODOT PS5 M10b independent test – " + name + "\n"
        "Requires hardware-confirmed PPSA99847 v0.1.3.\n"
        "No native eboot.bin change needed.\n"
        "Extract the ZIP and copy CONTENTS of GodotPS5/ to /data/GodotPS5/.\n"
        "This only replaces launch.txt and adds a new .pck.\n"
        "To switch between tests, set launch.txt to m10b-tilemap.pck\n"
        "or m10b-font-ui.pck with a newline, then restart PPSA99847.\n"
        "For tilemap: cyan square must stop on an actual pink tile platform.\n"
        "For font-ui: visually inspect five Godot Labels and umlauts.\n"
        "Collect gles3-stdout.log, gles3-runtime.log, gles3-stderr.log.\n"
        "The font is Press Start 2P (SIL OFL 1.1); license is inside its PCK.\n"
        "Remove launch.txt to restore the bundled Pong.\n"
        "Host PASS does not prove the behavior on physical PS5 hardware.\n"
    )
    result = output / zip_name
    with zipfile.ZipFile(result, "w", zipfile.ZIP_DEFLATED, compresslevel=8) as z:
        z.writestr(f"GodotPS5/games/{pck_name}", data)
        z.writestr("GodotPS5/launch.txt", pck_name + "\n")
        z.writestr("GodotPS5/M10b-README.txt", instructions)
        z.writestr(f"GodotPS5/{name}.sha256", f"{digest}  games/{pck_name}\n")
    with zipfile.ZipFile(result) as z:
        assert z.testzip() is None
        assert z.read("GodotPS5/launch.txt") == (pck_name+"\n").encode()
        assert z.read(f"GodotPS5/games/{pck_name}") == data
    return result, digest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("test", choices=sorted(TESTS))
    parser.add_argument("pck", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result, checksum = bundle(args.test, args.pck, args.output)
    print("GODOT_PS5_M10B_BUNDLE_OK", result, "sha256=", checksum)
