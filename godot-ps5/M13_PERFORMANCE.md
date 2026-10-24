# M13 – Real PS5 intermittent stutter: native CPU vs EGL/GPU swap profiling

**Date:** 2026-10-23. **Status:** The PS5 2D platformer is playable but intermittently drops to ~7.5fps. **M13 v0.1.7 native profiler is signed and published in TESTBUILD** ([full CI #39945288503](https://github.com/Yahballon/tmp_lap/actions/runs/39945288503), [experimental release](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gles3-canvas-v0.1.7), [PR #254 merged](https://github.com/Yahballon/tmp_lap/pull/254)); **physical M13 profiling and a real lag fix are not yet confirmed**. Do not call this a performance fix yet.

## User's physical PS5 evidence: bfpilot-download (31).tar

The **last** actual M12d run used `/data/GodotPS5/games/m12d-platformer-asset2201.pck` under known-good native Godot PS5 v0.1.6. `gles3-stdout.log` is append-only: isolate the LAST `GODOT_PS5_M12C_BOOT_READY` when interpreting M12D performance. Earlier v0.1.4/M12c and older error sessions MUST NOT be counted as current.

- `GODOT_PS5_M12C_BOOT_READY ts_ms=8137`
- `GODOT_PS5_M12C_LEVEL_LOAD_DONE duration_ms=2803 total_ms=4414`
- `GODOT_PS5_M12C_SCENE_SWITCH_REQUESTED rc=0 elapsed_ms=4484`
- `GODOT_PS5_M12C_PLAYABLE_SCENE_READY total_ms=5712` for **Level_01**. This is **only 1,228ms** scene creation after request, improved from the prior M12c **22,523ms** gap and 27,004ms to player. The original Godot startup still adds about 8.1 seconds beforehand.
- `GODOT_PS5_M12C_AUDIO_LOAD_DONE duration_ms=1584`: actual original WAV effects decode, improved from ~3538ms previously.
- `GODOT_PS5_M12D_NAV_DISABLED_CONFIRMED scene=Level_01 physics_ground=true physics_traps=true`; repeated for **Level_02**, confirming two real levels and intact collisions. The original gameplay and controller X work.
- **38 logged M12D frame hitches >=80ms** in the final run. Values **108–150ms**, often clustered and sometimes when the player stands still. Multiple 5-second slices have normal ~294–296 frames (59–60fps), but some show ~8 frames at **133ms/frame** and FPS readings **1–6**. The serious stutter is not a perception issue.
- **13 PS5 Gallium shader variant compile markers** during the last run, most around initial scenes; one new variant compiled later while playing. A later frame hitch of ~108ms happens near the variant compile, but this **does not prove shader compilation accounts for every large stall**.
- The append-only cumulative stderr has **370 historical** `navigation_map.is_null()` lines. The last M12d scene logs verify navigation DISABLED and physics ON, and the *recent M12d stdout* has no nav failures. Do NOT claim the cumulative 370 is 370 new M12d errors.
- The user's current `userdata/godot_app_userdata_2D-Platformer-Starter/shader_cache/` directory contains five standard Godot GLES3 cache blobs, so shader/cache data exists. That **does not confirm all PS5 Gallium pipeline variants are warmed or persisted**. Don't assume flushing the PCK or RAM-caching PNGs will fix EGL swap blocking.

## Why large RAM preloading is not the first intervention

The original M12c experiment already cut the external PCK from 13.3 MB to 3.3 MB **without** curing the massive stalls. M12d fixed unused TileMap navigation and cut scene-tree startup from 22.5 seconds to 1.2 seconds **without** curing intermittent 133ms frames. Large spikes also occur while the player stands still after resources and audio have loaded. Copying the entire PCK into RAM, turning on glFinish, or deleting shader caches may obscure the root cause, increase memory/boot time, or block the GPU.

## Actual native M13 instrumentation in engine wrapper

`native/gles3_canvas_main.cpp` is the real C++ entrypoint for the PS5 EGL/GLES3 context. It calls `display.swap()` from Godot's original DisplayServerPS5 rendering loop, so it is an ideal single measurement point.

New monotonic `CLOCK_MONOTONIC` timestamping around the **real swap** only:
- CPU/pre-swap interval = **time since the previous completed swap to the new present call**. This includes Godot scene updates, physics, renderer CPU submission and scheduling; it is NOT pure CPU computation.
- EGL-swap interval = **time blocked specifically within `Display::swap()`**. This can include vsync wait, driver/GPU, compositor, and scheduling. It is NOT by itself a GPU utilization figure.
- Total frame = sum of those intervals, with monotonic millisecond precision, no clock date/time changes or GPU readback.

Appends **bounded** diagnostics to existing `/data/GodotPS5/gles3-stdout.log`:
```text
GODOT_PS5_M13_NATIVE_FRAME_PROFILER_READY clock=monotonic threshold_ms=80
GODOT_PS5_M13_FRAME_SPIKE frame=N since_boot_ms=... cpu_before_swap_ms=... egl_swap_ms=... total_ms=... spike=N
GODOT_PS5_M13_FRAME_5S frames=N avg_cpu_ms=... avg_swap_ms=... max_cpu_ms=... max_swap_ms=... max_frame_ms=... spikes_80ms=N
```
Logs at most **8 individual spikes per five seconds**, plus one per 5s summary. No `glFinish`, `glReadPixels`, per-frame allocations or debug surface replacement. Existing audio, physics, fonts, PCKs and InputMap remain intact. Perf logging is best-effort: it should not be enabled as a permanent release feature without a hardware profile and minimal overhead check.

## Test and next action

Separate [M13 v0.1.7 signed native workflow](https://github.com/Yahballon/tmp_lap/actions/workflows/build-godot-ps5-m13-native-profiler.yml), [PR #254](https://github.com/Yahballon/tmp_lap/pull/254). Full CI #39945288503 **PASSED** native Godot compile/link and signed PPSA99847 with `contentVersion=01.000.008` while retaining the prior AudioOut, Physics2D and FreeType dependencies. [GitHub pre-release v0.1.7](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gles3-canvas-v0.1.7) and TESTBUILD main catalog version 0.1.7 are now live. Official release `PPSA99847.zip` is 22,657,871 bytes (SHA256 `14fbeb713ef6f6cf7dc50c214eddfe0fd0e8bfe6961907c9b956f099be272705`). No physical 0.1.7 console performance claims yet.

1. Install the signed **experimental v0.1.7** title from a verified successful CI artifact. Keep existing v0.1.6 ZIP for rollback.
2. Leave `/data/GodotPS5/launch.txt` pointing to `m12d-platformer-asset2201.pck`. No external PCK rebuild required for native profiling.
3. Cold start, run around both original game levels, reproduce the recurring severe stutters, wait at the idle scene, and use X/jump and coins as before.
4. Send **new** `gles3-stdout.log`, `gles3-stderr.log`, `gles3-runtime.log`. Isolate the newest M13 session (do not combine historical stats).
5. Compare `M12D_FRAME_HITCH` with `M13_FRAME_SPIKE` and `M13_FRAME_5S`, and GPU `[ps5-gallium] compile-shader` messages:
   - **EGL swap dominates:** prioritize PS5 driver/compositor/framepacing/vsync, shader compilation and pipeline cache; avoid blaming unrelated GDScript.
   - **CPU before swap dominates:** profile scene-tree/physics, font/audio/texture decode, disk I/O, and Godot render submission.
   - If both consistently low while gameplay delta spikes, investigate Godot scheduling and timer sources.
6. ONLY after the measured phase is known make a performance fix (e.g., shader warmup or native swap scheduling) and verify no loss of audible sound, controls, shader visuals or Level_02.

**PS5 hardware performance fix: NOT YET CONFIRMED.** Source and CI are distinct from hardware acceptance.
