# Godot PS5 M10b – TileMapLayer and Label/TTF support

Independent **real Godot 4.7.2 external PCK tests**, compatible with the
previously confirmed **PPSA99847 v0.1.3** native physics engine for the TileMap test. **FONT FIX REQUIRES a new native v0.1.4 engine**: v0.1.3 lacks FreeType even though the Godot host builds the font PCK.

## A. Real TileMapLayer collision

See [m10b-tilemap](m10b-tilemap/). Godot builds an atlas texture, a
`TileSetAtlasSource`, `TileSet` physics layer, `TileData` collision
polygon and a nine-cell `TileMapLayer`. A `CharacterBody2D` falls
onto those physical tile collision shapes using `move_and_collide()`.
**Success requires the reported collider to be the TileMapLayer itself,
with floor contact normal and correct resting position.** No manually
painted fake tile floor or custom collision algorithm.

Expected picture: cyan moving square stops on a row of pink squares,
turns green, and the round test indicator at top becomes green.
Required stdout markers:
`GODOT_PS5_M10B_TILEMAP_READY`,
`GODOT_PS5_M10B_TILE_CONTACT_OK`,
`GODOT_PS5_M10B_TILE_TEST_PASS`.

## PS5 hardware results (23 October 2026)

- **TileMap PASS:** Actual PS5 `bfpilot-download (23).tar` contains `GODOT_PS5_M10B_TILE_CONTACT_OK tilemap=RealTileMapPlatform normal=(0,-1) y=742.984375`, `GODOT_PS5_M10B_TILE_TEST_PASS tick=139`, native `GODOT_RETURN=0` and clean EGL shutdown.
- **Font FAIL on native v0.1.3:** The external 118,204-byte `PressStart2P-Regular.ttf` was found, but after `GODOT_PS5_M10B_FONT_TTF_LOADED`, Godot emitted `GODOT_PS5_M10B_FONT_FAIL_GLYPH_A`, `GODOT_RETURN=93`. Native stderr: `FreeType: Can't load dynamic font, engine is compiled without FreeType support!`. **It is not a missing PCK; copying this PCK again does not repair it.**
- **Font now visually PASS on native v0.1.4 (23 October 2026):** [M10c PR #243](https://github.com/Yahballon/tmp_lap/pull/243) enabled upstream FreeType+TextServerFallback. The signed [PPSA99847 v0.1.4 release](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gles3-canvas-v0.1.4) is published, and the user screenshot `20261023_083016_00527039.png` shows all five Godot Labels, Press Start 2P rasterization and visible `Ä Ö Ü ß` on the real PS5. No further PCK edit required. X color reaction and final shutdown status remain unverified by a screenshot.

## B. Real Label / TrueType / Unicode

See [m10b-font-ui](m10b-font-ui/). Actual Godot `Control` and five
`Label` nodes with `FontFile.load_dynamic_font()`, explicit font
metrics and Press Start 2P test text including `Ä Ö Ü ß`.
This is a genuine TrueType font (Press Start 2P, SIL OFL 1.1) pulled
from [google/fonts](https://github.com/google/fonts/tree/92345ac0dbb28d27dbd32f3a782e84c55eaac214/ofl/pressstart2p)
at a pinned source commit. **Both OFL.txt and FONTLOG.txt are embedded
in the distributed font PCK.** No third-party font files are committed
to the source repository.

Headless CI validates font loading, glyph availability, metrics and
creation of the five Label nodes. **Headless CI cannot establish
visual text rendering** on the PS5 GPU. The user must visually inspect
the test and logs on console.

Expected picture: large cyan header, white font title, yellow
alphanumeric row, green umlaut row, and instructions. Press DualSense
X to turn the header pink and change the second label.
Required stdout:
`GODOT_PS5_M10B_FONT_RESOURCE_OK`,
`GODOT_PS5_M10B_FONT_TTF_LOADED`,
`GODOT_PS5_M10B_FONT_METRICS_OK`,
`GODOT_PS5_M10B_LABEL_TREE_READY`,
`GODOT_PS5_M10B_FONT_TEST_FINISHED`.

## PS5 screenshot acceptance (M10c)

**Visible text/TTF support: PASSED on physical PS5, 23 October 2026.** The uploaded screenshot `20261023_083016_00527039.png` shows `GODOT PS5 / M10B` in cyan, `LABEL + TRUE TYPE FONT` in white, numbers and letters in yellow, `UMLAUT: Ä Ö Ü ß` in green, and `PRESS X / CHANGE COLOR` in grey. These are five native Godot Label controls using the standalone font PCK and v0.1.4 FreeType-enabled engine. The screenshot does not establish X responsiveness, end-of-test exit code, or broad Unicode support; inspect new console logs as a separate check.

## Get the test ZIPs

Open [M10b GitHub Actions](https://github.com/Yahballon/tmp_lap/actions/workflows/build-godot-ps5-m10b-tilemap-font.yml).
After a **green** run, download
`Godot-PS5-M10b-TILEMAP-FONT-Host-Validated-PS5-UNTESTED` and extract it.
It contains two independent PS5 data-only ZIPs:

- `GodotPS5-M10b-TILEMAP-PS5-TEST.zip`
- `GodotPS5-M10b-FONT-UI-PS5-TEST.zip`

To test the first, extract its inner ZIP and copy the `GodotPS5/`
**contents** into `/data/GodotPS5/` on the PS5. This adds
`games/m10b-tilemap.pck` and sets `launch.txt` to `m10b-tilemap.pck`.
Start the existing PPSA99847 v0.1.3.

To test the font separately, extract its ZIP and copy in the same manner.
It adds `games/m10b-font-ui.pck` and overwrites **only**
`launch.txt`, selecting `m10b-font-ui.pck`. Earlier PCKs remain.

Alternatively, if both PCKs already exist, you can change just
`/data/GodotPS5/launch.txt` to the filename of the desired PCK.

After each test inspect:
`/data/GodotPS5/gles3-stdout.log`,
`/data/GodotPS5/gles3-runtime.log`,
`/data/GodotPS5/gles3-stderr.log`.

**Acceptance:** TileMap PS5 evidence already passed; the font test must be repeated on FreeType-enabled native v0.1.4. Both require
`PACK_SOURCE=CONFIG`, `GODOT_RETURN=0`, `NORMAL_SHUTDOWN`,
`EGL_CLOSED`. An unreadable Label on PS5 means the font milestone
remains OPEN even if CI and script logs are green. When finished remove
`launch.txt` to return to Pong. **No native executable rebuild.**

Do not claim Audio, 3D, Savegames, arbitrary TileSet features, full
TextServer or universal Godot project compatibility from these fixtures.
