# M12d – Original G2P 2D Platformer: PS5 Tile Navigation and Hitch Fix

Status (2026-10-23): **PS5 performance root cause diagnosed, external PCK fix host-validated only once dedicated Actions succeeds; console speed result still PENDING.**

## Real PS5 diagnostic TAR #30

The user ran M12c `m12c-platformer-asset2201.pck` on a PS5 firmware 5.10, native Godot v0.1.6. It DOES load the original Level_01 and original sounds, but cold startup still takes 30–60 seconds and gameplay occasionally stutters. An independent inspection of `bfpilot-download (30).tar` found, in the **last** M12c stdout session:

```text
GODOT_PS5_M12C_BOOT_READY ts_ms=8124
GODOT_PS5_M12C_LEVEL_LOAD_BEGIN elapsed_ms=1608
GODOT_PS5_M12C_LEVEL_LOAD_DONE duration_ms=2799 total_ms=4407
GODOT_PS5_M12C_SCENE_SWITCH_REQUESTED rc=0 elapsed_ms=4481
GODOT_PS5_M12_SCENE_READY Level_01
GODOT_PS5_M12C_PLAYABLE_SCENE_READY total_ms=27004
GODOT_PS5_M12C_AUDIO_LOAD_DONE duration_ms=3538
```

The **scene-tree initialization** gap after successful resource loading is therefore **22,523 milliseconds**. The existing engine opens its GPU and starts the app; original `CharacterBody2D` movement and X jump work after init.

The aggregated `gles3-stderr.log` in this TAR contains **332** occurrences of:
```text
ERROR: Condition "navigation_map.is_null()" is true.
   at: _navigation_update_cell (scene/2d/tile_map_layer.cpp:1394)
```
These failures correspond to unused TileMapLayer navigation update attempts on a PS5 Godot build without a valid navigation map. Shader compilation messages in the Gallium stdout also make renderer first-use hitches plausible, but their causal share is **not yet measured**. Do not attribute all 22.5 seconds solely to navigation until a hardware retest shows a difference.

## Root cause and non-destructive M12d fix

Official Godot 4.7.2 `scene/2d/tile_map_layer.h` defines:
```cpp
bool navigation_enabled = true;
bool collision_enabled = true;
```
Navigation is **separate** from physics collision. The upstream G2P Platformer asset does not use `NavigationAgent2D` or navigation polygons, but its `Level_01.tscn` and `Level_02.tscn` each have two original collision TileMapLayer nodes: `Ground` and `Traps`. Default navigation therefore does needless work / emits errors when the PS5 navigation server has no valid map.

M12d uses a **separate** upstream source patcher `prepare_project_navfix.py`:

- Runs the proven M12c PS5 raw-texture import and compact-PCK builder. The existing **M12b and M12c source files remain unchanged**.
- Adds `navigation_enabled = false` to exactly **4 original TileMapLayer nodes** (Ground/Traps in both scenes) **before** Godot 4.7.2 editor import.
- Does **not** disable `collision_enabled`, delete physics polygons, remove coins, alter original player/game rules, or remove sound effects.
- Generates a new distinct `m12d-platformer-asset2201.pck`. A copy of MIT license and `launch.txt` is bundled by `package_platformer_navfix.py`. Native `PPSA99847 v0.1.6` does not change.
- Adds `PS5ControlsSmooth.gd` debug markers verifying navigation is disabled and collision is ON on real scene objects. Logs frame hitches above 80ms (bounded) and 5s frame statistics for diagnosing lingering Gallium shader compilation stalls. Retains the original M12c scene/audio timing markers.

## Hardware acceptance

1. Merge contents of the ZIP's `GodotPS5` folder into `/data/GodotPS5/`; it only adds a new PCK and selects it via `launch.txt`.
2. Start existing Godot PS5 v0.1.6; test how many seconds until the player is controllable. Compare with M12c's **27,004 ms** after boot-scene initialized and 30–60s user's complete startup.
3. Verify the original Level_01 sprite/tiles/UI, Ground collision, trap restart, left stick / D-pad movement, X jump, sound effects, coin counter, transition to Level_02.
4. Export fresh `gles3-stdout.log`, `gles3-stderr.log`, `gles3-runtime.log`. Important markers:
   - `GODOT_PS5_M12D_NAV_DISABLED_CONFIRMED scene=Level_01 physics_ground=true physics_traps=true`
   - `GODOT_PS5_M12C_LEVEL_LOAD_DONE duration_ms=`
   - `GODOT_PS5_M12C_PLAYABLE_SCENE_READY total_ms=`
   - `GODOT_PS5_M12D_FRAME_HITCH frame_ms=`
   - `GODOT_PS5_M12D_FRAME_5S mean_ms=... worst_ms=... hitches_80ms=... fps=...`
   - **No new** `navigation_map.is_null()` errors in the latest run.
5. If the startup is still slow after errors disappear, focus next on native GLES3 shader compilation and PS5 scene-tree/TileMap physics initialization, using the actual timing data. Don't assume that smaller PCK size, texture import format or desktop CI proves PS5 performance.

Original game: [Asset #2201](https://godotengine.org/asset-library/asset/2201), G2P Studios/AdilDevStuff, pinned MIT upstream commit `a48fc994cbcb168be472df84f2e13b55d2a2792f`. No Sony system binaries or copyrighted proprietary audio redistributions in the data-only PCK.
