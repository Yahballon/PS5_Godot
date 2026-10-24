#!/usr/bin/env python3
from pathlib import Path
p=Path(__file__).resolve().parents[3]
s=(p/".github/workflows/build-godot-ps5-scene-bridge.yml").read_text()
for x in ("PPSA99845","GODOT_PS5_SCENE_PREVIEW: '1'","visual-smoke.pck",
          "Godot-PS5-Scene-Bridge-v0.1.0-","--entry homebrew/godot-ps5/native/scene_bridge_main.cpp",
          "libps5opengl-group.a","GODOT_GDSCRIPT_SCENE_FRAME_DRAWN"):
    if x=="GODOT_GDSCRIPT_SCENE_FRAME_DRAWN":
        assert x in (p/"homebrew/godot-ps5/native/scene_bridge_main.cpp").read_text()
    else: assert x in s,x
assert "gh release create" not in s
print("PASS: unique native Godot scene bridge isolated from original PS5 test titles")
