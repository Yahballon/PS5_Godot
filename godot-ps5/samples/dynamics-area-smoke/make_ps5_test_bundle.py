#!/usr/bin/env python3
"""Generate PS5-ready M10a ZIP from an actual host-validated Godot 4.7.2 PCK."""
from pathlib import Path
import argparse
import hashlib
import struct
import zipfile


def bundle(pack: Path, out: Path) -> tuple[Path, str]:
    data = pack.read_bytes()
    if len(data) < 64 or data[:4] != b"GDPC":
        raise ValueError("not a Godot PCK")
    fmt, major, minor = struct.unpack_from("<III", data, 4)
    if not (2 <= fmt <= 4 and major == 4 and minor == 7):
        raise ValueError(f"unsupported Godot PCK: format={fmt} Godot={major}.{minor}")
    out.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(data).hexdigest()
    result = out / "GodotPS5-M10a-RIGIDBODY-AREA-TEST.zip"
    readme = (
        "GODOT PS5 M10a: REAL RigidBody2D + Area2D acceptance.\n"
        "PS5 engine PPSA99847 v0.1.3 is REQUIRED; older v0.1.2 uses DummyPhysicsServer2D.\n"
        "Extract this ZIP, then copy GodotPS5/* to /data/GodotPS5/.\n"
        "The included launch.txt selects dynamics-area-smoke.pck.\n"
        "Expect a yellow ball to fall through a cyan trigger region then land\n"
        "on a magenta platform. Three signal lights become green, then it quits.\n"
        "No hardcoded movement/overlap: all events come from original physics.\n"
        "Read /data/GodotPS5/gles3-stdout.log for AREA_ENTER_OK,\n"
        "AREA_EXIT_OK, RIGID_CONTACT_OK and M10A_TEST_PASS.\n"
        "Read /data/GodotPS5/gles3-runtime.log for GODOT_RETURN=0, EGL_CLOSED.\n"
        "Delete launch.txt to restore Pong, or choose an earlier PCK name.\n"
        "This is a PS5-HARDWARE-UNTESTED fixture even if CI is green.\n"
    )
    with zipfile.ZipFile(result, "w", zipfile.ZIP_DEFLATED, compresslevel=7) as z:
        z.writestr("GodotPS5/games/dynamics-area-smoke.pck", data)
        z.writestr("GodotPS5/launch.txt", "dynamics-area-smoke.pck\n")
        z.writestr("GodotPS5/M10a-README.txt", readme)
        z.writestr("GodotPS5/dynamics-area-smoke.sha256", f"{digest}  games/dynamics-area-smoke.pck\n")
    with zipfile.ZipFile(result) as z:
        assert z.testzip() is None
        assert z.read("GodotPS5/games/dynamics-area-smoke.pck") == data
        assert z.read("GodotPS5/launch.txt") == b"dynamics-area-smoke.pck\n"
    return result, digest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pack", type=Path)
    parser.add_argument("out", type=Path)
    params = parser.parse_args()
    path, digest = bundle(params.pack, params.out)
    print("GODOT_PS5_M10A_BUNDLE_READY", path, "sha256=", digest)
