# M14: PS5 present pacing A/B experiment (2026-10-23)

## Evidence
M12d physical PS5 logs in `bfpilot-download (31)(1).tar` are for v0.1.6, **not M13**: 38+ intermittent hitches, 133–150ms, including idle, with no M13_FRAME_SPIKE marker. M13 v0.1.7 is signed and in TESTBUILD but has not yet been measured on console. Shader compilation is present but is not a proven universal cause.

## M14 change (experimental)
The DevBridge display opens with `eglSwapInterval(display,1)` (VSync). On the same genuine Godot/PS5 native rendering path, M14 selectively calls `eglSwapInterval(eglGetCurrentDisplay(),0)` after the context opens and before original Godot canvas drawing starts. This changes only *present scheduling*, **not** physics, audio, GDScript, M12d PCK, GPU shaders, timing clock, or the engine. The existing M13 split-frame profiler remains active.

M14 immediate mode is an unverified **hypothesis**. No evidence yet that it fixes stutters. It may tear, render unnecessarily fast, worsen load or fail to affect driver blocking. No artificial CPU sleeps or glFinish are added.

## Safe device A/B
- Experimental M14 v0.1.8 defaults to `immediate` only when `/data/GodotPS5/present_mode.txt` is absent.
- Write `vsync` into `/data/GodotPS5/present_mode.txt` to restore previous frame scheduling **without installing another package**. Alternatively write `immediate`.
- Unknown/invalid settings select the conservative `vsync` path.
- If the EGL immediate request fails, code restores VSync=1 and reports the effective mode.
- `GODOT_PS5_M14_PRESENT_MODE requested=... effective=... egl_error=...` is written once at boot.
- `GODOT_PS5_M13_FRAME_SPIKE` and `GODOT_PS5_M13_FRAME_5S` continue measuring CPU and swap intervals.
- Existing v0.1.7 and v0.1.6 releases are kept for rollback.

## Acceptance
Independent signed native PS5 CI must pass. On console, run the original external `m12d-platformer-asset2201.pck` in both modes, play Level_01 and Level_02, ensure DualSense controls/audio/saves still work, compare matching 60-second samples of `gles3-stdout.log`. Need a reproducible improvement in >=80ms spikes and max egl_swap_ms / frame_ms before calling this a fix. If stalls persist in either mode, follow up with actual M13 CPU/EGL attribution. **No confirmed PS5 FPS fix at this stage.**
