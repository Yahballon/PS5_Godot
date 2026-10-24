# M18 – CPU execution vs wall time and native AudioOut A/B

Date: 2026-10-24. Hardware firmware 5.10, uploaded `bfpilot-download (36).tar`.

## What the previous hardware data actually proves

Original platformer remains unplayably laggy on experimental M17 v0.2.1. Latest M17 session contains **28 recorded phase spikes**. Sample `GODOT_PS5_M17_PHASE_SPIKE` maximum: physics 166.41ms (usually ~4ms), scene/process 981.81ms, renderer sync ~0ms, renderer draw 1912.47ms. Frame total reaches 2862.91ms; the median among these spikes is scene ~316.61ms and draw ~140.77ms. No M16 sleep requests in 11 recent 5-second intervals. Native EGL buffer swap itself is usually ~0.1ms. Frame performance can decay to 1 FPS during the session even while the audio worker is still advancing.

The measurements confirm at least two regions suffering large **wall-clock time**, but cannot tell whether Godot is burning CPU, waiting on a thread/mutex, waiting for GPU or being descheduled by the PS5 scheduler. Therefore do not claim the graphics driver or audio is definitely at fault; not enough evidence.

## M18 experimental instrumentation, no baseline gameplay changes

- On the main thread, measure wall clock (existing M15) and per-thread CPU clock `CLOCK_THREAD_CPUTIME_ID` around the **same** `Main::iteration()` call. This is optional if the PS5 libc exposes the clock; report unavailability explicitly rather than inventing zero-CPU readings.
- `GODOT_PS5_M18_MAIN_CPU_SPIKE wall_ms=... cpu_ms=... noncpu_ms=...` up to four per five seconds; `GODOT_PS5_M18_MAIN_CPU_5S` summarizes; noncpu time includes **all waits and descheduling**, not just scheduler activity.
- A/B control `/data/GodotPS5/m18_audio_mode.txt`. Absent or any content except the exact word `dummy` means original native AudioOut and normal sound. To explicitly test without the hardware audio worker, create the file with `dummy`, restart, compare frame counts/hitch severity, and remove the file afterward to restore audio. Log `GODOT_PS5_M18_AUDIO_AB_MODE mode=native_audioout|dummy`.
- Keep original working `/data/GodotPS5/launch.txt` pointing to `m12d-platformer-asset2201.pck`; VSync defaults to on. M13, M15, M16, M17 profilers retained.
- No arbitrary sleeps, GPU fences, new shaders or physics changes.

## Validation gates

Experimental signed v0.2.2 `PPSA99847` content version `01.000.013` compiles via its own native PS5 workflow, then release+TESTBUILD catalog must be updated only from a verified successful trusted push artifact. Host and native CI success do **not** mean FPS fixed. Need equal-duration physical PS5 tests with native audio vs dummy, plus valid M18 CPU clock readings, to choose an actual remediation. Preserve rollback signed v0.2.1.
