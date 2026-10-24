#!/usr/bin/env python3
"""M25 pinned upstream Viewport trace checks; no new GL work or gameplay changes."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
script=(root/"scripts/patch_ps5_m25_viewport.py").read_text()
build=(root/"scripts/build-engine.sh").read_text()
native=(root/"native/gles3_canvas_main.cpp").read_text()
for token in ("GODOT_PS5_M25_VIEWPORT_5S","GODOT_PS5_M25_VIEWPORT_READY",
              "GODOT_PS5_M25_VIEWPORT_SPIKE",
              "m25_canvas_us", "m25_draw_us", "m25_blit_us",
              "m25_present_us", "m25_context_us",
              "gl_window_make_current", 'RENDER_TIMESTAMP("> Render Canvas " + itos(canvas_idx));',
              "blit_render_targets_to_screen(", "gl_end_frame(",
              "m25_draw_other", "m25_other", "m25_report_epoch",
              "OS::get_singleton()->get_ticks_usec()",
              "source drift"):
    assert token in script,token
assert "GODOT_PS5_M25_VIEWPORT_STAGES" in build
assert "patch_ps5_m25_viewport.py" in build
assert "GODOT_PS5_M24_RENDER_STAGES" in build
assert "GODOT_PS5_M19_GL_SUMMARY_5S" not in native
assert "GODOT_PS5_M23_GL_5S" not in native
assert "PS5PresentMode perf_present_mode = PS5PresentMode::VSync;" in native
assert "GODOT_PS5_M13_FRAME_5S" in native
assert "GODOT_PS5_M17_PHASE_5S" in (root/"scripts/patch_ps5_m17_iteration.py").read_text()
print("GODOT_PS5_M25_GLES3_VIEWPORT_STAGE_GUARDS_PASS")
