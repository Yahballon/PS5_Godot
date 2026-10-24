#!/usr/bin/env python3
"""Verify that the graphical preview is powered by real Godot scene state."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]
os=(p/"engine/platform/ps5/os_ps5.cpp").read_text()
detect=(p/"engine/platform/ps5/detect.py").read_text()
scene=(p/"samples/visual-smoke/main.gd").read_text()
native=(p/"native/scene_bridge_main.cpp").read_text()
for token in ("godot_ps5_set_scene_frame_callback","get_current_scene()","get_node_or_null(NodePath(\"PreviewSprite\"))","scene->get(\"count\")","scene_frame_callback(sprite->get_position().x","GODOT_PS5_SCENE_PREVIEW"):
    assert token in os,token
assert "GODOT_PS5_SCENE_PREVIEW" in detect
assert 'sprite.name = "PreviewSprite"' in scene
# The PS5 headless static text server has no FreeType: this caused
# infinite error churn in v0.1.0 _ready, preventing the first GPU swap.
assert "Label.new()" not in scene and "status_label" not in scene
assert "GODOT_PS5_REAL_2D_SCENE_READY" in scene
for token in ("godot_ps5_run_pack(", "godot_ps5_set_scene_frame_callback", "GODOT_GDSCRIPT_SCENE_FRAME_DRAWN","GDSCRIPT_CROSS_COUNT","GL_TRIANGLE_STRIP","glTexImage2D","GL_SRC_ALPHA","TOTAL_PRESENTED","GPU_SHUTDOWN"):
    assert token in native,token
assert "NOT Godot's GLES3" in native
assert "profile_snapshot()" in native
assert "GDSCRIPT_CROSS_COUNT" in native
assert "PAD_MAX_US=" in native and "MAIN_MAX_US=" in native
assert "DRAW_MAX_US=" in native and "SWAP_MAX_US=" in native
assert "profile_snapshot();" in native and "last_presses=presses" in native
assert 'print("GODOT_PS5_REAL_2D_CROSS_PRESSED")' not in scene
assert "main_loop_us, pad_poll_us" in os
hooks=(p/"engine/platform/ps5/scene_frame_hooks_ps5.h").read_text()
assert "GodotPS5SceneFrameCallback" in hooks
assert "uint32_t main_loop_us, uint32_t pad_poll_us" in hooks
assert '"scene_frame_hooks_ps5.h"' in os and '"scene_frame_hooks_ps5.h"' in native
assert "GodotPS5SceneFrameCallback" in os
assert "extern \"C\" void godot_ps5_set_scene_frame_callback(void (*)(float, float, int));" not in native
wf=(p.parent.parent/".github/workflows/build-godot-ps5-scene-bridge.yml").read_text()
assert "scene_frame_hooks_ps5.h" in wf
assert "get_ticks_usec()" in os
assert 'BOOT_FRAME_PRESENTED' in native and 'BOOT_FRAME_GL_ERROR' in native
assert native.index('scene.boot_frame()') < native.index('const int result=godot_ps5_run_pack(')

print("PASS: Same-process real Godot GDScript → PS5 native GL proof wiring")
