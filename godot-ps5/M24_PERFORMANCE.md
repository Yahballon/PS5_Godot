# M24 – Isolate original Godot RenderingServer stages without GL API wrappers

Date: 2026-10-24. User firmware 5.10 TAR: `bfpilot-download (43).tar`.

## Confirmed hardware regression

Latest append-only log contains **two actual M23 v0.2.7 sessions** (`GODOT_PS5_M23_EXTRA_GL_TIMING active=1`, `GODOT_PS5_PONG_READY`, VSync on and native AudioOut). Both exhibit nearly identical stalls: first M13 five-second report 6 frames; M17 `max_draw_ms` 3676–3680ms in first window, then ~7648–7653ms. M18 reports wall 8578–8582ms on the worst subsequent frames versus ~39ms actual thread CPU; the majority is waiting/descheduling, not GDScript CPU. EGL buffer swaps remain ~0.1ms. The previously timed M19 23 GL calls total only 3.61ms and 3.80ms in late frames; 32 additional M23 GL calls total just 0.18ms and 0.20ms. Therefore **neither set of timed individual GL calls explains the 7.65-second stall**, and no specific individual GL function has been proved culpable. The user perceives v0.2.7 as WORSE. We must avoid another 50+ wrapper stack or repeat the disproven M20/M21/M22 hypotheses.

This file is a checkpoint only. Underlying root cause remains unverified: render-server viewport traversal, rasterizer frame boundary, GL driver and GPU queue waiting or cross-thread synchronization remain possible.

## M24 experimental low-overhead isolation

Start from the original signed v0.2.2 M18 **source branch**, not the progressively instrumented M23. This removes M19's 23 GL API wrappers, M23's 32 additional wrappers, M20's speculative timestamp-query patch, M21's modified GL fence-status polling, and M22's untriggered GL buffer ring. Standard Godot 4.7.2 GLES3 GPU command and buffer lifetime order remains intact. Native PS5 AudioOut, Godot Project/PCK loader, Physics2D, original GDScript and dualsense, VSync=1, M13 native swap timing, M15 main loop phases, M17 Main::iteration phases, and M18 CPU-vs-wall timing all remain.

An opt-in upstream Godot 4.7.2 `servers/rendering/rendering_server_default.cpp` patch adds eight monotonic clock samples inside `RenderingServerDefault::_draw` and reports seven section durations:

- begin: `RSG::rasterizer->begin_frame`
- scene: `scene->update` and `canvas->update`
- prepare: particles and probe work before viewport
- viewport: `RSG::viewport->draw_viewports` (contains scene/canvas draws)
- end: canvas updates and rasterizer end_frame
- post: visibility notifications and post-draw steps
- profile: frame profiling and memory info

Signals: `GODOT_PS5_M24_RENDER_READY`, `GODOT_PS5_M24_RENDER_SPIKE stage=X elapsed_ms=N` (max 3 per 5s), `GODOT_PS5_M24_RENDER_5S` (max and mean per-stage every 5s). This does **not** add GL commands, GPU fences, CPU sleeps, shader mutations, or 55 API-level clock calls per ordinary frame. Strict upstream source anchors and patch idempotency are exercised in host CI.

## Next hardware acceptance

Signed `PPSA99847` version `0.2.8`, contentVersion `01.000.019`, release only from successful trusted original branch push and verified binary. Keep v0.2.7/0.2.2 rollback assets, although neither is playable enough.

With `/data/GodotPS5/present_mode.txt` absent/`vsync`, native AudioOut default, and `launch.txt` temporarily renamed, run **bundled Pong until first severe hitch** and export fresh gles3 stdout. Inspect `max_viewport_ms` versus `max_begin_ms`, `max_scene_ms`, `max_end_ms`, `max_post_ms` and `max_profile_ms`. If the stall is isolated inside viewport draw, the next source-level fix/instrumentation must target its internal subfunctions or the AGC queue; if the stall is before viewport, stop assuming a GL draw command. This is a diagnostic build, not a hardware-confirmed FPS fix.
