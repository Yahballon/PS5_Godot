#!/usr/bin/env python3
"""Godot PS5 --main-pack requires OVERRIDE_PATH_ENABLED in the engine."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
script=(root/"scripts/build-engine.sh").read_text()
entry=(root/"engine/platform/ps5/godot_ps5.cpp").read_text()
assert 'disable_path_overrides=no' in script, "SCons must enable project/PCK CLI paths"
assert script.count("disable_path_overrides=no")==1
assert 'char main_pack[] = "--main-pack";' in entry
assert 'Main::setup("godot.ps5", count, args)' in entry
assert 'constexpr int count = 3;' in entry, "Headless engine CLI must preserve three arguments"
assert 'constexpr int count = 8;' in entry, "Opt-in GLES3 driver CLI must select native PS5"
print("PASS: PS5 engine includes --main-pack support for bundled smoke.pck")
