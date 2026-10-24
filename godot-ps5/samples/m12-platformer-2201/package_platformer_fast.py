#!/usr/bin/env python3
"""Zip genuine Godot 4.7 platformer PCK for already hardware-proven PS5 v0.1.6."""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import struct
import zipfile

PCK = "m12c-platformer-asset2201.pck"
ZIP = "GodotPS5-M12c-Platformer-FAST-PS5-TEST.zip"
UPSTREAM = "https://github.com/AdilDevStuff/2D-Platformer-Starter-Kit"
COMMIT = "a48fc994cbcb168be472df84f2e13b55d2a2792f"

def pack(pck: Path, original_license: Path, out_dir: Path) -> tuple[Path, str]:
    if pck.name != PCK:
        raise ValueError("expected the M12 project PCK")
    data = pck.read_bytes()
    if len(data) < 100_000 or data[:4] != b"GDPC":
        raise ValueError("missing real multi-resource Godot PCK")
    fmt, major, minor = struct.unpack_from("<III", data, 4)
    if fmt not in (2,3,4) or major != 4 or minor != 7:
        raise ValueError("not a Godot 4.7 PCK")
    mit = original_license.read_text(encoding="utf-8")
    if not mit.startswith("MIT License"):
        raise ValueError("upstream MIT license must be preserved")
    sha = hashlib.sha256(data).hexdigest()
    note = (
        "Godot PS5 M12 – real third-party game compatibility test!\n"
        "Asset: 2D Platformer - Starter Kit 1.1.1 (Godot Asset Library #2201)\n"
        "Author: G2P Studios / AdilDevStuff. Original LICENSE (MIT) included.\n"
        f"Source: {UPSTREAM} at pinned commit {COMMIT}\n"
        "Requires installed PPSA99847 Godot PS5 v0.1.6 with native audio.\n"
        "Extract this ZIP, copy GodotPS5 contents into /data/GodotPS5/\n"
        "Adds games/m12c-platformer-asset2201.pck and replaces launch.txt ONLY.\n"
        "Does not replace eboot, delete other PCKs or change save data.\n"
        "Controls: LEFT STICK or D-PAD = move; CROSS (X) = jump.\n"
        "Test: 2 levels, coin score, camera, collisions, sounds, animations.\n"
        "This PCK was imported/host-tested on original Godot 4.7.2 only.\n"
        "PS5 playability and audio for this third-party project require testing.\n"
        "Log: /data/GodotPS5/gles3-stdout.log, gles3-stderr.log, gles3-runtime.log.\n"
        "To return to bundled Pong, delete /data/GodotPS5/launch.txt.\n"
        "Upstream art credits: Kenney.nl; sound effects: Gdfxr.\n"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / ZIP
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        z.writestr(f"GodotPS5/games/{PCK}", data)
        z.writestr("GodotPS5/launch.txt", PCK+"\n")
        z.writestr("GodotPS5/M12c-Platformer-README.txt", note)
        z.writestr("GodotPS5/M12c-Platformer-Original-LICENSE.txt", mit)
        z.writestr("GodotPS5/m12c-platformer.sha256", sha+"  games/"+PCK+"\n")
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        assert z.read("GodotPS5/launch.txt") == (PCK+"\n").encode()
        assert z.read(f"GodotPS5/games/{PCK}") == data
    print("GODOT_PS5_M12C_INSTALL_ZIP_OK",out,"sha256=",sha)
    return out, sha

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("pck",type=Path)
    p.add_argument("license",type=Path)
    p.add_argument("output",type=Path)
    a=p.parse_args()
    pack(a.pck,a.license,a.output)
