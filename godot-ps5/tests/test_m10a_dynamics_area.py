#!/usr/bin/env python3
"""Static/mock tests: separate from the REAL Godot 4.7.2 runtime CI acceptance."""
import hashlib
import importlib.util
from pathlib import Path
import struct
import tempfile
import zipfile

root=Path(__file__).resolve().parents[1]/"samples/dynamics-area-smoke"
script=(root/"main.gd").read_text()
for token in [
    "RigidBody2D.new()", "StaticBody2D.new()", "Area2D.new()",
    "CircleShape2D.new()", "RectangleShape2D.new()",
    "sensor.body_entered.connect(", "sensor.body_exited.connect(",
    "ball.body_entered.connect(", "ball.gravity_scale = 1.0",
    "GODOT_PS5_M10A_AREA_ENTER_OK", "GODOT_PS5_M10A_AREA_EXIT_OK",
    "GODOT_PS5_M10A_RIGID_CONTACT_OK", "GODOT_PS5_M10A_TEST_PASS",
]:
    assert token in script, f"missing original Godot API acceptance: {token}"
assert "ball.position +=" not in script
assert "ball.linear_velocity =" not in script
pack=(root/"make_pack.gd").read_text()
for name in ("project.godot","main.gd","main.tscn"):
    assert f'"{name}"' in pack

spec=importlib.util.spec_from_file_location("m10pack",root/"make_ps5_test_bundle.py")
assert spec and spec.loader
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory() as td:
    folder=Path(td)
    fake=folder/"test.pck"
    data=b"GDPC"+struct.pack("<III",3,4,7)+bytes(128)
    fake.write_bytes(data)
    dest,checksum=module.bundle(fake,folder/"out")
    assert checksum==hashlib.sha256(data).hexdigest()
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        assert z.read("GodotPS5/games/dynamics-area-smoke.pck")==data
        assert z.read("GodotPS5/launch.txt")==b"dynamics-area-smoke.pck\n"
        assert checksum.encode() in z.read("GodotPS5/dynamics-area-smoke.sha256")
    fake.write_bytes(b"BAD!"+bytes(128))
    try: module.bundle(fake,folder/"out")
    except ValueError: pass
    else: raise AssertionError("invalid PCK accepted")
print("PASS: M10a source prerequisites and PS5 PCK ZIP packager mock test")
