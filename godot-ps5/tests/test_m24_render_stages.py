#!/usr/bin/env python3
"""M24: guard low-overhead renderer phase measurements and rollback of GL API interception."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=(root/"scripts/patch_ps5_m24_render_stages.py").read_text()
build=(root/"scripts/build-engine.sh").read_text()
native=(root/"native/gles3_canvas_main.cpp").read_text()
for marker in ("GODOT_PS5_M24_RENDER_READY", "GODOT_PS5_M24_RENDER_SPIKE",
               "GODOT_PS5_M24_RENDER_5S", "max_viewport_ms",
               "RSG::viewport->draw_viewports(p_swap_buffers);",
               "RSG::rasterizer->begin_frame(frame_step);",
               "RSG::rasterizer->end_frame(p_swap_buffers);",
               "RSG::utilities->update_memory_info();",
               "GODOT_PS5_NATIVE_GLES3", "m24_sums[7]",
               "Godot 4.7.2 M24 rendering source drift"):
    assert marker in p, marker
assert "GODOT_PS5_M24_RENDER_STAGES" in build
assert "patch_ps5_m24_render_stages.py" in build
assert "GODOT_PS5_M13_FRAME_5S" in native
assert "GODOT_PS5_M19_GL_SUMMARY_5S" not in native
assert "GODOT_PS5_M23_GL_SUMMARY_5S" not in native
assert "GODOT_PS5_M22_BOUNDED_CANVAS_RING" not in native
assert "PS5PresentMode perf_present_mode = PS5PresentMode::VSync;" in native
assert 'GODOT_PS5_M18_AUDIO_AB_MODE mode=%s' in (root/"engine/platform/ps5/godot_ps5.cpp").read_text()
print("GODOT_PS5_M24_LOW_OVERHEAD_RENDER_STAGES_PASS")
