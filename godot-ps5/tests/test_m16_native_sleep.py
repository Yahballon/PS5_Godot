#!/usr/bin/env python3
"""M16 PS5-native sleep shim and diagnostic gating regression test."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
h=(root/"engine/platform/ps5/os_ps5.h").read_text()
cpp=(root/"engine/platform/ps5/os_ps5.cpp").read_text()
launcher=(root/"native/gles3_canvas_main.cpp").read_text()
assert "#ifdef GODOT_PS5_NATIVE_GLES3" in h
assert "void delay_usec(uint32_t p_usec) const override;" in h
assert "void OS_PS5::delay_usec(uint32_t p_usec) const" in cpp
assert "sceKernelUsleep(p_usec)" in cpp
assert "OS_Unix::delay_usec(p_usec);" in cpp
assert "GODOT_PS5_M16_SLEEP_5S" in cpp
assert "ps5_sleep_fallbacks.exchange(0" in cpp
assert "std::atomic<uint64_t> ps5_sleep_calls" in cpp
assert "PS5PresentMode perf_present_mode = PS5PresentMode::VSync;" in launcher
assert "GODOT_PS5_M13_FRAME_SPIKE" in launcher
assert "GODOT_PS5_M15_ITER_SPIKE" in cpp
print("GODOT_PS5_M16_NATIVE_SLEEP_AND_ROLLBACK_GUARDS_PASS")
