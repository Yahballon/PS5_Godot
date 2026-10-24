#!/usr/bin/env python3
"""Regression checks for M17 upstream in-frame phase instrumentation."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]
patch=(p/"scripts/patch_ps5_m17_iteration.py").read_text()
build=(p/"scripts/build-engine.sh").read_text()
native=(p/"native/gles3_canvas_main.cpp").read_text()
for marker in (
 "GODOT_PS5_M17_PHASE_PROFILER_READY",
 "GODOT_PS5_M17_PHASE_SPIKE",
 "GODOT_PS5_M17_PHASE_5S",
 "m17_after_physics", "m17_before_sync", "m17_after_sync",
 "m17_after_draw", "m17_before_delay", "m17_after_delay",
 "RenderingServer::get_singleton()->sync()",
 "OS::get_singleton()->add_frame_delay",
 "Godot 4.7.2 M17 source anchor",
):
    assert marker in patch, marker
assert "#if defined(PS5_ENABLED) && defined(GODOT_PS5_NATIVE_GLES3)" in patch
assert "GODOT_PS5_M17_PHASE_PROFILE" in build
assert "patch_ps5_m17_iteration.py" in build
assert "GODOT_PS5_NATIVE_GLES3" in build
assert "PS5PresentMode perf_present_mode = PS5PresentMode::VSync;" in native
assert "GODOT_PS5_M13_FRAME_5S" in native
assert "glFinish(" not in patch and "glReadPixels(" not in patch
print("GODOT_PS5_M17_PHASE_PROFILER_SOURCE_GUARDS_PASS")
