#!/usr/bin/env python3
"""M18 native PS5 engine CPU-vs-wall and optional audio A/B source gates."""
from pathlib import Path
base=Path(__file__).resolve().parents[1]
os=(base/"engine/platform/ps5/os_ps5.cpp").read_text()
launch=(base/"engine/platform/ps5/godot_ps5.cpp").read_text()
native=(base/"native/gles3_canvas_main.cpp").read_text()
for marker in ("CLOCK_THREAD_CPUTIME_ID","clock_gettime(CLOCK_THREAD_CPUTIME_ID",
               "GODOT_PS5_M18_MAIN_CPU_SPIKE","GODOT_PS5_M18_MAIN_CPU_5S",
               "GODOT_PS5_M18_CPU_CLOCK_UNAVAILABLE",
               "m18_cpu_sum_us","m18_wall_sum_us"):
    assert marker in os, marker
for marker in ("m18_audio_mode.txt","m18_dummy_audio_requested()",
               "--audio-driver","Dummy","GODOT_PS5_M18_AUDIO_AB_MODE",
               'dummy_audio?"dummy":"native_audioout"'):
    assert marker in launch, marker
assert "if(dummy_audio)" in launch
assert "constexpr int count = 8;" in launch
assert "int m18_count=count;" in launch
assert 'Main::setup("godot.ps5", m18_count, args)' in launch
assert "GODOT_PS5_M17_PHASE_5S" in (base/"scripts/patch_ps5_m17_iteration.py").read_text()
assert "PS5PresentMode perf_present_mode = PS5PresentMode::VSync;" in native
assert "GODOT_PS5_M13_FRAME_5S" in native
assert "GODOT_PS5_M15_ITER_5S" in os
assert "GODOT_PS5_M16_SLEEP_5S" in os
print("GODOT_PS5_M18_CPU_CLOCK_AUDIO_AB_SOURCE_OK")
