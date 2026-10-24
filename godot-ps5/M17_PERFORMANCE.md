# M17 – Native Godot 4.7.2 in-frame phase profiler

Date: 2026-10-24. Reference console firmware 5.10, test archive `bfpilot-download (35).tar` (M16 v0.2.0).

## Actual hardware observations

Latest M16 session: 9 `GODOT_PS5_M16_SLEEP_5S` summaries, **all calls=0**. Native kernel sleep is not called during observed stalls: the M16 hypothesis is unsupported. The `M15_ITER_5S` windows slow to 2 frames in five seconds, with `Main::iteration` up to 1922.9ms and outside-loop ~1016ms. `M13_FRAME_5S` shows almost entirely `egl_swap_ms` ~0.09–0.1ms during the worst windows, with pre-swap frame stalls in the multiple-second range. The original M12d game shows Level_01 and Level_02 loaded and M12d hitches. The effective present setting is VSync after M15 regression rollback. Disabling VSync in M14 caused a severe regression and must not be a default.

There are no significant shader compilation messages in the late, persistently stalling gameplay windows, so attributing all late hitches to shader compilation is unjustified.

## Exact next diagnostic

A guarded overlay `scripts/patch_ps5_m17_iteration.py` instruments the actual upstream `main/main.cpp` from pinned Godot 4.7.2 **only for the isolated experimental PS5 GLES3 engine build**, not the headless titles. It measures:
- `physics_ms`: frame prep, physics loops and PhysicsServer2D handling.
- `scene_ms`: input dispatch, GDScript/SceneTree process, navigation and message queue work before renderer sync.
- `sync_ms`: RenderingServer::sync.
- `draw_ms`: RenderingServer::draw and present via original GLES3 backend.
- `tail_ms`: GDExtension/ScriptServer/AudioServer/FPS update and other trailing frame tasks.
- `delay_ms`: OS::add_frame_delay.

Three markers: `GODOT_PS5_M17_PHASE_PROFILER_READY`, `GODOT_PS5_M17_PHASE_SPIKE` (maximum four per five seconds), `GODOT_PS5_M17_PHASE_5S` (max and average phase timings). This does not change animation, physics step counts, collision, game assets, controller input, AudioOut, VSync or GPU synchronization. M13 and M15 native timing remain in parallel. It reports what subsystem is blocking, so the *subsequent* fix can be narrow and validated.

## Safety and acceptance

Patch fails closed on unexpected Godot 4.7.2 source anchors. Host test downloads original `main.cpp`, checks patch, then checks patch idempotency. Native signed title `PPSA99847` v0.2.1 content version `01.000.012`; publisher only accepts a trusted successful push artifact. Keep v0.2.0 and v0.1.9 as fallbacks. **Not a hardware-confirmed FPS fix.**

On console keep `/data/GodotPS5/launch.txt` selecting original `m12d-platformer-asset2201.pck`; `/data/GodotPS5/present_mode.txt` absent or set `vsync`. Play Level_01 and Level_02 through multiple stutters and export stdout/stderr/runtime logs. Correlate `M17_PHASE_SPIKE` with `M15_ITER_SPIKE` and `M13_FRAME_SPIKE` to identify phase(s), then focus remediation.
