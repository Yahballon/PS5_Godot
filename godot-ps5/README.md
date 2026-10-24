# Godot 4.7.2 PS5 Homebrew Runtime

> **Projektstatus / Meilensteine:** [**MILESTONES.md – Erfolge, aktuelle Builds und nächste Aufgaben**](MILESTONES.md) · Stand 23.10.2026.
> **Currently (2026-10-23):** Godot v0.1.6 on real PS5 confirms original 2D physics, GDScript/GLES3, DualSense, TTF, saves, and audible AudioOut. Original G2P Studios Platformer Asset #2201 now loads both levels with M12d and native sound. PS5 TAR #31 confirms *faster Level_01 setup* (27.0→5.7s from test bootstrap) but sporadic **133–150ms frames** remain. M13 independent native v0.1.7 profiler branch instruments CPU-before-swap and EGL-swap times to locate rendering stalls. **M13 v0.1.7 is now signed and in TESTBUILD** ([native CI #39945288503](https://github.com/Yahballon/tmp_lap/actions/runs/39945288503), [official release](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gles3-canvas-v0.1.7), [merged PR #254](https://github.com/Yahballon/tmp_lap/pull/254)). Hardware perf trace and actual hitch fix remain OPEN; keep previously audible/playable v0.1.6 for rollback.

**by YAHBALLON** · AudioOut/GLES3 hardware test title ID `PPSA99847` · original Godot Engine (MIT)

## M13 Native profiler: why a real Godot platformer still has severe frame spikes (2026-10-23)

The real PS5 M12d platformer remains intermittently laggy despite **major launch improvement**. New user TAR `bfpilot-download (31).tar` shows Level_01 scene-player ready after **5,712ms** from BootFast initialization vs **27,004ms** with previous M12c. Both real original levels load, ground/trap TileMap collisions work and `navigation_enabled=false` is confirmed. Native audio still works.

However there are **38 measured >80ms frame spikes**, commonly **133–150ms** (7fps-like judder) including idle moments, alongside normal 60fps periods. Native PS5 Gallium also compiles shader variants during startup and in-game; no evidence yet that it explains *all* spikes. Existing 3.3MB compact PCK already fits in a small footprint, and preloading the package into RAM has not been shown to solve GPU/compositor stalls.

**M13 experimental native profiler** adds `CLOCK_MONOTONIC` timestamps around the real `display.swap()` PS5 GLES3 rendering hook. Its bounded, rate-limited `GODOT_PS5_M13_FRAME_SPIKE` logs report **CPU time before EGL swap** separately from **the time blocked in EGL swap**, and `M13_FRAME_5S` prints averages/maxima. This differentiates Godot/CPU/physics/IO stalls from Mesa/PS5-Gallium, swap/vsync or compositor stalls without forcing GPU synchronization. Proven native AudioOut/Fonts/Physics retained. Independent **v0.1.7 PPSA99847 experimental signed CI** with no automatic replacement of working 0.1.6.

**PS5 status:** v0.1.7 signed native cross-build PASSED and experimental TESTBUILD release PUBLISHED, but PS5 device trace pending. This is a **diagnostic**, not an FPS fix; real optimization comes after hardware measurements. [M13_PERFORMANCE.md](M13_PERFORMANCE.md), [PR #254](https://github.com/Yahballon/tmp_lap/pull/254), [native M13 workflow](https://github.com/Yahballon/tmp_lap/actions/workflows/build-godot-ps5-m13-native-profiler.yml). Keep the last proven M12d platformer PCK and its `launch.txt` setting.
## M12c Fast Boot – compact true third-party platformer PCK (2026-10-23)

The user now confirms real PS5 M12b gameplay works but waits **30–60 seconds** before controls become responsive. Previous M12b PCK binary inspection shows 13,271,676 bytes, 70% of which is unused 5.93 MiB disabled original splash and 3.34 MiB game icon (+ SVG icon). The M12b diagnostic boot preloaded unnecessary asset stages.

**M12c** uses separate files `prepare_project_fast.py`, `pack_m12_fast.gd`, `package_platformer_fast.py` and `PS5BootFast.gd`, preserving M12b source and all true game scenes. Original six game textures remain raw Godot `DATA_FORMAT_IMAGE`, while three unused images are excluded. It loads original Level_01 once after rendering one frame of status. `PS5ControlsFast.gd` marks when native PS5 Level_01 player is ready and `AudioManagerFast.gd` times original WAV loading; markers `M12C_LEVEL_LOAD_DONE duration_ms`, `M12C_PLAYABLE_SCENE_READY total_ms`, `M12C_AUDIO_LOAD_DONE duration_ms` will reveal where latency occurs.

[Original Godot 4.7.2 host CI #39936285140](https://github.com/Yahballon/tmp_lap/actions/runs/39936285140) **SUCCESS**: 87 real project files, PCK **3,323,440 bytes vs 13,271,676** (75% smaller), six PS5-compatible raw textures, original Level_01 and CharacterBody2D collision, original WAV effects. Host player-ready 17 ms is **NOT PS5 timing**.

**PS5 test**: `GodotPS5-M12c-Platformer-FAST-PS5-TEST.zip` (347,780 bytes), containing separate `games/m12c-platformer-asset2201.pck`, `launch.txt`, original MIT license, SHA256 `a44b5c60b613e770ffd1b7a277c30e410310a58eade3cf0935c89deff80ab551` for PCK. Copy folder contents into `/data/GodotPS5/`, use existing PPSA99847 v0.1.6; old M12b PCK/save files remain untouched. Confirm how many seconds to actual gameplay and share current 3 gles3 logs; do not assume hardware improvement from host measurements.
## M12b PS5 imported texture compatibility: WORKAROUND READY (2026-10-23)

The M12 third-party original Platformer was **not compatible** with the tested PS5 engine. User screenshot showed a frozen upstream Godot splash; `bfpilot-download (28).tar` proves native `GODOT_RETURN=1` and a failed Level_01 after Godot `CompressedTexture2D` tries to load original lossless `.ctex` sprites. Original source import configs specify `compress/mode=0`, which embeds PNG/WebP data; the existing PS5 build does not have usable PNG/WebP Image unpackers. The PCK itself and GPU successfully initialize.

**M12b** fixes the PCK WITHOUT a native engine rebuild: re-import eight PNGs plus the SVG icon as upstream `compress/mode=3` (VRAM Uncompressed) so `.ctex` has raw `DATA_FORMAT_IMAGE=0`; verify the binary field at offset 36 for each asset. A visible tiny PS5Boot loader replaces the opaque splash, then loads the original two-level game. Lightweight deferred audio/scene-manager autoloads keep the same original gameplay APIs.

[Official Godot 4.7.2 Actions #39933593514](https://github.com/Yahballon/tmp_lap/actions/runs/39933593514) **PASSED**: nine raw textures, 99 packed files, staged asset probes, original Level_01 boot and grounded CharacterBody2D collision, original WAV sounds, no script errors. [PR #251](https://github.com/Yahballon/tmp_lap/pull/251).

PS5 retest ZIP: **GodotPS5-M12b-Platformer-SplashFix-PS5-TEST.zip**, 625858 bytes, distinct 13271676-byte `m12b-platformer-asset2201.pck`, SHA256 `d2b62dd7c26dc77f8d187c05973e8aaba0da4335e73c2c6e9cec1ec121f4f7b7`. Extract/merge its `GodotPS5/` folder into `/data/GodotPS5/`, keep installed Godot PS5 v0.1.6. Other packs/saves are preserved and only `launch.txt` changes. **Still not physically validated**; request screenshot, audio/button report and new gles3 logs.
## M12 original 2D Platformer Starter Kit – third-party game PCK (23 October 2026)

[Godot Asset Library #2201](https://godotengine.org/asset-library/asset/2201)
**2D Platformer – Starter Kit 1.1.1** by G2P Studios / AdilDevStuff,
MIT-licensed and pinned to upstream commit
`a48fc994cbcb168be472df84f2e13b55d2a2792f`.

This is a genuine third-party Godot 4.7 2D platformer, not a synthetic smoke
test: includes **two existing levels**, CharacterBody2D gameplay,
TileMapLayer floor/trap collision, animated sprites, coin score/HUD,
camera, scene changes, original WAV effects, custom TTF font,
and particles.

The original source gameplay scripts remain intact. Our
`samples/m12-platformer-2201/PS5Controls.gd` adapter adds DualSense
**left stick / D-Pad move** and **Cross (X) jump** input actions and
readable PS5 log markers. Renderer switches from Forward Plus to
PS5 GLES3 Compatibility.

**Full real Godot 4.7.2 desktop host CI**
[#39930320591](https://github.com/Yahballon/tmp_lap/actions/runs/39930320591)
succeeded: imported original sprites/fonts/WAV, built a Godot
4.7 PCK with 92 included project+imported files,
loaded `Level_01`, found the player at (150,318),
and confirmed real floor collision at (150,447.959),
without script errors. A separate PS5-ready
`GodotPS5-M12-Platformer-Asset2201-PS5-TEST.zip`
was produced and checksum-verified.
The original MIT license and attribution are included.

**Install for PS5 hardware validation:** keep TESTBUILD-installed
**PPSA99847 v0.1.6**, extract the ZIP and copy its
`GodotPS5/` contents into `/data/GodotPS5/`.
This adds `games/m12-platformer-asset2201.pck` and
overwrites only `launch.txt` with the PCK name.
Launch Godot, move via stick/D-Pad and jump with X.
Inspect two levels, imported visuals, coins, scene transitions
and audible original effects. Share screenshots/video and
`gles3-stdout.log`, `gles3-stderr.log`, `gles3-runtime.log`.
Remove `launch.txt` to restore default Pong.

**Host-validated only: full PS5 gameplay compatibility is unverified
until the user confirms it on the physical console.**
Detailed English docs: [M12_README.md](samples/m12-platformer-2201/M12_README.md).
Source integration: [PR #250](https://github.com/Yahballon/tmp_lap/pull/250).

## M11d real audible PS5 Godot AudioStreamPlayer (23 October 2026)

**HARDWARE ACCEPTED on the real PS5, firmware 5.10.** The user installed
the signed `PPSA99847 v0.1.6` candidate, heard the six note sounds and
confirmed DualSense **X** replay. The accompanying
`bfpilot-download (27).tar` verifies a working 48,000 Hz native stereo
`AudioDriverPS5`/PS5 `libSceAudioOut` implementation.

The **final** run in cumulative stdout contains:
`GODOT_PS5_M11D_AUDIOOUT_THREAD_STARTED`,
`GODOT_PS5_M11C_AUDIOOUT_READY rate=48000 channels=2 frames=256`,
`GODOT_PS5_M11_AUDIO_MIX_RATE=48000.0`,
`GODOT_PS5_M11D_AUDIOOUT_OUTPUT_OK blocks=1` and `blocks=2048`,
**nine** `GODOT_PS5_M11_AUDIO_X_REPLAY` lines, plus
`GODOT_PS5_M11D_AUDIOOUT_CLOSE rc=0 blocks=2831 errors=0`.
Matching runtime confirms `GODOT_RETURN=0`, `NORMAL_SHUTDOWN`,
and `EGL_CLOSED` for `m11-audio.pck`. Unlike the older v0.1.5
sessions stored in the same TAR, the successful v0.1.6 session
has no dummy audio driver fallback and no AudioOut output errors.

Root cause of the old silence was a Thread::ID return value incorrectly
compared to Error::OK, which caused a properly created audio worker to
be rejected and its handle closed. Corrected in
[PR #249](https://github.com/Yahballon/tmp_lap/pull/249), signed CI
[run #39924377575](https://github.com/Yahballon/tmp_lap/actions/runs/39924377575).
Script-cache warnings and minor shutdown object leaks remain
non-blocking but require independent investigation.

**Status: Native PS5 sound and replay proven.** Further music formats,
long sessions, pause/resume, streaming and compatibility with external
Godot games have **not** yet been independently validated. The main
A public [v0.1.6 prerelease](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gles3-canvas-v0.1.6) **now exists and is indexed by main TESTBUILD `version.json`** (published 2026-10-23 08:48:34 UTC; 22,657,378-byte `PPSA99847.zip`, SHA256 `e15323c7736eaeead0bad1158de33dd1a7f439e6510928b6661d34219ca96026`). Real PS5 audible sound + X replay was independently confirmed using the earlier signed v0.1.6 candidate; both hardware result and release are now verified.

## M11 PS5 result + M11b2 save direct-open repair (23 October 2026)

User TAR `bfpilot-download (24).tar` contains one M11a audio session and
two distinct M11b save sessions. Godot PCM and `AudioStreamPlayer` ran
successfully, with two X replay markers and clean `GODOT_RETURN=0`, but
the **user did not hear any sound**. The native `OS_PS5` currently
registers no real AudioDriver so Godot's sound output cannot be considered
implemented. Requires an independent native AudioOut integration.

M11b is subtler: both on-console sessions wrote and immediately reread
`user://m11-save-v1.txt` successfully, but each reported `new=1` as
if starting fresh. The same archive contains the physical
`userdata/GodotPS5M11Saves/m11-save-v1.txt` with correct
`GODOT_PS5_M11_SAVE_V1|1|960` content, proving writes and storage are
available. The PS5 `ACCESS_USERDATA` route currently remains
`FileAccessUnix`, whose `file_exists` checks POSIX `stat/access`
that are unreliable in this homebrew environment.

**M11b2 standalone external PCK fix:** [PR #246](https://github.com/Yahballon/tmp_lap/pull/246)
and [green Actions #39913555804](https://github.com/Yahballon/tmp_lap/actions/runs/39913555804).
It bypasses the brittle existence check, attempts a direct read before
writing, fails closed if an existing save cannot be read or fails checksum,
and visibly shows a **green SAVE RESTORED** label with old/new counts
using original Godot FreeType. Two separate host Godot processes genuinely
confirm `FIRST_LAUNCH_PASS new=1` followed by
`RESTART_PERSISTENCE_PASS old=1 new=2`.
The installed `PPSA99847 v0.1.4` requires **no native update** for this
standalone diagnostic. `GodotPS5-M11b2-SAVES-VISIBLE-FIX.zip` is a
new PCK/launch configuration; it preserves the previous user data.
**Real PS5 persistence acceptance still awaits the user test.**

## M11 AudioStreamPlayer and user:// savegames (23 October 2026)

Two independent **real Godot 4.7.2** PCK fixtures (no PS5 native rebuild).
Both passed [GitHub Actions run #39911102004](https://github.com/Yahballon/tmp_lap/actions/runs/39911102004).
Read [`samples/M11_README.md`](samples/M11_README.md) for installation, safety
and independent PS5 hardware acceptance criteria.

- **M11a audio:** A genuine `AudioStreamWAV` 16-bit PCM sound is generated in
GDScript and passed to `AudioStreamPlayer`, six notes and optional X replay.
CI sees `AUDIO_PCM_READY`, `AUDIO_PLAYER_STARTED` and `AUDIO_HOST_API_PASS`.
**Desktop playback-API success does NOT prove audible PS5 sound**; only user
hearing TV/headphone tones establishes console audio support. Existing
PS5 platform may still use a dummy sound output.
- **M11b savegames:** The PCK writes a checksum-protected `user://` save,
immediately reopens it, and CI launches a **second independent Godot
process** reading the old value and incrementing `1` to `2`. CI verified
`SAVE_FIRST_LAUNCH_PASS`, `SAVE_PERSIST_OK` and
`SAVE_RESTART_PERSISTENCE_PASS old=1 new=2`.
**PS5 filesystem writes are unverified** because `FileAccessPS5` currently
implements kernel I/O on reads but delegates writes to Unix libc. A failed
write on the actual console would require a separate native engine fix.

The successful workflow publishes independent ready-to-copy
`GodotPS5-M11a-AUDIO-TEST.zip` and `GodotPS5-M11b-SAVES-TEST.zip`.
Each adds just one PCK under `/data/GodotPS5/games/` and replaces
`launch.txt`. All earlier PS5 apps and packs remain present. The Save
test requires **two complete PS5 app launches** using the same PCK.
Collect three `gles3-*.log` files for reliable diagnostics.

**Both M11 hardware milestones remain OPEN** until the required audio
hearing report or PS5 save persistence report and logs are available.

## M10c FreeType/Label native engine repair (23 October 2026)

**PS5 diagnostic:** User-provided `bfpilot-download (23).tar` contains two
failed Label test runs; `m10b-font-ui.pck` loads correctly
(`FONT_RESOURCE_OK size=118204`), yet `FontFile.has_char(65)` fails
(`FONT_FAIL_GLYPH_A`; `GODOT_RETURN=93`). Godot stderr explains:
`FreeType: Can't load dynamic font, engine is compiled without FreeType support!`.
This is a **missing native PS5 module**, not an incorrect PCK.

The **real TileMapLayer test passed on the same hardware**:
`TILE_CONTACT_OK normal=(0,-1) y=742.984375`,
`TILE_TEST_PASS tick=139`, `GODOT_RETURN=0`.

A new isolated [M10c pull request](https://github.com/Yahballon/tmp_lap/pull/243)
enables official upstream Godot 4.7.2 FreeType and TextServerFallback, builds
signed `PPSA99847 v0.1.4` while retaining v0.1.3 Physics2D, and verifies
the genuine FreeType and fallback text libraries are in the PS5 link
manifest. [M10c native build](https://github.com/Yahballon/tmp_lap/actions/runs/39879701956).

**Current status:** Signed native **PPSA99847 v0.1.4 FreeType installer published** as [GitHub prerelease](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gles3-canvas-v0.1.4) on 23 October 2026 at 01:30 UTC and indexed in TESTBUILD `version.json` on `main`. **Physical PS5 visible text/Unicode acceptance has now PASSED (23 October 2026):** the user screenshot `20261023_083016_00527039.png` shows the actual external `m10b-font-ui.pck` with five distinct Godot Labels in the Press Start 2P TrueType font, valid colored glyphs, numbers and `Ä Ö Ü ß`. The v0.1.3 FreeType-disabled failure is resolved for this sample. X interaction and final `GODOT_RETURN=0`/`EGL_CLOSED` markers are **not established by a static screenshot**, so full lifecycle acceptance remains open. Once the signed native
installer is available, leave `/data/GodotPS5/launch.txt` selecting
`m10b-font-ui.pck` and inspect visible Labels/umlauts, PS5 log markers
and graceful return. Visible native FreeType/Label rendering is now confirmed; continue testing X input, shutdown logs and further font/script coverage separately.
A trusted GitHub publisher was added on the default branch to release
`v0.1.4` into the TESTBUILDS catalog **after successful branch build**.
The previous v0.1.3 native installer remains a rollback candidate.

## M10b independent tile physics and real Label/TTF (23 October 2026)

Two official Godot 4.7.2 external PCKs are built, host-executed and available
as individual PS5-ready test ZIPs. Source and installation runbook:
[`samples/M10B_README.md`](samples/M10B_README.md).

1. **TileMapLayer** has real `TileSet` collision polygons, atlas textures and
nine grid cells. Upstream `CharacterBody2D.move_and_collide()` identified
`RealTileMapPlatform` as the collision target, normal `(0,-1)`,
`GODOT_PS5_M10B_TILE_TEST_PASS tick=139` on the host. Not manual collision.
2. **Control/Labels/Fonts** includes a real `FontFile` dynamically loaded
from a licensed, pinned Press Start 2P TTF with `OFL.txt` and
`FONTLOG.txt` embedded. The host measured glyphs and rendered control
nodes to a headless scene (`LABEL_TREE_READY count=5`);
**visual glyph appearance on PS5 remains unverified.**

[Host GitHub Actions #39878279649](https://github.com/Yahballon/tmp_lap/actions/runs/39878279649)
is **SUCCESS**, publishing test files for the unchanged `PPSA99847 v0.1.3`
under artifact `Godot-PS5-M10b-TILEMAP-FONT-Host-Validated-PS5-UNTESTED`.
Each ZIP supplies `/data/GodotPS5/games/` and selects its own `.pck`
using `launch.txt`. Older samples remain installed. **Do not mark either
M10b feature as PS5 supported without its individual physical-console
report/logs**, particularly visible text and Unicode rendering.

## M10a real RigidBody2D + Area2D external PCK (23 October 2026)

This is a separate, host-validated Godot 4.7.2 project at
[`samples/dynamics-area-smoke/`](samples/dynamics-area-smoke/README.md).
Using original Godot PhysicsServer2D, a gravity-driven `RigidBody2D` crosses
an `Area2D` trigger and settles on a `StaticBody2D` platform. The scene
requires real engine signals: `body_entered`, `body_exited`, a rigid-body
floor contact, and a settled location/zero-velocity result.

[Actions run #39876290256](https://github.com/Yahballon/tmp_lap/actions/runs/39876290256)
**passed on official desktop/headless Godot 4.7.2**, reporting
`GODOT_PS5_M10A_TEST_PASS ticks=143 rest_y=777.3 velocity=(0,0)`.
The workflow published an independent, ready-to-copy
`GodotPS5-M10a-RIGIDBODY-AREA-TEST.zip` which contains only
`games/dynamics-area-smoke.pck`, `launch.txt` and diagnostic instructions.
It runs with **already installed PPSA99847 v0.1.3** and does **not** replace
the native PS5 executable, Pong, or the previous external PCKs.

**PS5 hardware acceptance PASSED (23 October 2026).** The user confirmed the falling-ball visual, and provided `bfpilot-download (22).tar`, including **two complete on-console sessions**. Both stdout runs log `GODOT_PS5_M10A_AREA_ENTER_OK y=409.258422851563`, `GODOT_PS5_M10A_AREA_EXIT_OK y=646.669494628906`, `GODOT_PS5_M10A_RIGID_CONTACT_OK y=777.437438964844`, and `GODOT_PS5_M10A_TEST_PASS ticks=143 rest_y=777.299987792969 velocity=(0.0, 0.0)`. Their runtime segments show `PACK_SOURCE=CONFIG`, `GODOT_RETURN=0`, `NORMAL_SHUTDOWN`, `EGL_CLOSED`. The remaining `project.binary`/global script-cache errors in stderr were **nonblocking** here. Do not extrapolate this to tilemaps, fonts/UI, audio, saving, or third-party Godot games.

## M9b native PhysicsServer2D acceptance on PS5 (23 October 2026)

**PASS – genuine upstream Godot 4.7.2 2D physics is running on a physical PS5.**
The M9a sample `physics-smoke.pck` uses `CharacterBody2D.move_and_collide()` against
a `StaticBody2D` wall with `CollisionShape2D`; no hand-coded bounce or
visual-only stand-in. The known-good v0.1.2 previously ran with
`PhysicsServer2DDummy` and timed out (`GODOT_RETURN=43`).

The independent native `PPSA99847 v0.1.3` engine was built and signed in
[Actions #39872101079](https://github.com/Yahballon/tmp_lap/actions/runs/39872101079)
and [PR #238](https://github.com/Yahballon/tmp_lap/pull/238) enabled the
real `godot_physics_2d` module. User-provided console logs
(`bfpilot-download (21).tar`) contain **two** successful sessions:

```text
GODOT_PS5_M9_BODIES_READY
GODOT_PS5_M9_REAL_COLLISION_OK x=1093.984375 normal=(-1.0, 0.0)
GODOT_PS5_M9_TEST_PASS physics_frames=369
GODOT_RETURN=0
NORMAL_SHUTDOWN
EGL_CLOSED
```

The two latest hardware sessions contain **no dummy PhysicsServer2D fallback warning**.
Earlier appended logs in the same TAR retain old dummy warnings and timeouts
from the previous build; distinguish sessions, rather than searching the
full accumulated log for any old warning. Nonblocking `project.binary` and
global script cache diagnostics still appear and can be revisited.

This **does not yet establish** `RigidBody2D`, `Area2D`, `TileMap`, UI fonts,
audio, savegames or general third-party game compatibility. Next milestone:
broader Godot 2D API acceptance using separate external PCKs.

## M8c acceptance: independent Godot PCK on PS5 (23 October 2026)

The user confirms that the separate `external-smoke.pck` loaded by existing `PPSA99847 v0.1.2` via `/data/GodotPS5/launch.txt`, transitioned between both Canvas2D scenes and responded to DualSense X as expected. **No native `eboot.bin` rebuild was required.** The standalone PCK was generated and host-tested by successful [Actions run #39866584380](https://github.com/Yahballon/tmp_lap/actions/runs/39866584380). See [`samples/external-pack-smoke/README.md`](samples/external-pack-smoke/README.md). User-confirmed PS5 behavior is stronger than CI-only evidence, but FPS, full input mapping and shutdown log markers have not yet been independently recorded for this sample. This does not establish general compatibility with arbitrary Godot projects. The **next milestone is real 2D physics**, not just hand-coded Pong collision.

## Breakthrough: Real Godot 4.7.2 GLES3 Canvas2D on PS5 hardware

**22 Oct 2026 – physical PS5 user test passed for PPSA99847 v0.1.0.**
The screenshot supplied by the user shows an actual Godot-produced
translucent `Sprite2D` checkerboard over a `ColorRect`; DualSense X
drives GDScript background color changes. The PS5 logs in
`bfpilot-download (18).tar` contain four successful native engine
sessions (1001, 1145, 1136 and 1106 Godot GL swaps), with return code 0,
clean EGL shutdown and 223 GDScript Cross button press events.

**Unlike the previous GPL native scene bridge PPSA99845**, the new
`PPSA99847` test uses Godot's real `DisplayServerPS5`,
`RasterizerGLES3` and GLES3 CanvasItem pipeline. The wrapper provides
only EGL context creation and presentation, not a custom sprite renderer.

**Next experimental v0.1.1:** explicit Godot 4 external PCK selection
through `/data/GodotPS5/launch.txt`, with the working bundled 2D
fixture as fallback. See `gles3-canvas/README.md` for instructions.
The broad Godot API surface (fonts, audio, 2D/3D physics, arbitrary
projects and complex scenes) is **not** yet hardware validated.

**Licensing:** the original Godot engine is MIT, while the integrated
PS5 GPU bridge uses GPL-3.0-or-later components and a pinned unofficial
OpenGL SDK mirror requiring distribution/source provenance review.


## Hardware-confirmed DualSense-to-GDScript — PS5 v0.3.2 (2026-10-22)

The user-provided hardware TAR `bfpilot-download (14).tar` independently verifies
the **full end-to-end path**:

```text
[GodotPS5 engine] MAIN_ENTER_BEFORE_REDIRECT v0.3.2
[GodotPS5 engine] PACK_SOURCE=BUNDLED_SMOKE PACK=/app0/assets/godot/smoke.pck
[GodotPS5 PAD] CONNECTED dev=0
[GodotPS5 PAD] CROSS_DOWN
GODOT_PS5_SMOKE_READY
GODOT_PS5_DUALSENSE_TEST_WAITING
GODOT_PS5_DUALSENSE_CONNECTED
GODOT_PS5_DUALSENSE_CROSS_PRESSED
GODOT_PS5_DUALSENSE_TEST_FINISHED
[GodotPS5 engine] NATIVE_GODOT_RETURN=0
[GodotPS5 engine] SHELL_EXIT_REQUEST v0.3.2 status=0
```

The saved `engine-stdout.log` contains **38 distinct
`GODOT_PS5_DUALSENSE_CROSS_PRESSED` lines**. The bundled current GDScript
scene completed the 20-second input test and returned 0. This demonstrates
native PS5 `scePad` samples forwarded into the real Godot `Input` singleton
and observed by real GDScript on the console, not just a raw pad driver test.

The existing missing optional `project.binary`, `override.cfg`, script
cache and dummy PhysicsServer2D diagnostics did not prevent this headless
input smoke success. They must not be mistaken for verified graphics/physics
compatibility.

**Next:** start an isolated PS5 OpenGL/EGL GPU probe with a *different*
title ID `PPSA99844`, and only after actual video output on firmware 5.10
work toward the native Godot DisplayServer. `PPSA99843` remains the proven
headless runtime; do not add an unverified GPU probe to TESTBUILDS.

## Proven on real PS5

The **v0.2.11 headless build actually executes Godot GDScript on the console**.
A console TAR recorded:

```text
Godot Engine v4.7.2.stable.custom_build
GODOT_PS5_SMOKE_READY
```

The native `engine-smoke.log` independently recorded
`NATIVE_GODOT_RETURN=0` and a PS5 shell-exit request. This is a meaningful
engine milestone: we are running the real native Godot VM, resource loader,
project settings, main loop, and a GDScript scene, not emulating Godot.

**Not yet a playable game port:** Godot still runs headless; there is no PS5
DisplayServer, Vulkan or OpenGL renderer, or audio driver. The DualSense-to-Godot
Input bridge is **now proven on PS5 with v0.3.2** (X-button GDScript events).
Other input mappings and full graphical gameplay still require hardware tests.

## PS5 hardware discovery and v0.3.2 fix

User's 22 Oct 2026 PS5 console log (TAR #13) confirms native
`[GodotPS5 PAD] CONNECTED dev=0` and `[GodotPS5 PAD] CROSS_DOWN`.
However its selected pack is `PACK_SOURCE=AUTOSCAN PACK=/mnt/usb0/godot/smoke.pck`.
That USB fixture is older and prints only `GODOT_PS5_SMOKE_READY`:
it has no `GODOT_PS5_DUALSENSE_TEST_WAITING` marker. That v0.3.1 finding was resolved in the subsequent v0.3.2 hardware test:
GDScript now logs real Cross button presses.

v0.3.2 fixes the test collision: automatic discovery ignores a file named
`smoke.pck` (case insensitive) in external folders, but still launches real
external games such as `Demo.pck`. The bundled current smoke pack then
runs when no other game PCK is detected. A user may explicitly select an
external `smoke.pck` with `/data/GodotPS5/launch.txt` if desired.
Run the bundled smoke and check for `GODOT_PS5_DUALSENSE_TEST_WAITING`,
`GODOT_PS5_DUALSENSE_CONNECTED`, and
`GODOT_PS5_DUALSENSE_CROSS_PRESSED` before claiming success.

## Next native milestone: DualSense → Godot Input (v0.3.2 test)

The **experimental** controller bridge now uses the native PS5 `scePad` and
user-service interfaces to pass controller input to the real Godot
`Input` singleton. Cross/Circle/Square/Triangle, D-pad, L1/R1, L3/R3,
Options, touchpad click, dual analog sticks and analog triggers are mapped.
Native samples are consumed in batches to preserve short presses.
Connection, disconnection, short-lived controller interception and retry
are handled without using the app's UI-specific pad classes.

Host mapping and 120-byte sample ABI tests are present. **DualSense X and
connection events are now proven end-to-end on real PS5 hardware.** The built-in `smoke.pck` still immediately prints
`GODOT_PS5_SMOKE_READY`, then waits up to **20 seconds** for a controller:
press X (Cross) on the DualSense and read these console logs:

```text
/data/GodotPS5/engine-stderr.log   # [GodotPS5 PAD] CONNECTED / CROSS_DOWN
/data/GodotPS5/engine-stdout.log   # GODOT_PS5_DUALSENSE_CONNECTED
                                   # GODOT_PS5_DUALSENSE_CROSS_PRESSED
```

A headless test has **no display output**; the logs are the acceptance
criteria, not a visible controller UI. If an external PCK is explicitly selected by `launch.txt`, or a non-smoke
external game is auto-detected, it runs instead of the bundled controller test.
To test the bundled fixture, remove `launch.txt` and temporarily move all
external `.pck` files other than old `smoke.pck` out of the scanned folders.

The **graphics** milestone is next: an isolated GPU/display probe and then a
real Godot DisplayServer / renderer. DualSense events do not by themselves
enable visual gameplay.

## Next milestone: universal PCK launcher (v0.3.0 test)

The experimental launcher now supports **standalone Godot 4 .pck projects**
without rebuilding the executable for each project.

Launch order:

1. `/data/GodotPS5/launch.txt` — a text file containing one absolute PCK
   path or a basename such as `Demo.pck` (which selects
   `/data/GodotPS5/games/Demo.pck`)
2. First alphabetically valid `.pck` in
   `/data/GodotPS5/games/`, `/mnt/usb0/godot/`,
   `/mnt/usb1/godot/`, `/mnt/usb2/godot/`,
   `/mnt/usb3/godot/` or `/mnt/usb0/GodotPS5/games/`
3. The packaged `/app0/assets/godot/smoke.pck` fallback

Example `launch.txt`:

```text
/mnt/usb0/godot/MyGodotGame.pck
```

The kernel-based selector checks native PCK headers and restricts external
paths to dedicated game folders. The next CI build tests these rules using
host and simulated PS5-kernel tests; **external-game launching has not yet
been verified on hardware.** Projects requiring a graphical renderer, 2D/3D
physics, sound or normal gamepad input are not compatible yet.

Runtime logs:

```text
/data/GodotPS5/engine-smoke.log
/data/GodotPS5/engine-stdout.log
/data/GodotPS5/engine-stderr.log
```

Look for `PACK_SOURCE=CONFIG`, `PACK_SOURCE=AUTOSCAN` or
`PACK_SOURCE=BUNDLED_SMOKE` to confirm which PCK was selected. Look for
`GODOT_PS5_SMOKE_READY` **only** when the bundled smoke script runs.

Read [GRAPHICS_BRINGUP.md](GRAPHICS_BRINGUP.md) for the concrete DisplayServer, Vulkan/OpenGL, DualSense, audio and hardware-verification roadmap.

## Engineering roadmap

1. **Real Godot VM and PCK I/O:** proven for the built-in v0.2.11 smoke test;
   v0.3.0 adds external project selection and tests.
2. **DualSense Input:** implement and verify PS5 pad connection, polling,
   button/axis events and Godot `Input` integration, without changing SDL
   or a non-PS5 platform.
3. **DisplayServer and rendering:** implement PS5 video output and a genuine
   Godot-compatible graphics path; evaluate Vulkan/Godot RenderingDevice
   compatibility with public PS5 homebrew SDK before claiming game support.
4. **Audio + timing + savegames:** native sound and reliable per-game
   persistence, lifecycle, crash recovery and gameplay testing.
5. **General Godot games:** test one real Godot 4 2D project end-to-end,
   then 3D, shader and engine-feature compatibility.

## Build and source

Sources live under `engine/platform/ps5` and are overlaid on pinned upstream
Godot **4.7.2-stable**. `scripts/build-engine.sh` cross-compiles genuine Godot
static archives with Clang 18; native PS5-DevBridge links a signed
`PPSA99843/eboot.bin`, including the test PCK and normal
`sce_sys` package metadata. GitHub Actions validates host test fixtures and
provides signed installers through trusted default-branch publishing.

`ENGINE_PORTING.md` documents platform internals, native linker details,
source patches and runtime acceptance criteria.

## Licensing

- Original Godot Engine — [godotengine/godot](https://github.com/godotengine/godot) (MIT)
- PS5 homebrew port — YAHBALLON (MIT, see [LICENSE](LICENSE))
- Public PS5 SDK, PS5-DevBridge and other dependencies retain their own licenses
