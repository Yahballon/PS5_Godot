#!/usr/bin/env python3
import argparse
import hashlib
from pathlib import Path
import struct
import zipfile

TESTS = {
    "audio": ("m11-audio.pck", "GodotPS5-M11a-AUDIO-TEST.zip"),
    "saves": ("m11-saves.pck", "GodotPS5-M11b-SAVES-TEST.zip"),
    "saves-v2": ("m11-saves-v2.pck", "GodotPS5-M11b2-SAVES-VISIBLE-FIX.zip"),
}

def bundle(mode, source, directory):
    if mode not in TESTS:
        raise ValueError("invalid mode")
    filename, zipname = TESTS[mode]
    if source.name != filename:
        raise ValueError("mismatched filename")
    data = source.read_bytes()
    if len(data) < 64 or data[:4] != b"GDPC":
        raise ValueError("bad PCK")
    fmt, major, minor = struct.unpack_from("<III", data, 4)
    if fmt not in (2, 3, 4) or major != 4 or minor != 7:
        raise ValueError("not Godot 4.7 PCK")
    directory.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(data).hexdigest()
    instructions = (
        "PPSA99847 v0.1.4 needed. Copy GodotPS5 contents into /data/GodotPS5/\n"
        "Changes launch.txt only; previous PCKs remain.\n"
        "Audio: six notes must be HEARD; PLAYER_STARTED does not prove audible sound.\n"
        "Saves: launch app TWICE. Only the second launch can confirm persistence.\n"
        "Collect /data/GodotPS5/gles3-stdout.log and runtime/stderr logs.\n"
    )
    out = directory / zipname
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=8) as z:
        z.writestr("GodotPS5/games/" + filename, data)
        z.writestr("GodotPS5/launch.txt", filename + "\n")
        z.writestr("GodotPS5/M11-README.txt", instructions)
        z.writestr("GodotPS5/m11.sha256", digest + "  games/" + filename + "\n")
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        assert z.read("GodotPS5/launch.txt") == (filename + "\n").encode()
    return out, digest

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=sorted(TESTS))
    parser.add_argument("source", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    path, sha = bundle(args.mode, args.source, args.out)
    print("GODOT_PS5_M11_BUNDLE_READY", path, sha)
