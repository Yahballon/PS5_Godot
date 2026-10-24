#!/usr/bin/env python3
from pathlib import Path
root=Path(__file__).resolve().parents[1]
native=(root/"native/gles3_canvas_main.cpp").read_text()
workflow=(root.parent.parent/".github/workflows/build-godot-ps5-gles3-canvas.yml").read_text()
for token in ("godot_ps5_set_graphics_hooks(&hooks)", "godot_ps5_run_pack(",
              "BOOT_FRAME_PRESENTED","GODOT_SWAP_FIRST","gles3-stderr.log","gl_resolve"):
    assert token in native,token
for token in ("GODOT_PS5_NATIVE_GLES3: '1'","GODOT_PS5_GLES3_ARCHIVES: '1'",
              "GODOT_PS5_DISPLAY_EXPERIMENT: '1'","PPSA99847",
              "visual-smoke.pck","graphics_hooks_ps5.h","stage_native_link.py"):
    assert token in workflow,token

assert "glDrawArrays(" not in native
assert "glTexImage2D(" not in native
assert "gh release create" not in workflow
for symbol in ('#include "pck_launch_config.hpp"', 'read_launch_txt()',
               'trusted_external_path(requested)', 'valid_godot4_pack(requested)',
               'PACK_SOURCE=%s PACK=%s', 'BUNDLED_VISUAL', 'visual-smoke.pck'):
    assert symbol in native, symbol
assert 'first_pack_in(' not in native, "Do not auto-load stale external content"
assert "Godot-PS5-REAL-GLES3-Canvas-v0.1.2-" in workflow
assert "contentVersion='01.000.003'" in workflow
for marker in ("GodotPS5-GLES3-Pong-Godot4-PCK-NOT-PS5",
               "GODOT_PS5_PONG_READY", "pong.pck"):
    assert marker in workflow, marker
pong=(root/"samples/pong-smoke/main.gd").read_text()
for marker in ("extends Node2D", "func _draw()", "draw_rect(",
               "draw_circle(", "draw_line(", "queue_redraw()",
               "JOY_AXIS_LEFT_Y", "JOY_BUTTON_DPAD_UP",
               "JOY_BUTTON_DPAD_DOWN", "JOY_BUTTON_A",
               "JOY_BUTTON_B", "JOY_BUTTON_START",
               "GODOT_PS5_PONG_READY", "GODOT_PS5_PONG_SERVE"):
    assert marker in pong, marker
assert "Label.new()" not in pong
assert "PhysicsServer2D." not in pong and "PhysicsBody2D.new(" not in pong
assert "glDrawArrays(" not in pong and "glTexImage2D(" not in pong
print("PASS: true Godot GLES3 Canvas2D PS5 title source/build isolated")
