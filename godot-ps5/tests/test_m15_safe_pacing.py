#!/usr/bin/env python3
"""Regression guards for the M15 safe VSync / low-overhead PS5 profiler."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]
native=(r/"native/gles3_canvas_main.cpp").read_text()
os=(r/"engine/platform/ps5/os_ps5.cpp").read_text()
io=(r/"engine/platform/ps5/file_access_ps5.cpp").read_text()
assert "PS5PresentMode perf_present_mode = PS5PresentMode::VSync;" in native
assert "file=absent mode=vsync (safe_default)" in native
assert 'mode=="immediate"' in native
assert "eglSwapInterval(d,0)" in native and "eglSwapInterval(d,1)" in native
assert "GODOT_PS5_M13_FRAME_SPIKE" in native
assert "GODOT_PS5_M13_FRAME_5S" in native
for marker in ("GODOT_PS5_M15_ITER_PROFILER_READY","GODOT_PS5_M15_ITER_SPIKE","GODOT_PS5_M15_ITER_5S",
               "diag_after_pad_us","diag_before_main_us","diag_main_us","diag_idle_us"):
    assert marker in os, marker
assert "#ifdef GODOT_PS5_NATIVE_GLES3" in os
assert "Main::iteration();" in os
assert "static std::atomic<unsigned> successful_open_logs" in io
assert "successful_open_logs.fetch_add(1, std::memory_order_relaxed) < 8" in io
assert 'OPEN_FAILED' in io
assert 'native_fd = open_native(native_path);' in io
assert "glFinish(" not in native and "glReadPixels(" not in native
print("GODOT_PS5_M15_SAFE_PACING_AND_ITER_PROFILER_HOST_PASS")
