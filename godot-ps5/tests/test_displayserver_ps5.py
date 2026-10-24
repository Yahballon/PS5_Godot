#!/usr/bin/env python3
"""Host guardrails for real Godot-PS5 DisplayServer ABI bringup."""
from pathlib import Path
p = Path(__file__).resolve().parents[1]
overlay = p / "engine/platform/ps5"
header = (overlay / "display_server_ps5.h").read_text()
impl = (overlay / "display_server_ps5.cpp").read_text()
os_src = (overlay / "os_ps5.cpp").read_text()
scons = (overlay / "SCsub").read_text()
detect = (overlay / "detect.py").read_text()
for symbol in ("public DisplayServerHeadless", "get_screen_count() const override",
               "get_screen_size(", "window_can_draw(", "get_rendering_drivers_func",
               "register_ps5_driver"):
    if symbol == "get_screen_size(":
        assert "screen_get_size(" in header
    else:
        assert symbol in header, symbol
assert '"ps5", create_func' in impl
assert 'RasterizerDummy::make_current()' in impl
assert 'RasterizerGLES3::make_current(true)' in impl
assert 'DISPLAY_SERVER_PS5_EGL_READY' in impl
assert 'glad_eglGetProcAddress' in impl
assert 'GODOT_PS5_NATIVE_GLES3' in impl
assert 'GODOT_PS5_NATIVE_GLES3' in detect
assert '"--rendering-driver"' in (p/"engine/platform/ps5/godot_ps5.cpp").read_text()
assert '"--headless"' in (p/"engine/platform/ps5/godot_ps5.cpp").read_text()
assert "p_rendering_driver != \"dummy\"" in impl
assert 'graphics_hooks_ps5.h' in header
assert 'ERR_UNAVAILABLE' in impl
assert 'p_rendering_driver != "dummy"' in impl
assert 'DISPLAY_SERVER_PS5_DUMMY_REGISTERED_NO_VIDEO' in impl
assert 'DisplayServerPS5::register_ps5_driver()' in os_src
assert '#ifdef GODOT_PS5_DISPLAY_EXPERIMENT' in os_src
assert 'GODOT_PS5_DISPLAY_EXPERIMENT' in detect
assert 'GODOT_PS5_DISPLAY_EXPERIMENT' in scons
# The normal PS5 build remains headless without the explicit opt-in.
assert 'os.environ.get("GODOT_PS5_GLES3_ARCHIVES") == "1"' in detect
assert "GODOT_PS5_GLES3_ARCHIVES" in scons
assert 'return false;' in header
assert 'EGL' not in (overlay / "os_ps5.h").read_text()
print("PASS: isolated DisplayServerPS5 ABI target does not claim OpenGL.")
