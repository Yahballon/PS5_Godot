# M12 – Real Third-Party 2D Platformer #2201 on PS5 (Godot 4.7.2)

**Upstream original game:** [2D Platformer – Starter Kit 1.1.1](https://godotengine.org/asset-library/asset/2201), by **G2P Studios / AdilDevStuff**, original [GitHub repository](https://github.com/AdilDevStuff/2D-Platformer-Starter-Kit), pinned to commit `a48fc994cbcb168be472df84f2e13b55d2a2792f`, **MIT license**. Original 2D sprite assets credited to Kenney.nl, sound FX credited to Gdfxr. The original MIT license is preserved **inside the test installer ZIP and PCK**.

## M12c fast PCK, original playable console game retained (2026-10-23)

The user confirms the real M12b third-party platformer starts on PPSA99847 v0.1.6 and becomes controllable, but cold startup still takes **about 30–60 s**. Old M12b actual 13,271,676-byte PCK contained >9.3 MiB UNUSED original splash/icon raw textures and a multi-step diagnostic resource loader. Their existence and lack of gameplay references were verified against the packaged asset and actual level scene paths.

New **M12c** is a separate, independently built `m12c-platformer-asset2201.pck` with only six needed original scene texture `.ctex`, size **3,323,440 bytes** (75% smaller), one direct original Level_01 load and `Time.get_ticks_msec()` diagnostics for level resource load, real player scene, original WAV audio. It DOES NOT remove gameplay, coin art, levels, saves, or original MIT license; uses the same PS5 v0.1.6 native eboot.

[Host CI #39936285140](https://github.com/Yahballon/tmp_lap/actions/runs/39936285140) succeeded in Godot 4.7.2, including original CharacterBody2D grounded collision and WAV effect loading. Desktop total to Level_01 player was 17ms (not PS5). Separate `GodotPS5-M12c-Platformer-FAST-PS5-TEST.zip` (347,780 bytes) bundles new PCK plus launch config and license. PCK SHA256 `a44b5c60b613e770ffd1b7a277c30e410310a58eade3cf0935c89deff80ab551`.

Physical PS5 next step: time from app launch to controlling player, collect stdout markers `GODOT_PS5_M12C_LEVEL_LOAD_DONE duration_ms`, `GODOT_PS5_M12C_PLAYABLE_SCENE_READY total_ms`, `GODOT_PS5_M12C_AUDIO_LOAD_DONE duration_ms`, match them to native runtime startup timestamps; check levels, jump and sounds. No PS5 speed result can be asserted until user test.
## M12b real PS5 texture failure and fixed PCK (2026-10-23)

Original M12 PCK is proven **incompatible** with the current PS5 engine: screenshot shows stuck original splash, TAR `bfpilot-download (28).tar` shows missing PNG/WebP decoders for original lossless `.ctex` files in `scene/resources/compressed_texture.cpp:343`, preventing `Level_01.tscn` from loading (`GODOT_RETURN=1`). Original Godot host success DID NOT predict this PS5 failure.

**M12b is the replacement external PS5 test PCK.** Reproducible Godot 4.7.2 import changes only 9 texture import configurations (8 PNG + 1 SVG) to `compress/mode=3`, causing raw `CompressedTexture2D::DATA_FORMAT_IMAGE` payload instead of embedded PNG/WebP. Each `.ctex` header is checked for `GST2` magic and data-format 0 at offset 36. PCK also disables original splash and displays staged boot diagnostics while loading original textures, font, player scene, and Level_01. Original player/coin/level gameplay code remains unchanged.

[GitHub Actions #39933593514](https://github.com/Yahballon/tmp_lap/actions/runs/39933593514) PASSED: 9 raw image payloads, 99 bundled source/import files, complete original Level_01, grounded player physics and original `.wav` sounds. Real PS5 hardware test for this replacement is pending.

Install **GodotPS5-M12b-Platformer-SplashFix-PS5-TEST.zip** (625858 bytes): merge inner `GodotPS5/` contents into `/data/GodotPS5/`. It adds `games/m12b-platformer-asset2201.pck` (13271676 bytes, SHA256 `d2b62dd7c26dc77f8d187c05973e8aaba0da4335e73c2c6e9cec1ec121f4f7b7`), and changes only `launch.txt`. Existing native `PPSA99847 v0.1.6`, old PCKs and savegames remain untouched. During physical testing expect `GODOT_PS5_M12B_BOOT_READY`, `GODOT_PS5_M12B_PROBE_OK`, `GODOT_PS5_M12B_LEVEL_SWITCH_OK`, `GODOT_PS5_M12_SCENE_READY Level_01`; then confirm true visible sprites/coin UI, DualSense movement/X jump, audible original SFX. Send new three `gles3-*.log` files and screenshot/video. Do not claim hardware success until confirmed.
## Why this is a milestone

This is **not** a new trivial Godot smoke scene. It imports and runs the
**actual original third-party 2D platform game**, including:

- 2 original authored levels, original player animations and Camera2D
- CharacterBody2D floor collision, gravity, jumping, optional double-jump code
- Multiple real TileMapLayer ground and trap collision layers
- Animated sprites, CPUParticles2D, coin pickup and HUD/score
- Scene changes through LevelFinishDoor, original manager autoloads
- Original TrueType `Assets/Fonts/Star Choco.ttf` and four real `.wav` effects

No original gameplay code is rewritten. Only a **PS5Controls** autoload
maps existing `Left`, `Right`, `Jump` input actions to the DualSense
and logs scene loading and player position. Compatibility renderer replaces
upstream Forward Plus because our native Godot PS5 v0.1.6 is GLES3-based.
One desktop-only tutorial text is changed to the PS5 button names.

## Reproducible build

[GitHub Actions #39930320591](https://github.com/Yahballon/tmp_lap/actions/runs/39930320591)
**PASSED** on the original Godot 4.7.2 headless application.

- GitHub checkout of exact upstream asset pinned commit
- Editor import of all original PNG tilesets, fonts, WAV sound effects
- **92** packed original/game/imported files, genuine Godot 4.7 PCK
- Independent engine boot with `--main-pack`, Level_01 loaded
- PS5 DualSense actions created, CharacterBody2D player at (150,318)
- Host player fell onto actual ground and was grounded at
  `(150,447.959)` by physics tick 180
- No Godot script/scene loading errors detected in host acceptance
- Installable ZIP passed CRC, retained full upstream MIT license,
  PCK magic `GDPC`, format 4, Godot version 4.7
- PCK SHA256:
  `df286a34ac6df63950a7b73cd394dc5ee9975c1251dac53bcab940eab3a240ac`

**Important: this proves the third-party project loads and plays in desktop
Godot 4.7.2 headless, NOT yet on actual PS5 hardware.** v0.1.6 remains
the proven console engine version. It may still reveal missing image
texture importer support, other native modules or audio file decoding on
PS5, which must be diagnosed from console logs.

## PS5 testing – v0.1.6, PPSA99847

Download `GodotPS5-M12-Platformer-Asset2201-PS5-TEST.zip` from the
successful GitHub Actions artifact.

1. Extract it and copy its **`GodotPS5`** folder contents into the
   existing `/data/GodotPS5/` folder (merge files).
2. It installs only
   `/data/GodotPS5/games/m12-platformer-asset2201.pck`, and sets
   `/data/GodotPS5/launch.txt` to
   `m12-platformer-asset2201.pck` (with a newline).
3. Open your already installed **Godot PS5 v0.1.6** title
   `PPSA99847`. **No native `eboot.bin` change** and no update
   or new title ID is required.
4. Use **left stick or D-Pad** to move and **Cross (X)** to jump.
5. Test both levels, jumping on platforms, coins/score,
   camera scrolling, traps/respawn, scene transition and
   audible jumping/pickup/completion sound effects.
6. Send one photo/video of actual rendered level and a TAR with
   `/data/GodotPS5/gles3-stdout.log`,
   `gles3-stderr.log`, `gles3-runtime.log`.
   Host-only `SCENE_READY` markers do not prove console graphics.

Expected PS5 log markers from the unmodified original game
plus compatibility adapter:
```text
GODOT_PS5_M12_INPUT_READY DualSense left-stick DPad CROSS
GODOT_PS5_M12_SCENE_READY Level_01
GODOT_PS5_M12_PLAYER_FOUND position=(150.0, 318.0)
GODOT_PS5_M12_FRAME tick=180 ...
GODOT_PS5_M12_CROSS_JUMP
GODOT_PS5_M12_SCENE_READY Level_02
```

To return to the default Godot Pong sample, delete only
`/data/GodotPS5/launch.txt`. Older game PCKs, persistent saves and
the native `PPSA99847 v0.1.6` installation remain untouched.

## Next action after PS5 hardware test

**Until the player confirms this third-party platformer renders and plays
correctly on an actual console, M12 is 🟡 HOST-VALIDATED, HARDWARE-UNTESTED.**
If PS5 fails to boot/render/load textures, use real `gles3` logs to isolate
the missing native resource decoder/module. Don't invent green hardware
status from desktop CI.

Sources: MIT original upstream asset pinned at the SHA above, plus
`PS5Controls.gd`, `prepare_project.py`, `pack_m12.gd`,
`package_platformer.py` (PS5 wrapper code) in this folder.
