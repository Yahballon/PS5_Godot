# M16 – Native PS5 Sleep Timing / CPU Frame Pacing Candidate

Date: 2026-10-24. Based on real firmware-5.10 user logs `bfpilot-download (34).tar`, M15 v0.1.9.

## Hardware evidence (newest M15 session only)

- `GODOT_PS5_M14_PRESENT_MODE requested=vsync effective=vsync` confirmed.
- `GODOT_PS5_M15_ITER_PROFILER_READY mode=main_thread_v1` confirms new instrumentation.
- 34 individually logged `M15_ITER_SPIKE` events; `Main::iteration()` peaks about 1923ms and outside-loop about 948ms. 10 five-second M15 windows; some have just 2–3 frames.
- `M13_FRAME_SPIKE` counts 57 in this session; almost all EGL swap intervals <1ms, with a rare ~655ms swap. Overall long stalls overwhelmingly occur **before** the swap call.
- `Level_01` and `Level_02` load with original M12d collision-safe PCK; startup scene marker Level_01 3434ms, Level_02 24549ms.
- The PS5 game is still severely laggy even with VSync restored. A pure `eglSwapInterval(0)` toggle is not a proven solution and significantly worsened previous M14 run.

## Code experiment

Godot's PS5 `OS_PS5` inherits Unix `OS_Unix::delay_usec`, which uses FreeBSD libc `nanosleep`. This M16 candidate overrides `delay_usec` **only for the experimental native GLES3 build** with public `sceKernelUsleep(uint32_t)`; if native sleep reports an error, falls back to inherited Unix sleep. No busy spin or artificial frame cap. Other PS5 test titles and the existing Godot 4.7.2 engine logic are unaffected.

`GODOT_PS5_M16_SLEEP_5S calls=N requested_ms=N actual_ms=N max_sleep_ms=N fallbacks=N` summarizes the actual sleep behavior every five seconds. M13 swap and M15 MainLoop time probes stay in place. Native default VSync remains 1.

## Evidence gate

The implementation is a **hypothesis, NOT a confirmed hardware fix**. Require signed v0.2.0 PS5 CI, in-game audio, control & collision retesting, `v0.1.9` regression comparison, and logs documenting whether requested-vs-actual sleeps track any 80ms+ stutters. Preserve older signed releases and original PCK; no change to `launch.txt`.

## Test

Keep `/data/GodotPS5/present_mode.txt` set to `vsync` or remove it (v0.2.0 default). Leave `launch.txt` pointed at `m12d-platformer-asset2201.pck`. Run Level_01 and Level_02; capture `gles3-stdout.log`, `gles3-stderr.log`, `gles3-runtime.log`. Check `M16_SLEEP_5S`, `M15_ITER_5S`, and `M13_FRAME_5S`. Roll back to [v0.1.9](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gles3-canvas-v0.1.9) if degraded.
