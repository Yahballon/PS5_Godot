#!/usr/bin/env python3
"""M26: isolate costly PS5 /data stdout/stderr writes without rendering changes."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
native=(root/"native/gles3_canvas_main.cpp").read_text()
engine=(root/"engine/platform/ps5/display_server_ps5.cpp").read_text()
for token in ("GODOT_PS5_M26_IO_MODE mode=%s",
              "m26_log_mode.txt", "m26_unbuffered",
              "_IOFBF", "_IONBF", "m26_stdout_buffer[128*1024]",
              "m26_stderr_buffer[128*1024]",
              'value=="unbuffered"', 'record("M26_IO_A_B_MODE"',
              "setvbuf(stdout,m26_stdout_buffer,_IOFBF",
              "setvbuf(stderr,m26_stderr_buffer,_IOFBF",
              'record("BOOT");',
              "GODOT_PS5_M25_VIEWPORT"):
    if token=="GODOT_PS5_M25_VIEWPORT":
        continue
    assert token in native, token
assert 'ps5_graphics.swap()' in engine
assert 'PS5PresentMode perf_present_mode = PS5PresentMode::VSync;' in native
assert "GODOT_PS5_M13_FRAME_5S" in native
assert "GODOT_PS5_M19_GL_SUMMARY_5S" not in native
assert "GODOT_PS5_M23_GL_SUMMARY_5S" not in native
assert "GODOT_PS5_M24_RENDER_STAGES" in (root/"scripts/build-engine.sh").read_text()
assert "GODOT_PS5_M25_VIEWPORT_STAGES" in (root/"scripts/build-engine.sh").read_text()
# Keep original render engine and actual API call order untouched.
assert 'void* gl_resolve(const char *name)' in native
assert 'display.swap()' in native
print("GODOT_PS5_M26_BUFFERED_OUTPUT_AB_SOURCE_PASS")
