# M25 – Real Godot 4.7.2 Viewport Canvas vs Blit vs GL-End Timing

2026-10-24. Real PS5 firmware 5.10 test: uploaded `bfpilot-download (44).tar`. Native GLES3 PS5 `PPSA99847` v0.2.8 M24.

## Hardware evidence

Directly extracted the latest stdout rather than relying on earlier append-only sessions. M24 logs are present only in the newest hardware session, with `PACK_SOURCE=BUNDLED_VISUAL` and `GODOT_PS5_PONG_READY`, native AudioOut and VSync=1.

- Initial M24 five-second report: **149 frames**, 10 >80ms stutters; `max_viewport_ms=3238.37`, but `max_begin_ms=0.08`, `max_scene_ms=0.24`, `max_prepare_ms=0.00`, `max_end_ms=0.01`, `max_post_ms=0.01` and `max_profile_ms=0.00`. This is a substantial initial improvement compared with M23's six frames but remains unusable.
- Later same run: five-second reports 6,4,3,3,1,1 frames. Severe viewport stage stalls up to ~1033ms per M24 return; M17 Godot draw stage occasionally several seconds, and M13 EGL swap is ~0.1ms once warm. All other M24 stages ~0.0–0.02ms.
- Thus **RenderingServerDefault::_draw -> RSG::viewport->draw_viewports** is the only measured Godot renderer source of major wall-clock stall. But this broad method contains separate **real Canvas2D item drawing, framebuffer-to-screen blit and rasterizer gl_end_frame**, so fast EGL swaps do not prove blit is fast. The root cause remains unverified.

## M25 source and diagnostic scope

M25 v0.2.9 branches strictly from M24, preserving its lean original Godot 4.7.2 GLES3 code. New `patch_ps5_m25_viewport.py` overlays the pinned original `servers/rendering/renderer_viewport.cpp` only on PS5 native GLES3, adding monotonic timing guards to:

1. `_draw_viewport`: time `gl_window_make_current` and each Canvas2D draw pass `RSG::canvas->render_canvas()` via surrounding original `RENDER_TIMESTAMP` macros.
2. `draw_viewports`: time original standard viewport `_draw_viewport(vp)` work, the original OpenGL `blit_render_targets_to_screen`, and `RSG::rasterizer->gl_end_frame(p_swap_buffers)` (which internally may do EGL swap or glFinish depending on passed flag); account for unprofiled setup and other viewport work.
3. Report the difference between entire viewport draw and canvas/context as `draw_other`; everything outside timed draw/blit/present as `other`.

Only bounded `GODOT_PS5_M25_VIEWPORT_READY`, `GODOT_PS5_M25_VIEWPORT_SPIKE` (max 3/win) and `GODOT_PS5_M25_VIEWPORT_5S` (max + mean per-stage) are printed. No explicit GPU fence/readback, shader changes, GL API wrappers, PCK, AudioOut or controller modifications. Existing M24, M17 and M18 profilers remain to cross-check wall clock attribution.

## Next physical hardware pass

Signed `PPSA99847` v0.2.9 contentVersion `01.000.020` after successful trusted PS5 CI and TESTBUILD publication. Test bundled Pong (`launch.txt` temporarily renamed) until lag happens; then export stdout/runtime TAR. Look at coincident **M25 max_canvas_ms, max_draw_other_ms, max_blit_ms, max_gl_end_ms and max_other_ms** vs M24 max_viewport_ms to determine which *actual original operation* is responsible for the stalls. If `blit` is slow, move to PS5 framebuffer blit/AGC path; if `canvas` is slow, isolate Canvas2D drawing/command processing; if `other` is slow, source-level inspect viewport traversal and XR/render-target setup. The experiment is **not a confirmed lag fix**; earlier v0.2.8 is signed rollback and may temporarily perform better because M25 adds trace points.
