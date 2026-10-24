#!/usr/bin/env python3
"""Package a host-verified genuine Godot 4 PCK for PS5 M9 physics testing."""
import argparse
import hashlib
from pathlib import Path
import struct
import zipfile


def make_bundle(pack: Path, output_dir: Path) -> tuple[Path, str]:
    data = pack.read_bytes()
    if len(data) < 64 or data[:4] != b"GDPC":
        raise ValueError("not a real Godot PCK")
    fmt, major, minor = struct.unpack_from("<III", data, 4)
    if not (2 <= fmt <= 4 and major == 4 and minor <= 7):
        raise ValueError("incompatible Godot 4 PCK")
    output_dir.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256(data).hexdigest()
    destination = output_dir / "GodotPS5-M9a-REAL-PHYSICS-TEST.zip"
    instructions = (
        "Godot PS5 M9a PhysicsServer2D REAL collision acceptance\n"
        "Use existing PPSA99847 v0.1.2, no native app update required.\n"
        "Copy GodotPS5/ contents into /data/GodotPS5/.\n"
        "The supplied launch.txt selects games/physics-smoke.pck.\n"
        "Cyan CharacterBody2D must collide with magenta StaticBody2D wall.\n"
        "Green result requires CharacterBody2D.move_and_collide() contact,\n"
        "correct StaticBody2D collider and correct contact normal.\n"
        "Examine gles3-stdout.log for GODOT_PS5_M9_REAL_COLLISION_OK and\n"
        "GODOT_PS5_M9_TEST_PASS. If it passes through, physics is NOT proven.\n"
        "Remove launch.txt after testing to restore bundled Pong.\n"
    )
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=7) as archive:
        archive.writestr("GodotPS5/games/physics-smoke.pck", data)
        archive.writestr("GodotPS5/launch.txt", "physics-smoke.pck\n")
        archive.writestr("GodotPS5/M9a-README.txt", instructions)
        archive.writestr("GodotPS5/physics-smoke.sha256", f"{sha}  games/physics-smoke.pck\n")
    with zipfile.ZipFile(destination) as archive:
        assert archive.testzip() is None
        assert archive.read("GodotPS5/games/physics-smoke.pck") == data
        assert archive.read("GodotPS5/launch.txt") == b"physics-smoke.pck\n"
    return destination, sha


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pack", type=Path)
    parser.add_argument("output", type=Path)
    options = parser.parse_args()
    path, digest = make_bundle(options.pack, options.output)
    print(f"GODOT_PS5_M9_BUNDLE_READY {path} sha256={digest}")
