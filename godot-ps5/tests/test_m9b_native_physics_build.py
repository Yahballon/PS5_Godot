#!/usr/bin/env python3
"""M9b regression: native PS5 runner must link actual upstream GodotPhysics2D."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
build=(root/"scripts/build-engine.sh").read_text()
m9=(root.parent.parent/".github/workflows/build-godot-ps5-m9b-native-physics.yml").read_text()
known_good=(root.parent.parent/".github/workflows/build-godot-ps5-gles3-canvas.yml").read_text()
assert 'GODOT_PS5_PHYSICS2D:-0' in build
assert 'module_godot_physics_2d_enabled=yes' in build
assert 'disable_physics_2d=no' in build
assert 'GODOT_PS5_PHYSICS2D: \'1\'' in m9
assert 'libmodule_godot_physics_2d.' in m9
assert "contentVersion='01.000.004'" in m9
assert "Godot-PS5-M9b-NATIVE-PHYSICS-v0.1.3-PS5-HARDWARE-UNTESTED" in m9
assert "GodotPS5-M9b-Physics-Godot4-PCK-HOST-ONLY" in m9
assert "GODOT_PS5_M9_REAL_COLLISION_OK" in m9
assert "GODOT_PS5_M9_TEST_PASS" in m9
assert "GODOT_PS5_PHYSICS2D:" not in known_good
assert "contentVersion='01.000.003'" in known_good
print("PASS: M9b explicitly links real GodotPhysics2D; known-good v0.1.2 stays unchanged")
