#!/usr/bin/env python3
"""M13 native 48/60Hz hitch attribution: CPU-before-swap vs EGL/GPU swap.
Hardware logging is bounded to avoid turning measurement into a slowdown.
"""
from pathlib import Path
src=Path(__file__).resolve().parents[1]/"native/gles3_canvas_main.cpp"
s=src.read_text()
need=["clock_gettime(CLOCK_MONOTONIC", "GODOT_PS5_M13_NATIVE_FRAME_PROFILER_READY",
      "GODOT_PS5_M13_FRAME_SPIKE", "GODOT_PS5_M13_FRAME_5S",
      "cpu_before_swap_ms=", "egl_swap_ms=", "max_cpu_ms=", "max_swap_ms=",
      "spikes_80ms=", "perf_window_logged<8", "if(end-perf_epoch_ms>=5000.0)",
      "const double before=ps5_now_ms()", "const double after=ps5_now_ms()",
      "display.swap()", "perf_report(cpu_before_swap,swap_ms,before,after)"]
for x in need:assert x in s,x
assert s.index('const double before=ps5_now_ms()')<s.index('if(!display.swap()){',s.index('bool present()'))
assert s.index('const double after=ps5_now_ms()')>s.index('if(!display.swap()){',s.index('bool present()'))
assert 'glFinish(' not in s and 'glReadPixels(' not in s
assert 'perf_report' in s and 'perf_last_swap_complete_ms=after;' in s
assert "GODOT_PS5_M13_FRAME_SPIKE" in s
assert "if(frames==1)" in s
assert 'fopen(logpath' in s  # old runtime log remains, untouched
print("GODOT_PS5_M13_BOUNDED_NATIVE_PERF_TEST_PASS")
