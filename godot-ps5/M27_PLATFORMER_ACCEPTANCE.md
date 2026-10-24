# M27 hardware acceptance – Godot PS5 2D Platformer Starter Kit

Status: **HARDWARE ACCEPTANCE PASS — external M12d platformer at sustained 60 FPS**.
Date: 2026-10-24. Signed engine baseline: **v0.2.10, PPSA99847, Godot 4.7.2 GLES3**, PS5 firmware 5.10. **Do not rebuild or modify this known-good engine for this test.**

## Why this test

Real PS5 TAR #46 and user feedback establish the first ~50-second **60 FPS, no-stall Pong acceptance** on v0.2.10. After the initial warmup window, there were 9 consecutive intervals of 300 frames over 5 seconds with 0 >=80ms hitch counts. Only meaningful native difference vs v0.2.9 was stdout/stderr buffering with `M26_IO_A_B_MODE=1`. External gameplay remains an unverified separate acceptance gate.

The real 2D Platformer Starter Kit 1.1.1 (Godot Asset Library #2201) was packaged as **M12d** and originally suffered progressive frame stalls on older builds. It now passes an initial 30-second real-console test on M26. The user's archive `bfpilot-download (46).tar` contains `launch.txt.bak` with exactly `m12d-platformer-asset2201.pck`, and prior runtime history proves the loader resolves it to `/data/GodotPS5/games/m12d-platformer-asset2201.pck`. Earlier uploaded TAR #31 includes the original 3,325,680-byte PCK. SHA256:
`6d2145876d9c73e9d33c5c98336c56bb6e0339636e38b5ea58367c7f28ed05f2`.

## Activation – no new TESTBUILD homebrew needed

1. Ensure the user has **Godot PS5 GLES3 Canvas v0.2.10** installed through TESTBUILD (the already released signed title).
2. Check that `/data/GodotPS5/games/m12d-platformer-asset2201.pck` exists. Previous logs suggest it does.
3. Rename **`/data/GodotPS5/launch.txt.bak` to `/data/GodotPS5/launch.txt`** (its single line is `m12d-platformer-asset2201.pck`). Or create the same text if backup is missing. If the PCK is missing, use the original M12d package or supplied companion kit to copy `games/m12d-platformer-asset2201.pck`.
4. Keep `m26_log_mode.txt` absent, because **buffered logs are essential** to validated stable M26 performance. Keep `present_mode.txt` absent or `vsync`; leave native AudioOut enabled.
5. Fully close/restart same installed **PPSA99847**. Do not modify PS5 firmware or replace the engine EBOOT. Verify latest `gles3-runtime.log` says `PACK_SOURCE=CONFIG PACK=/data/GodotPS5/games/m12d-platformer-asset2201.pck` and `M26_IO_A_B_MODE=1`.

## Test matrix

| Subsystem | Physical action | Pass condition |
| --- | --- | --- |
| Scene loading | Start external M12d PCK | Fully loads both game menus/level 1 without remaining frozen |
| Controls | Left stick or D-pad move; X jump | Responds within frame, no repeat-button input delay |
| Collision + camera | Play Level 1 and Level 2 with jumps and moving camera | No severe geometry/collision regression, no seconds-long motion freezes |
| Rendering | Run / move continuously for 3–5 minutes | Ideally ~60 FPS; no progressive stalls / >=80ms bursts recurring |
| UI + score | Collect coins, restart, change level | HUD and interaction update reliably |
| Audio | Trigger game effects | Native AudioOut works; audio does not produce frame stalls |
| Regression | Rename `launch.txt` back to `launch.txt.bak` | Built-in Pong again loads at validated 60 FPS |

### Logs

The M26 stdout/stderr use static 128KiB full buffering. If the app is forcibly terminated, recent lines may not reach disk. Prefer normal exit if offered; collect `gles3-runtime.log` independently to confirm loaded pack and mode. For measured FPS, isolate lines from the **last session** after the external `PACK_SOURCE=CONFIG` marker, not appended older Pong summaries. Look for `GODOT_PS5_M13_FRAME_5S` with ~300 frames/5 sec, `M24_RENDER_5S`, `M25_VIEWPORT_5S`, M17 frame hitches and M12d script controls/audio markers.

Send user's next TAR and qualitative performance. **Do not mark external game / general Godot compatibility stable before that evidence arrives.** Preserve release `godot-ps5-gles3-canvas-v0.2.10` and main `version.json` with unchanged slug and title ID. This is a **test activation**, not a firmware update or an engine code change.

## Source / licenses

Upstream [2D Platformer Starter Kit](https://github.com/AdilDevStuff/2D-Platformer-Starter-Kit) pinned at `a48fc994cbcb168be472df84f2e13b55d2a2792f`. Original M12d packaging includes MIT license and credits (G2P Studios/AdilDevStuff, Kenney.nl art, Gdfxr sound). Do not expose runtime user's own uploaded PCK publicly in repo without explicit request; share the test kit directly with user only.


## Actual physical hardware result — PASS (user TAR #47, 2026-10-24)

The user tested the **unchanged signed PPSA99847 v0.2.10 M26 engine** on PS5 firmware 5.10 and reports that **the M12d Platformer starts quickly, both levels work, and gameplay has no persistent lags**. The actual uploaded `bfpilot-download (47).tar` was opened and its **last buffered M26 stdout session** isolated rather than mixing historical append-only results.

Grounded results:
- Last `gles3-runtime.log` contains `M26_IO_A_B_MODE=1` and `PACK_SOURCE=CONFIG PACK=/data/GodotPS5/games/m12d-platformer-asset2201.pck`, confirming **buffered I/O** and the original external Platformer PCK (not the built-in Pong).
- Console: native Godot `4.7.2.stable.custom_build`, GLES3, 1920x1080, Mesa 26.2.0 PS5 AGC, VSync active, native AudioOut confirmed with successful blocks 1, 2048 and 4096.
- All **six** new-session M12d game performance summaries report `fps=60.0`. They contain per-5s frame counts **302, 300, 299, 300, 300, 300**, with a single startup `GODOT_PS5_M12D_FRAME_HITCH frame_ms=136.9` in the first interval. After warmup there are **five complete 5-second M12d windows with zero hitches at >=80ms** (299–300 frames per interval), i.e. roughly **25 seconds of hitch-free observed game data** after the first interval.
- Independent M13 engine timing shows six windows: **275**, followed by **300, 300, 300, 300, 300** frames, all five steady windows **0 spikes >=80ms**, avg frame ~16.7ms, EGL swap ~0.11–0.13ms. The first window contains two startup-frame spikes of 161.1ms and 456.4ms and a costly scene-update step, but did **not** develop the previously progressive multi-second stalls. A separate 136.9ms game-script hitch occurs around the start.
- `GODOT_PS5_M12D_NAV_DISABLED_CONFIRMED scene=Level_01 physics_ground=true physics_traps=true` and separately `scene=Level_02` prove both game levels loaded with the intended ground/trap physics. Real `GODOT_PS5_M12_FRAME` heartbeats show horizontal movement and `grounded=false` during jumps (ticks through 1800), confirming interactive script/physics update instead of a frozen display.
- M24 and M25 viewport summaries show all five steady windows at 300 frames and zero >=80ms spikes. On this particular external Platformer shader workload the OpenGL framebuffer blit averages ~15ms, making the total frame around 16.7ms; this is normal steady-budget use rather than a multi-second freeze.
- The user independently confirms fast game entry and lag-free real-world interaction.

### Release/verification boundaries

**HARDWARE PASS**: bundled Pong and this external 2D Platformer have both shown sustained ~60 FPS on actual PS5 fw 5.10 with M26 buffered stdout/stderr. This supports a major stable baseline for 2D Godot GDScript, GLES3, physics, dualsense inputs, and AudioOut.

**NOT YET PROVED**: general Godot 4.7.2 game compatibility, 3D engine support, hours-long sessions, or every M12d feature (e.g. saving, all sounds, any additional levels). This uploaded run spans approximately 30 seconds of reported 5s windows—not the proposed full 3–5-minute endurance test—so avoid claiming more. There are two isolated startup frame hitches; reporting `0 hitches` only applies **after initial warmup**.

Preserve EXACT signed [v0.2.10](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gles3-canvas-v0.2.10), `PPSA99847`, and its TESTBUILD catalog entry; do not regress to earlier unbuffered logging. This documentation-only acceptance update makes **no engine/source/package modification**.

Next safe milestone: longer 2D game endurance test and another third-party Godot 4.x 2D PCK, not a speculative graphics driver rewrite.
