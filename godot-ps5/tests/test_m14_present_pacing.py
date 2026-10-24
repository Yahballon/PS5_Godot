#!/usr/bin/env python3
"""M14 must preserve known-good swap path and support bounded, reversible A/B comparison."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=(root/"native/gles3_canvas_main.cpp").read_text()
requirements=[
 "GODOT_PS5_M14_PRESENT_MODE", "GODOT_PS5_M14_CONFIG",
 "/data/GodotPS5/present_mode.txt",
 "sceKernelOpen(conf,O_RDONLY | O_NOFOLLOW,0)",
 "eglGetCurrentDisplay()", "eglSwapInterval(d,0)",
 "eglSwapInterval(d,1)", "perf_present_mode=PS5PresentMode::VSync",
 "apply_present_mode();", "load_present_mode();",
 "GODOT_PS5_M13_NATIVE_FRAME_PROFILER_READY",
 "GODOT_PS5_M13_FRAME_SPIKE",
 "GODOT_PS5_M13_FRAME_5S",
]
for token in requirements:
    assert token in s, token
assert s.index("load_present_mode();") < s.index("godot_ps5_run_pack(pack.c_str())")
assert s.index("apply_present_mode();") < s.index('record("BOOT_FRAME_PRESENTED")')
assert "glFinish(" not in s and "glReadPixels(" not in s
assert 'constexpr const char *logpath="/data/GodotPS5/gles3-runtime.log";' in s
print("GODOT_PS5_M14_HOST_PRESENT_MODE_TEST_PASS")
