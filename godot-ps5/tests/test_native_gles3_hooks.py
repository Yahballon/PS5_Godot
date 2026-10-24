#!/usr/bin/env python3
"""Native opt-in GLES3 test must use the original Godot canvas pipeline."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
ps5=root/"engine/platform/ps5"
header=(ps5/"graphics_hooks_ps5.h").read_text()
impl=(ps5/"display_server_ps5.cpp").read_text()
entry=(ps5/"godot_ps5.cpp").read_text()
for token in ("bool (*open)(int width, int height)", "bool (*swap)()",
              "void (*close)()", "void *(*get_gl_proc)(const char *name)"):
    assert token in header,token
for token in ("RasterizerGLES3::make_current(true)",
              "glad_eglGetProcAddress",
              "DISPLAY_SERVER_PS5_EGL_READY",
              "DisplayServerPS5::swap_buffers()",
              "DisplayServerPS5::~DisplayServerPS5()",
              "godot_ps5_set_graphics_hooks"):
    assert token in impl,token
assert 'constexpr int count = 8;' in entry
assert '"gl_compatibility"' in entry
assert 'GODOT_PS5_NATIVE_GLES3' in (ps5/"detect.py").read_text()
print("PASS: opt-in real Godot GLES3 DisplayServer callback surface defined")
