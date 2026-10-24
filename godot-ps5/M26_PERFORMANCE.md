# M26 – Are synchronous PS5 /data stdout/stderr writes causing increasing renderer stalls?

Date: 2026-10-24. Actual user firmware 5.10 TAR: `bfpilot-download (45).tar`.

## Two hardware v0.2.9 M25 sessions

In the uploaded archive `gles3-stdout.log` has two `GODOT_PS5_M25_VIEWPORT_READY` markers and twelve M25 five-second windows. Both actual user tests boot bundled Godot Pong at 1920×1080 using PS5 AGC Mesa 26.2.0, native AudioOut, VSync default and Godot GLES3 renderer.

Test 1: first M25 report 121 frames, late reports 5,3 frames (then next session boot). Test 2: first M25 report 124 frames, later 5,3,2,2,1,1,1 frames, progressively unplayable. These tests strongly reproduce the issue.

Critical timings from late test 2:
- `GODOT_PS5_M25_VIEWPORT_SPIKE wall_ms=8660.38 canvas_ms=1.85 draw_other_ms=0.01 context_ms=0.00 blit_ms=0.06 gl_end_ms=8658.45 other_ms=0.01`
- Native M13 `egl_swap_ms` remains about 0.1ms; this is timed *inside* the swap hook's `display.swap()`.
- Godot M24 `max_viewport_ms` for analogous late windows grows to **24,884.22ms**, whereas its nested M25 window's `max_wall_ms` is **8,660.38ms**. The discrepancy means time accumulated **after M25 took its end-of-viewport timestamp but before the caller returned**, consistent with output/log activity (not proof of its cause).
- Actual Canvas2D render ~1.8ms, separate GLES3 render-target blit ~0.06ms, frame-end operation takes seconds. `RasterizerGLES3::gl_end_frame(p_swap_buffers)` calls the PS5 DisplayServer swap hook when rendering is enabled. The native `present()` callback calls `display.swap()` and then logs M13 diagnostic data with `std::printf` **after** the internal EGL duration is measured. Therefore fast EGL swap does not exclude slow logging after swap inside `gl_end_frame`.
- The native launcher in v0.2.9 uses `freopen("/data/GodotPS5/gles3-stdout.log","ab",stdout)` and `setvbuf(stdout,nullptr,_IONBF,0)`, and analogously unbuffered stderr. Thus any Godot/M13–M25 `printf` can perform immediate filesystem writes on render thread. Such writes may be blocked by storage I/O and plausibly explain time spent sleeping/descheduled rather than in GL API or CPU computation. **No I/O write trace has proved this root cause yet**.

## Controlled M26 change

Source branch `perf/godot-ps5-m26-buffered-io-ab` starts exactly from M25 and changes only native PS5 launcher C stdio buffering after `freopen`:
- By default stdout and stderr use two independent **128 KiB static, full buffers** via `setvbuf(...,_IOFBF,...)` to avoid synchronous line-by-line writes from swap callbacks and rendering diagnostics. Lifetime is static until app termination.
- For direct A/B, create `/data/GodotPS5/m26_log_mode.txt` with exact `unbuffered` (optional newline) and reboot: restores previous `_IONBF` for both streams. Delete file and reboot to restore buffered mode.
- `gles3-runtime.log`, written through a separate short-lived FILE handle, immediately includes `M26_IO_A_B_MODE=1` for buffered or `=0` for unbuffered, even if stdout remains in memory; stdout itself adds `GODOT_PS5_M26_IO_MODE` when flushed. Original M13/M17/M18/M24/M25 log text and real GLES3 draw calls are unchanged.
- Buffered logs may be lost if the title is forcibly killed before flushing; absence of M25 lines is not evidence it never ran. Test *gameplay responsiveness* first.
- No VSync off/on tweak, extra GL commands, new shader, RAM-backed PCK, physics, audio, or buffer-ring changes.

## Physical acceptance gate

Version `0.2.10` / `PPSA99847` / `contentVersion=01.000.021`, signed native PS5 CI followed by trusted verified TESTBUILD publisher only.

1. Ensure `m26_log_mode.txt` does not exist, and existing `present_mode.txt` absent or `vsync`. Native audio as normal, bundled Pong active (temporarily rename `launch.txt`).
2. Run same scene for at least 45–90s or until freezes, observing if FPS remains responsive past 120 frames. It is a **failure** if it degrades to 1 frame / 5 seconds.
3. Only if practical, create `m26_log_mode.txt` containing `unbuffered` and reboot, compare whether stall returns within similar duration. `runtime.log` tells mode.
4. If both modes remain unplayable, consider removing all diagnostic `printf` entirely for production, using an asynchronous logging thread or isolated in-memory ring, and trace actual native PS5 `swap()` outside logging. Avoid declaring `glFinish` culpable absent proof that p_swap_buffers is false; real display is available.

Hardware success and actual root cause **NOT YET VERIFIED**.


## Hardware acceptance: PASS for bundled Pong – user TAR #46 (2026-10-24)

The user reports, unambiguously, that Pong is now playable **without lag**. Direct inspection of `bfpilot-download (46).tar` supports this on real PS5 firmware 5.10:

- `gles3-runtime.log` contains `M26_IO_A_B_MODE=1`, confirming the **default buffered** stdio path. New stdout includes `GODOT_PS5_M26_IO_MODE mode=buffered stdout_buffer=131072 stderr_buffer=131072`; some earlier append-only stdout content shares the same line due to buffer/previous-session flush boundaries, so do **not** attribute the preceding old `max_draw_ms=34580.22` fragment to the new M26 test.
- The **new M26 session only**, starting at its M26 mode marker, has ten complete `GODOT_PS5_M13_FRAME_5S` samples: first 301 frames / one 150.2ms warm-up spike; the **following nine windows all have exactly 300 frames in five seconds and 0 spikes >=80ms**. That is **2,700 consecutive stable frames / 45 seconds**, after initial 301 frames (~50 sec total measured).
- Nine stable windows have `avg_cpu_ms` ~16.56–16.57 and `avg_swap_ms` ~0.12. Max render frame after warm-up is ~17.7–17.8ms. `M25_VIEWPORT_5S` has 300 frames, 0 spikes per window, steady `avg_wall_ms` ~16.5 and `avg_canvas_ms` ~1.7. `M24_RENDER_5S` confirms normal viewport timing, and `M17_PHASE_5S` shows 0 frame spikes.
- Pong heartbeats at frames **600, 1200, 1800, 2400, 3000**, plus `GODOT_PS5_PONG_HIT` and `GODOT_PS5_PONG_SCORE`, confirm the **live GDScript/gameplay loop**, not just an idle video. Native AudioOut output markers remain active.
- This is a decisive **hardware acceptance PASS for the built-in Pong sample on the signed experimental v0.2.10 / PPSA99847**, compared with repeated v0.2.9 failures of only 1–3 frames per five-second window. The signed `godot-ps5-gles3-canvas-v0.2.10` release and main `version.json` TESTBUILD catalog were verified successfully published.
- Causal confidence: the only intended change from v0.2.9 is buffered stdout/stderr output; the large improvement is strong evidence of render-thread synchronous log I/O as a major contributor. We have **not** separately instrumented individual `write()` calls or reproduced a controlled `unbuffered` comparison in v0.2.10, so root cause should be stated as **strongly supported, not mathematically proven**.

**Preserve this known-good v0.2.10 signed release as a hardware-validated rollback baseline. Do not overwrite or regress it during later experiments.**

Remaining acceptance: verify M12d external platformer and other larger Godot 4.7.2 projects independently, stress the build for more than 50 seconds, and validate that buffered logs are flushed safely on orderly quit or explicit bounded flush without bringing back per-frame filesystem stalls. Original M26 stream buffering can leave unsynced logs if killed abruptly; prefer asynchronous collector or scheduled slow-path flush if production needs real-time diagnostics. Do not label universal PS5 Godot compatibility or all games as proven.
