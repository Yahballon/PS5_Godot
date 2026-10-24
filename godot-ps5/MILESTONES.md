# Godot 4.7.2 auf PS5 – Meilensteine & Roadmap

**Projekt:** PS5-Godot-Homebrew-Port von YAHBALLON  
**Stand:** 23. Oktober 2026 · PS5 Firmware **5.10** · Entwicklungsbranch `feature/godot-ps5-engine-foundation` · [PR #207](https://github.com/Yahballon/tmp_lap/pull/207)

> **Current milestone (2026-10-23): M12d original platformer now starts on PS5 in 5.712s after boot scene (previous M12c 27.004s) but severe 133–150ms gameplay stutters remain; M13 native CPU-vs-EGL profiler SIGNED, MERGED, RELEASED to TESTBUILD as experimental v0.1.7.** Physical PS5 TAR `bfpilot-download (31).tar` confirms full two-level game, `M12D_NAV_DISABLED_CONFIRMED` for Level_01/Level_02 with physics ON, `LEVEL_LOAD_DONE duration_ms=2803`, player ready `total_ms=5712`, original SFX `1584ms`. Yet 38 last-run 80ms+ frame spikes and 1–6 FPS slices remain, frequently when idle, with 133ms Godot delta likely capped. Last-run Gallium compiles 13+ shader variants; **not proven to be every stall cause**. Native M13 v0.1.7 measures monotonic time separately in Godot CPU/pre-swap vs PS5 EGL/GPU/swap, rate-limited `FRAME_SPIKE`/`FRAME_5S` events. [GitHub signed CI #39945288503](https://github.com/Yahballon/tmp_lap/actions/runs/39945288503) SUCCESS, v0.1.7 `PPSA99847` `01.000.008` verified. [PR #254](https://github.com/Yahballon/tmp_lap/pull/254) and [M12d PR #253](https://github.com/Yahballon/tmp_lap/pull/253) both squash merged to engine foundation. **Public experimental TESTBUILD v0.1.7** [release](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gles3-canvas-v0.1.7) published 2026-10-23 11:34:28 UTC, `PPSA99847.zip` 22,657,871 bytes, SHA256 `14fbeb713ef6f6cf7dc50c214eddfe0fd0e8bfe6961907c9b956f099be272705`, main `version.json` confirms 0.1.7. **v0.1.7 console hardware and FPS fix remain unverified:** user should test M12d PCK and collect M13 markers. Keep v0.1.6 rollback. Full details in `M13_PERFORMANCE.md`.

## Bedeutung der Statusangaben

- **✅ Auf PS5 bestätigt:** physischer Bildschirmtest und/oder konkrete Konsolenlogs liegen vor.
- **🟡 CI/Release erfolgreich:** der Code hat Tests/Kompilierung/Signierung bestanden, aber die jeweilige neue Funktion **noch keinen Hardware-Nachweis**.
- **⬜ Offen:** noch nicht umgesetzt oder ohne ausreichenden Funktionsnachweis.

Diese Unterscheidung ist wichtig: Ein erfolgreich signiertes ELF/ZIP ist **kein** Beweis, dass ein Spiel auf PS5 sichtbar oder spielbar ist.

## Erreichte Meilensteine

| Phase | Meilenstein | Ergebnis / belastbarer Nachweis | Status |
| --- | --- | --- | --- |
| M0 | Godot 4.7.2 nativ für PS5 bauen | `x86_64-sie-ps5`, Clang 18, native statische Engine-Bibliotheken, PS5-Installationspakete | ✅ Build |
| M1 | Echte Godot-VM auf der PS5 starten | `PPSA99843`: `GODOT_PS5_SMOKE_READY`, echte PCK/GDScript-Ausführung, `NATIVE_GODOT_RETURN=0` | ✅ Auf PS5 |
| M2 | DualSense an Godot Input anbinden | `PPSA99843 v0.3.2`: **38** `GODOT_PS5_DUALSENSE_CROSS_PRESSED` in GDScript | ✅ Auf PS5 |
| M3 | PS5-GPU initialisieren | `PPSA99844 v0.1.5`: EGL, Mesa **OpenGL 4.6**, **GLSL 4.60**, `PS5 AGC`, 1920×1080; sichtbare Farbwechsel, **1.800 Frames** | ✅ Auf PS5 |
| M4 | Native Shader/Geometrie | `PPSA99844 v0.1.6`: farbiges Dreieck, GLSL-Shader, VAO/VBO, `GL_FIRST_DRAW_ERROR=0`; Screenshot | ✅ Auf PS5 |
| M5 | 2D-Texturen und Blending | `PPSA99844 v0.1.7`: sichtbare RGBA-Schachbretttextur, UV-Mapping, Alpha-Blending | ✅ Auf PS5 |
| M6 | Godot + GPU in **einem** Prozess | `PPSA99845 v0.1.1`: echte Godot-GDScript-Szene steuert native OpenGL-Brücke; **24 X-Eingaben**, sichtbares Schachbrett, sauberes Ende in späterem Log | ✅ Auf PS5 |
| M7 | **Godots eigener GLES3-/Canvas2D-Renderer** | `PPSA99847 v0.1.0`: `DisplayServerPS5`, `RasterizerGLES3`, `Sprite2D`, `ColorRect`, Controller; **4.388 Godot-Swaps über vier Sitzungen**, **223 X-Meldungen**, Screenshot und sauberer Exit | ✅ Auf PS5 |
| M8a | Fremde Godot-PCK explizit auswählen | `PPSA99847 v0.1.2`: Externes `external-smoke.pck` über `launch.txt` auf PS5 geladen; Nutzer bestätigt Szenen und X-Interaktion | ✅ Auf PS5 vom Nutzer bestätigt (M8c) |
| M8b | Erstes Godot-Spiel als Hardwaretest | `PPSA99847 v0.1.2`: **Pong** läuft sichtbar auf echter PS5; Video zeigt Ballbewegung, Schläger und Punktestand. Individuelle Eingaben/Punkte/sauberer Exit ohne neue Pong-Logs nicht unabhängig nachgewiesen. | ✅ Auf PS5 sichtbar/laufend; 🟡 Detailabnahme offen |
| M8c | Eigenes externes Godot-4.7.2-PCK ohne eboot.bin-Neubau | Zwei Szenen, `res://palette.json`, GDScript, Canvas2D, DualSense-X; grüner CI-Lauf **39866584380** und Nutzerbericht „geht auch alles wie es soll“ | ✅ PS5-Funktion vom Nutzer bestätigt; 🟡 Hardware-Logs noch ausstehend |
| M9a | **Real PhysicsServer2D collision PCK** | Original-Godot-4.7.2-PCK mit `CharacterBody2D`, `StaticBody2D`, `CollisionShape2D`, `move_and_collide()`; Host-CI 39869677215 erfolgreich; auf PS5 mit v0.1.2 zunächst Dummy-Physics/Timeout, mit v0.1.3 echter Kontakt | ✅ PCK auf PS5 mit M9b erfolgreich; v0.1.2 ursprünglich fehlgeschlagen |
| M9b | **Native GodotPhysics2D / PPSA99847 v0.1.3** | Build [#39872101079](https://github.com/Yahballon/tmp_lap/actions/runs/39872101079) erfolgreich; `bfpilot-download (21).tar`: **2×** `REAL_COLLISION_OK`, `TEST_PASS physics_frames=369`, `GODOT_RETURN=0`, `EGL_CLOSED`, ohne Dummy-Warnung in den erfolgreichen Sitzungen | ✅ **Auf PS5 mit Logs bestätigt** |
| M10a | **Real RigidBody2D-Schwerkraft + Area2D-Signale (externes PCK)** | Echte PS5, Nutzerbericht und **2 vollständige Logläufe** aus `bfpilot-download (22).tar`: Eintritt y=409.2584, Austritt y=646.6695, Bodenkontakt y=777.4374; `TEST_PASS ticks=143`, Resthöhe 777.3000, Geschwindigkeit (0,0), `GODOT_RETURN=0`, `EGL_CLOSED`. Host CI [#39876290256](https://github.com/Yahballon/tmp_lap/actions/runs/39876290256) ebenfalls grün | ✅ **PS5 Hardware bestätigt (2×)** |
| M10b-a | **TileMapLayer + TileSetAtlasSource / echte Level-Kollision** | Echte PS5 `bfpilot-download (23).tar`: `GODOT_PS5_M10B_TILE_CONTACT_OK tilemap=RealTileMapPlatform normal=(0,-1) y=742.984375`, `GODOT_PS5_M10B_TILE_TEST_PASS tick=139`, `GODOT_RETURN=0`, normaler Shutdown | ✅ Auf PS5 bestätigt |
| M10b-b | **Control/Label + TrueType-Font** | Native v0.1.3 scheiterte mit `FONT_FAIL_GLYPH_A`, `GODOT_RETURN=93`. **Nach v0.1.4-FreeType-Fix:** Screenshot `20261023_083016_00527039.png` zeigt fünf echte Godot-Label-Zeilen mit Press Start 2P einschließlich `Ä Ö Ü ß`, Farben und Zahlen | ✅ **Sichtbare PS5-Textausgabe bestätigt; Interaktion/Exit-Logs offen** |
| M10c | **Native FreeType + TextServerFallback PS5 v0.1.4** | Signierter [GitHub v0.1.4-Release](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gles3-canvas-v0.1.4), Original-Godot-4.7.2-FreeType eingebunden; physisches PS5-Bild zeigt korrekt gerenderte Press Start 2P-Lettern inklusive deutscher Umlaute aus unabhängigem externem PCK | ✅ **PS5 visuelles FreeType/Label-Akzeptanzkriterium erfüllt; X/Exit separat offen** |
| M11a | **Original Godot `AudioStreamWAV`/`AudioStreamPlayer`** | Echte PS5 `bfpilot-download (24).tar`: `AUDIO_PCM_READY bytes=529200`, `AUDIO_PLAYER_STARTED`, X-Replay erkannt, Exit 0, **aber subjektiv kein hörbarer Ton**. Native PS5-Godot-Engine hat bislang keinen echten AudioOut-Treiber registriert | ❌ **Audio PS5 stumm; native AudioOut-Integration nötig** |
| M11b | **Godot `FileAccess` mit `user://`-Save** | Echte PS5, zwei Sessions: `SAVE_WRITE_OK current=1` und `VERIFY_READBACK_OK` erfolgreich; **zweiter Start erkennt vorhandene Save-Datei nicht**, obwohl `userdata/GodotPS5M11Saves/m11-save-v1.txt` im Nutzer-TAR vorhanden und valide ist | 🟡 **Schreiben klappt; Neustart-Erkennung schlägt fehl** |
| M11b2 | **Godot `user://`-Save über vollständige PS5-App-Neustarts** | Echte Konsole, `bfpilot-download (25)(1).tar`: drei hintereinander erfolgreiche `DIRECT_READ_OK`/`RESTART_PERSISTENCE_PASS`-Läufe **1→2→3→4**, exportierte Save-Datei `GODOT_PS5_M11_SAVE_V1|4|999`, mindestens zwei vollständige `GODOT_RETURN=0`/`EGL_CLOSED`/`NORMAL_SHUTDOWN`-Läufe | ✅ **Echte PS5-Persistenz 3× bestätigt** |
| M11c | **Erste Native AudioDriverPS5/libSceAudioOut-Integration (v0.1.5)** | Cross-Link und signierter Build liefen, echte PS5 `AUDIOOUT_INIT=0`, `OPEN handle=536870912`, aber `Thread::start()`-ID fälschlich als Fehler behandelt, Port geschlossen, Dummy-Fallback. Durch M11d v0.1.6 repariert | ❌ v0.1.5 Audio stumm (behoben in M11d) |
| M11d | **Godot AudioDriverPS5 / libSceAudioOut mit funktionierendem Thread (v0.1.6)** | **Echte PS5, `bfpilot-download (27).tar`:** Nutzer hört Töne und X-Replay. `THREAD_STARTED`, `AUDIOOUT_READY 48000 Hz stereo`, `OUTPUT_OK blocks=1/2048`, `CLOSE rc=0 blocks=2831 errors=0`, neun X-Replays, `GODOT_RETURN=0`, `EGL_CLOSED`, `NORMAL_SHUTDOWN`. [CI #39924377575](https://github.com/Yahballon/tmp_lap/actions/runs/39924377575) signiert; [PR #249](https://github.com/Yahballon/tmp_lap/pull/249) gemergt | ✅ **PS5-Hardware-Audio und X-Replay bestätigt** |
| M12 | **Original third-party Asset #2201 platformer** | PS5 bfpilot-download (28).tar: lossless .ctex fails to decode (missing PNG/WebP unpacker), no original Level_01; GODOT_RETURN=1 | ❌ PS5 hardware FAILED; superseded by M12b |
| M12b | **Real third-party Platformer with raw textures** | User now confirms actual original Level_01 on PS5 v0.1.6 starts and is controllable; **30–60 s startup** from launch to control; full game/audio/level2 still separately unverified | ✅ PS5 Level_01 playability confirmed, slow loading |
| M12c | **Fast compact original Platformer PCK** | [Godot 4.7.2 CI #39936285140](https://github.com/Yahballon/tmp_lap/actions/runs/39936285140) green, six real game raw `.ctex`, 87 files, **13,271,676 → 3,323,440 bytes (75% smaller)**; direct Level_01 load with M12C elapsed-ms markers for level, player, audio; desktop host player ready 17 ms. SHA256 a44b5c60b613e770ffd1b7a277c30e410310a58eade3cf0935c89deff80ab551 | 🟡 HOST PASS, PS5 speed retest OPEN |
| M12d | **Original Platformer PS5 TileMap navigation OFF (physical verified)** | Real user TAR #31: Level_01 player ready **5,712ms** from boot scene vs M12c 27,004ms; four TileMaps nav disabled, Ground/Traps physics ON; genuine Level_02 transition and audio. However **38 major frame hitches** persist, 133–150ms, including idle. | ✅ **PS5 fast scene initialization + gameplay**; ❌ **frame stutters ongoing** |
| M13 | **Native PS5 CPU-vs-EGL frame profiler v0.1.7** | [Signed CI #39945288503](https://github.com/Yahballon/tmp_lap/actions/runs/39945288503) SUCCESS, PPSA99847/01.000.008 ZIP checked. [PR #254](https://github.com/Yahballon/tmp_lap/pull/254) merged, trusted [v0.1.7 TESTBUILD prerelease](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gles3-canvas-v0.1.7) published with 22,657,871-byte ZIP, SHA256 14fbeb713ef6f6cf7dc50c214eddfe0fd0e8bfe6961907c9b956f099be272705. Native logs bounded monotonic `M13_FRAME_SPIKE cpu_before_swap_ms egl_swap_ms` plus 5s maxima/means; M12d original gameplay pack unchanged. | ✅ Signed & publicly testable, 🟡 PS5 CPU/EGL results/FPS fix open |

**Wichtig zu M6/M7:** M6 benutzte noch einen **eigenen nativen OpenGL-Zeichner**. **M7 ist der eigentliche Renderer-Durchbruch:** Das Schachbrett wird dort vom **originalen Godot-Canvas2D** gezeichnet, nicht von unserem Test-Shader. Die native Hülle besitzt nur EGL-Kontext, GL-Prozedurauflösung und Präsentation.

### Wichtige Hardware- und Build-Nachweise

| Nachweis | Quelle |
| --- | --- |
| Headless Engine + Pad | `bfpilot-download (14).tar`, `engine-stdout.log` / `engine-stderr.log`, `PPSA99843 v0.3.2` |
| Shader-Dreieck und Textur | PS5-Screenshots und `graphics-probe.log`, `PPSA99844 v0.1.6–0.1.7` |
| Szene → native OpenGL-Brücke | `bfpilot-download (16).tar`, `scene-bridge.log`, `PPSA99845 v0.1.1` |
| **Echtes Godot GLES3/Canvas2D** | PS5-Screenshot, `bfpilot-download (18).tar`, `gles3-runtime.log`, `gles3-stdout.log` |
| Pong v0.1.2 kompiliert/signiert | [Erfolgreicher GitHub Actions Build #39853780399](https://github.com/Yahballon/tmp_lap/actions/runs/39853780399) |
| **Pong v0.1.2 auf PS5 sichtbar und laufend** | Nutzer-Video `20261022_234930_00248487(1).webm` (13,88 s, 1920×1088, VP9), hier im Chat geprüft; dynamischer Ball und unterschiedliche Paddle-Positionen, kein Schwarzbild. Aussage des Nutzers: „geht bereits“. Keine neuen Pong-Logs eingereicht. |
| **M9b echte PhysicsServer2D-Kollision auf PS5** | Nutzer-TAR `bfpilot-download (21).tar`, jeweils 2× `GODOT_PS5_M9_REAL_COLLISION_OK`, `GODOT_PS5_M9_TEST_PASS physics_frames=369`, `GODOT_RETURN=0` und `EGL_CLOSED`; keine Dummy-Warnung in den letzten beiden stderr-Sessions |
| **M10a RigidBody2D und Area2D auf echter PS5** | Nutzer-TAR `bfpilot-download (22).tar`: zwei Sessions mit `GODOT_PS5_M10A_AREA_ENTER_OK`, `GODOT_PS5_M10A_AREA_EXIT_OK`, `GODOT_PS5_M10A_RIGID_CONTACT_OK`, `GODOT_PS5_M10A_TEST_PASS ticks=143`, plus `PACK_SOURCE=CONFIG`, `GODOT_RETURN=0`, `NORMAL_SHUTDOWN`, `EGL_CLOSED` |
| Echter GLES3-Test-Quellcode | [`gles3-canvas/README.md`](gles3-canvas/README.md), [`display_server_ps5.cpp`](engine/platform/ps5/display_server_ps5.cpp) |

Die vier geprüften GLES3-Sitzungen aus `bfpilot-download (18).tar` enthalten jeweils **1001 / 1145 / 1136 / 1106** Swap-Aufrufe, `GODOT_RETURN=0`, `NORMAL_SHUTDOWN` und `EGL_CLOSED`. Insgesamt wurden **223** `GODOT_PS5_REAL_2D_CROSS_PRESSED`-Meldungen protokolliert. Diese Werte gehören zur **bestätigten GLES3-Checkerboard-Version v0.1.0**, nicht zum neuen Pong.

## Aktuelle TESTBUILD-Titel

| Title-ID | App / Version | Zweck | Hardwarestand |
| --- | --- | --- | --- |
| `PPSA99842` | Godot PS5 Probe v0.1.0 | Frühes Native-Build-Grundgerüst | Diagnose/Legacy |
| `PPSA99843` | [Engine Smoke v0.3.2](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-engine-smoke-v0.3.2) | Original Godot VM, PCK, GDScript, DualSense | ✅ bestätigt |
| `PPSA99844` | [GPU Probe v0.1.7](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gpu-probe-v0.1.7) | EGL/GL, Triangle, Textur, Alpha | ✅ bestätigt |
| `PPSA99845` | [Scene Bridge v0.1.2](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-scene-bridge-v0.1.2) | Godot-Szene → **eigener** OpenGL-Renderer, Performance-Messung | ✅ **v0.1.1** bestätigt; v0.1.2 Diagnoseänderung |
| **`PPSA99847`** | **[GLES3 Canvas v0.1.2 + M9b Physics2D v0.1.3](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gles3-canvas-v0.1.2)** | **Echter Godot-Renderer mit neuem Pong-PCK** | ✅ Pong v0.1.2 sowie Physik v0.1.3 auf PS5 bestätigt (2 Log-Sessions) |

Alle genannten Versionen wurden mit dem `main/version.json`-Katalog abgeglichen. **Installierbare Builds kommen nur über erfolgreiche signierte GitHub Releases in TESTBUILD.** Bestehende Title-IDs und die bestätigten älteren Releases bleiben für Regressionstests erhalten.

## Wo wir aktuell stehen

```text
PS5 / Firmware 5.10
  └─ PPSA99847: Godot 4.7.2 / echtes GLES3 Canvas2D ✅
       ├─ PS5-Payload-SDK + Godot Main Loop ✅
       ├─ GDScript + SceneTree + Resource/PCK ✅ (eingeschränkt getestet)
       ├─ DualSense scePad → Godot Input ✅ (X sicher bestätigt)
       ├─ DisplayServerPS5 + RasterizerGLES3 ✅
       ├─ PS5 AGC / EGL / OpenGL 4.6 / GLAD ✅
       ├─ Shader/Texture/Sprite2D/ColorRect ✅
       ├─ Externe PCK-Auswahl ✅ (M8c auf PS5 vom Nutzer bestätigt)
       ├─ Pong Godot 2D ✅ (PS5-Video: sichtbar und laufend; Detail-Logs noch offen)
       └─ Fonts / Audio / Physik / Saves / 3D / allgemeine Spiele ⬜
```

**Der Status ist „funktionierender experimenteller Godot-2D-Renderer“, nicht „vollständige oder universelle Godot-PS5-Engine“.** Insbesondere darf aus der selbstgeschriebenen Pong-Kollision nicht auf einen funktionierenden Godot-PhysicsServer2D geschlossen werden.

## M8c – Independent external PCK acceptance fixture (23 October 2026)

**Status: ✅ Physical PS5 M8c behavior confirmed by user on 23 October 2026; 🟡 diagnostic logs/video not provided for this fixture.** The user tested the standalone `external-smoke.pck` with the existing `PPSA99847 v0.1.2` and reported that both Godot scenes and X-triggered color changes work as intended. This is real **user-reported console acceptance**, not just a host simulation. Official Godot 4.7.2 PCK generation, two-scene/asset runtime acceptance, header/ZIP/checksum verification and artifact publication all passed [CI run #39866584380](https://github.com/Yahballon/tmp_lap/actions/runs/39866584380). [PR #235](https://github.com/Yahballon/tmp_lap/pull/235) merged at `7f3fe710f9d11e399b49f96092ab0461b43dade3`. Do not claim measured FPS, independent shutdown traces or generalized third-party game support.

- New standalone project: [`samples/external-pack-smoke/`](samples/external-pack-smoke/README.md), deliberately **not** linked into the native PPSA99847 binary.
- New [`build-godot-ps5-external-pck.yml`](../../.github/workflows/build-godot-ps5-external-pck.yml) produces a genuine `external-smoke.pck` with official Godot 4.7.2, verifies markers in a Linux/headless game run, then runs strict PCK-header/ZIP checks. A passing workflow uploads artifact **`Godot-PS5-M8c-External-PCK-PS5-READY-HOST-TESTED`**, containing `external-smoke.pck` and nested **`GodotPS5-M8c-External-PCK-PS5-TEST.zip`**. CI is now **confirmed successful** in [run #39866584380](https://github.com/Yahballon/tmp_lap/actions/runs/39866584380), artifact `Godot-PS5-M8c-External-PCK-PS5-READY-HOST-TESTED` (artifact ID `12464481166`).
- The nested PS5-ready ZIP maps `GodotPS5/launch.txt`, `GodotPS5/games/external-smoke.pck`, instructions and SHA-256 so the user can copy its `GodotPS5` contents to `/data/GodotPS5` without modifying the known-good native runner. Packager [`make_ps5_test_bundle.py`](samples/external-pack-smoke/make_ps5_test_bundle.py) and mock regression [`test_external_pck_bundle.py`](tests/test_external_pck_bundle.py) are committed. Branch pushes invoke the workflow automatically; workflow_dispatch may not appear until the YAML is on the default branch.
- The PCK contains two `Node2D` scenes, their GDScripts and a `res://palette.json` resource. It tests **real** `FileAccess.open`, `JSON.parse_string`, scene switching, CanvasItem primitive rendering, X input and clean engine exit.
- Use `PPSA99847 v0.1.2` unchanged: copy artifact `external-smoke.pck` to `/data/GodotPS5/games/external-smoke.pck`; create `/data/GodotPS5/launch.txt` containing `external-smoke.pck`. Remove `launch.txt` afterward to restore the bundled Pong game.
- Expected `gles3-runtime.log`: `PACK_SOURCE=CONFIG`, `GODOT_SWAP_FIRST`, `GODOT_RETURN=0`, `NORMAL_SHUTDOWN`, `EGL_CLOSED`.
- Expected `gles3-stdout.log`: `GODOT_PS5_EXTERNAL_MAIN_READY`, `GODOT_PS5_EXTERNAL_ASSET_OK`, `GODOT_PS5_EXTERNAL_SCENE_CHANGE_REQUESTED`, `GODOT_PS5_EXTERNAL_SECOND_SCENE_READY`, `GODOT_PS5_EXTERNAL_FINISHED`; optional pad proof `GODOT_PS5_EXTERNAL_GAMEPAD_X`.
- **Acceptance result:** user confirms PS5 display, independent PCK loading, scenes and X behavior. **Hardware logs and independent video remain optional follow-up evidence** for accurate frame-time, resource-open and exit diagnostics. Do not relabel those measurements as proven without logs.
- No claims yet for broad Godot compatibility, saving, text rendering, PhysicsServer2D, audio or 3D.

## M9a – Real upstream GodotPhysics2D collision acceptance (23 October 2026)

**Status: 🟡 Real Godot 4.7.2 host collision verified; PS5 physics hardware test required.**
Host Actions run [39869677215](https://github.com/Yahballon/tmp_lap/actions/runs/39869677215) is **SUCCESS**. [PR #236](https://github.com/Yahballon/tmp_lap/pull/236) merged to this branch as `83fa6e4a6f2018ee04e4df659886c9fb1a7ad761`. Existing known-good `PPSA99847 v0.1.2` native executable was **not changed**.

- New [`samples/physics-smoke/`](samples/physics-smoke/README.md) contains a true Godot `CharacterBody2D` moving with `move_and_collide()`, a `StaticBody2D` wall, and engine `CollisionShape2D/RectangleShape2D` geometry. There is **no hand-coded contact/bounce**.
- Desktop Godot reported `GODOT_PS5_M9_REAL_COLLISION_OK x=1093.984375 normal=(-1.0, 0.0)` and `GODOT_PS5_M9_TEST_PASS physics_frames=369`, then exited successfully. Earlier first run [39869575617](https://github.com/Yahballon/tmp_lap/actions/runs/39869575617) correctly failed because its `--quit-after` cap was too short after actual contact; [39869677215](https://github.com/Yahballon/tmp_lap/actions/runs/39869677215) corrected the cap and passed all host steps.
- Download [M9a test artifact](https://github.com/Yahballon/tmp_lap/actions/runs/39869677215/artifacts/12466240152) named `Godot-PS5-M9a-REAL-PHYSICS-Host-Validated-PS5-UNTESTED`; extract the nested `GodotPS5-M9a-REAL-PHYSICS-TEST.zip`. The `physics-smoke.pck` is 5,440 bytes, **SHA-256 `414583c3e2cd79de23d9344df0b8b44c1cd15aaa76961327e919214add2c5ea1`**. The ZIP includes `GodotPS5/launch.txt` with `physics-smoke.pck`.
- Copy the nested ZIP's `GodotPS5/` contents under `/data/GodotPS5/`. This **replaces the selected launch.txt**, but leaves Pong, M8c, and native PS5 title unchanged. Open `PPSA99847 v0.1.2`.
- **Success criterion on PS5:** cyan CharacterBody2D moves right and physically stops at magenta StaticBody2D wall; visual body turns green only after real `move_and_collide()` returns matching collider and normal; logs contain `GODOT_PS5_M9_REAL_COLLISION_OK` and `GODOT_PS5_M9_TEST_PASS`. Also check native `gles3-runtime.log` for `PACK_SOURCE=CONFIG`, `GODOT_RETURN=0`, `NORMAL_SHUTDOWN`, and `EGL_CLOSED`.
- **Failure diagnostic:** if the square passes through the wall or prints `GODOT_PS5_M9_NO_COLLISION_PHYSICS_UNAVAILABLE`, the PS5 executable still needs native PhysicsServer2D support. **Do not mark M9 passed** simply because the desktop workflow or visible squares succeed. Capture `gles3-stdout.log`, `gles3-stderr.log`, and `gles3-runtime.log` before deciding whether to rebuild the native engine.

## M9b – Native GodotPhysics2D integration, PS5 v0.1.3 (23 October 2026)

**Status: ✅ auf echter PS5 erfolgreich, durch den Nutzer bestätigt und durch zwei vollständige Hardware-Log-Sessions unabhängig belegt.** Die native `GodotPhysics2D`-Implementierung ist geladen, echte Kollisionen und sauberer Exit funktionieren. Andere PhysicsServer2D-Funktionen, Performance und breite Spielekompatibilität müssen weiterhin separat getestet werden.

- Root cause observed on the user's PS5 M9a test: `Falling back to dummy PhysicsServer2D` and `GODOT_PS5_M9_TIMEOUT physics_frames=720`, resulting in `GODOT_RETURN=43`. The PCK and display rendered correctly, but the native engine had been compiled without the actual physics module.
- Fix in `scripts/build-engine.sh`: opt-in `GODOT_PS5_PHYSICS2D=1` enables the genuine Godot 4.7.2 `module_godot_physics_2d_enabled=yes` while retaining default behavior for previously verified versions.
- Dedicated [native M9b build #39872101079](https://github.com/Yahballon/tmp_lap/actions/runs/39872101079) **SUCCESS**: real GodotPhysics2D archive present, native PS5 engine compiled and linked, signed `eboot.bin` generated, `PPSA99847.zip` passed ZIP/integrity/title/version validation.
- PS5 package `PPSA99847`, version `01.000.004` (project v0.1.3), with default Pong and additional bundled `physics-smoke.pck`; explicit `launch.txt` still selects `/data/GodotPS5/games/physics-smoke.pck`. Build artifact `Godot-PS5-M9b-NATIVE-PHYSICS-v0.1.3-PS5-HARDWARE-UNTESTED`, artifact ID `12467676123`.
- [PR #238](https://github.com/Yahballon/tmp_lap/pull/238) merged to the engine foundation branch as `94bb83919c112e7ecafeff02a21b463b67d6f677`. Previous `PPSA99847 v0.1.2` remains available as regression fallback.
- **Hardware-Abnahme BESTANDEN (23.10.2026):** `bfpilot-download (21).tar` enthält zwei vollständige `physics-smoke.pck`-Läufe unter dem neuen `PPSA99847 v0.1.3`: je `GODOT_PS5_M9_BODIES_READY`, `GODOT_PS5_M9_REAL_COLLISION_OK x=1093.984375 normal=(-1.0, 0.0)` und `GODOT_PS5_M9_TEST_PASS physics_frames=369`; dazu `PACK_SOURCE=CONFIG`, `GODOT_RETURN=0`, `NORMAL_SHUTDOWN` und `EGL_CLOSED` im Runtime-Log. Zuvor im selben TAR enthalten: zwei alte Fehlversuche mit `GODOT_RETURN=43`, Dummy-Warnung und Timeout. Die beiden letzten Sessions enthalten **keine** Dummy-Warnung mehr.
- **Restwarnungen:** `Couldn't load file res://project.binary` und `Could not load global script cache` sind weiterhin im stderr der erfolgreichen Sitzungen vorhanden, blockieren hier nicht. Nur die getesteten Physics-Basics beanspruchen; noch keine Bestätigung für RigidBody2D, TileMaps, Areas, Joints, Audio, Fonts oder Savegames.

## M10a – Real rigid bodies, gravity and Area2D signals (23 October 2026)

**Status: ✅ HOST UND PHYSISCHE PS5 BESTANDEN.** Das unveränderte, bereits auf Hardware bestätigte `PPSA99847 v0.1.3` lädt das externe PCK und führt originale `RigidBody2D`-/`Area2D`-Physik aus. Zwei komplette aufeinanderfolgende Konsolenläufe durch `bfpilot-download (22).tar` bestätigt; keine neue native ELF-Datei erforderlich.

- Source and runbook: [`samples/dynamics-area-smoke/`](samples/dynamics-area-smoke/README.md). New [`build-godot-ps5-m10a-dynamics-area.yml`](../../.github/workflows/build-godot-ps5-m10a-dynamics-area.yml) builds a **genuine Godot 4.7.2 PCK** and starts it independently on a Linux host, then checks real engine physics signals and generates an installable PS5-ready *data-only* ZIP.
- CI **SUCCESS**: [run 39876290256](https://github.com/Yahballon/tmp_lap/actions/runs/39876290256), artifact `Godot-PS5-M10a-RIGIDBODY-AREA-HOST-PASS-PS5-UNTESTED` (ID `12468183558`). Standalone real Godot PCK SHA-256: `afec68be20df28c71119d8e8d23c3b19c8e81ace54739decbea2d810d8a908ff`.
- Host proof: `GODOT_PS5_M10A_AREA_ENTER_OK y=409.2584`, `GODOT_PS5_M10A_AREA_EXIT_OK y=646.6695`, `GODOT_PS5_M10A_RIGID_CONTACT_OK y=777.4374`, and `GODOT_PS5_M10A_TEST_PASS ticks=143 rest_y=777.3000 velocity=(0.0, 0.0)`. These are genuine Godot `Area2D.body_entered`, `Area2D.body_exited` and `RigidBody2D.body_entered` events with Godot-managed gravity and body position. No scripted movement or synthetic collisions.
- To test on PS5: extract **`GodotPS5-M10a-RIGIDBODY-AREA-TEST.zip`** inside the Actions artifact; copy `GodotPS5/` contents to `/data/GodotPS5/`. It adds `games/dynamics-area-smoke.pck` and writes `launch.txt` containing `dynamics-area-smoke.pck` (previous PCKs remain installed). Run existing `PPSA99847 v0.1.3`.
- Expected visual result: yellow ball falls through cyan trigger and lands on magenta platform, three signal lights turn green. Required console proof: `gles3-stdout.log` contains `GODOT_PS5_M10A_AREA_ENTER_OK`, `GODOT_PS5_M10A_AREA_EXIT_OK`, `GODOT_PS5_M10A_RIGID_CONTACT_OK`, `GODOT_PS5_M10A_TEST_PASS`; `gles3-runtime.log` contains `PACK_SOURCE=CONFIG`, `GODOT_RETURN=0`, `NORMAL_SHUTDOWN`, `EGL_CLOSED`.
- **Hardware acceptance COMPLETE:** User confirms the yellow ball falls through the cyan trigger and lands on the magenta platform. Two physical-console `gles3-stdout.log` sessions contain all four markers: `AREA_ENTER_OK y=409.258422851563`, `AREA_EXIT_OK y=646.669494628906`, `RIGID_CONTACT_OK y=777.437438964844`, `TEST_PASS ticks=143 rest_y=777.299987792969 velocity=(0.0,0.0)`. Corresponding `gles3-runtime.log` sessions show `PACK_SOURCE=CONFIG` with `/data/GodotPS5/games/dynamics-area-smoke.pck`, `TOTAL_GODOT_SWAP_COUNT=114/119`, `GODOT_RETURN=0`, `EGL_CLOSED`, `NORMAL_SHUTDOWN`. No M10a FAIL markers in either session.
- **Non-blocking diagnostics:** `gles3-stderr.log` still contains `Couldn't load file res://project.binary` and `Could not load global script cache`, yet M10a completes and exits normally. Follow up separately as a resource/cache compatibility issue. Still no verified support for `TileMapLayer`, `Label`/fonts, joints, audio, saves or arbitrary Godot projects.

## M10b – TileMapLayer-Kollision und echte Godot-UI/TrueType (23 October 2026)

**Status: 🟡 beide externen PCK-Projekte auf offizieller Desktop-Godot-4.7.2-Engine erfolgreich; beide physischen PS5-Hardwaretests stehen noch aus.** GitHub Actions [#39878279649](https://github.com/Yahballon/tmp_lap/actions/runs/39878279649) vollständig grün. [PR #242](https://github.com/Yahballon/tmp_lap/pull/242) dokumentiert Source, Host-Tests und separate Testpakete.

- **M10b-a TileMapLayer:** Eigenständiges `samples/m10b-tilemap/` erzeugt echte Textur, `TileSet`-Physikebene, `TileSetAtlasSource`, ein Kollisionspolygon pro Tile, neun `TileMapLayer`-Zellen. `CharacterBody2D.move_and_collide()` meldet im Host `GODOT_PS5_M10B_TILE_CONTACT_OK tilemap=RealTileMapPlatform normal=(0.0, -1.0) y=742.984375` und `GODOT_PS5_M10B_TILE_TEST_PASS tick=139`. **Kein vorgetäuschter Boden oder eigenes Kollisionssystem.**
- **M10b-b Text/Fonts:** Eigenständiges `samples/m10b-font-ui/` erstellt fünf echte Godot-`Label`-Nodes mit `FontFile.load_dynamic_font()`. Original Press Start 2P aus `google/fonts` auf Revision `92345ac0dbb28d27dbd32f3a782e84c55eaac214`, License `SIL OFL 1.1`, `OFL.txt` und `FONTLOG.txt` in PCK mitgeliefert. Host-Marker: `GODOT_PS5_M10B_FONT_RESOURCE_OK size=118204`, `GODOT_PS5_M10B_FONT_METRICS_OK size=(392.0, 28.0)`, `GODOT_PS5_M10B_LABEL_TREE_READY count=5`, `GODOT_PS5_M10B_FONT_TEST_FINISHED frames=480`. **Headless kann sichtbare GPU-Glyphen nicht bestätigen.**
- Host-erzeugte echte PCK-SHA256: **TileMap `9372acb6f978775b5378424427bb3e766df47ed95c42f623f1a63890e843c1a5`**, **Font `c8925cfe52dba5b128dd12aba47cd9ae07623919ae15899610a8942a293d0cc7`**.
- Download-Artefakt `Godot-PS5-M10b-TILEMAP-FONT-Host-Validated-PS5-UNTESTED` (ID `12469481706`). Es enthält **zwei getrennte ZIPs** `GodotPS5-M10b-TILEMAP-PS5-TEST.zip` und `GodotPS5-M10b-FONT-UI-PS5-TEST.zip`. Jeweils nur die Inhalte von `GodotPS5/` nach `/data/GodotPS5/` kopieren. Jede ZIP schreibt `launch.txt` auf ihr eigenes PCK; alle bisherigen PCKs und das **bekannt funktionierende PPSA99847 v0.1.3** bleiben unverändert.
- **PS5-Abnahme separat:** erst TileMap-Test starten, Screenshot/Video sowie `gles3-stdout.log` und `gles3-runtime.log` mit `TILE_CONTACT_OK`, `TILE_TEST_PASS`, `GODOT_RETURN=0`, `EGL_CLOSED` erfassen. Danach die Font-ZIP kopieren und **visuell** prüfen, dass alle fünf Godot-Labels samt Umlauten sichtbar sind. `FONT_TTF_LOADED` und `LABEL_TREE_READY` allein beweisen noch keine gerenderten Zeichen. Optional **X** für Textfarbe.
- Die beiden Testprojekte sind unabhängig: Tile-Kollision kann PASS sein, während der Font-Renderer FAIL ist. Keine Behauptungen zu Audio, Savegames, 3D, TextServer-Full, vollständigen TileMap-Funktionen oder allgemeinen Godot-Spielen.

## M10c – Native FreeType/TrueType integration (23 October 2026)

**Status: ✅ FreeType + Godot-Label auf physischer PS5 bestätigt (Screenshot, 23.10.2026, ca. 08:30 Uhr).** Native v0.1.4 `PPSA99847` lädt das externe `m10b-font-ui.pck` und stellt Text, Zahlen, fünf Labels, verschiedenfarbige Glyphen und `Ä Ö Ü ß` sichtbar dar. Quelle: vom Nutzer bereitgestelltes Foto/Screenshot `20261023_083016_00527039.png`. Ein einzelnes Bild ist kein Nachweis für die X-Tastenreaktion oder `GODOT_RETURN=0`/`EGL_CLOSED`; entsprechende Konsolenlogs wurden in diesem Turn nicht mitgeliefert. Installer-Veröffentlichung bleibt [GitHub v0.1.4](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gles3-canvas-v0.1.4), SHA256 `d068a20fdc3bdb3242568d17b363812cf398f3584b9a34db12f0474c7b116b8f`.

- **User bug report:** `bfpilot-download (23).tar` contains two M10b Font/UI sessions. Native runner successfully selects `/data/GodotPS5/games/m10b-font-ui.pck`, reads 118,204-byte TTF and logs `GODOT_PS5_M10B_FONT_TTF_LOADED`. Both sessions then log `GODOT_PS5_M10B_FONT_FAIL_GLYPH_A`, exit `GODOT_RETURN=93`, while `gles3-stderr.log` explicitly reports **`FreeType: Can't load dynamic font, engine is compiled without FreeType support!`**. This is a **native engine build regression**, not a missing PCK or bad TTF.
- **Independent TileMap result:** The same TAR contains a successful M10b TileMapLayer PS5 run: `GODOT_PS5_M10B_TILE_CONTACT_OK tilemap=RealTileMapPlatform normal=(0,-1) y=742.984375`, `GODOT_PS5_M10B_TILE_TEST_PASS tick=139`, `GODOT_RETURN=0`, `NORMAL_SHUTDOWN`, `EGL_CLOSED`. Mark M10b-a hardware-confirmed; keep M10b-b pending.
- **Fix:** `scripts/build-engine.sh` now supports the opt-in `GODOT_PS5_FREETYPE=1`, compiling original upstream Godot 4.7.2 `module_freetype_enabled=yes`, `builtin_freetype=yes`, retaining the lightweight `module_text_server_fb_enabled=yes`. Original `GODOT_PS5_PHYSICS2D=1` remains enabled. Baseline v0.1.3 is unchanged and available for regression fallback.
- **Native build:** [M10c FreeType PR #243](https://github.com/Yahballon/tmp_lap/pull/243) merged. Dedicated [native FreeType v0.1.4 Actions workflow](../../.github/workflows/build-godot-ps5-m10c-freetype-fonts.yml) host-tests the unchanged Font/UI PCK and must prove `libfreetype_builtin`, `libmodule_text_server_fb` and `libmodule_godot_physics_2d` in the full PS5 static archive manifest. **Upstream Godot 4.7.2 does NOT produce a separate `libmodule_freetype.a`:** the original check was corrected to verify the actual FreeType builtin archive, exported `FT_Init_FreeType` and generated `MODULE_FREETYPE_ENABLED`. Run [#39881296128](https://github.com/Yahballon/tmp_lap/actions/runs/39881296128) then successfully compiled, linked and signed a ~72.4 MB `eboot.bin`, but the job failed *only* its final metadata assertion, which still expected v0.1.3 `01.000.004`. The assertion was fixed to the v0.1.4 metadata `01.000.005` and the **trusted GitHub publisher subsequently released signed PPSA99847 v0.1.4**, as verified by the GitHub Releases API and `version.json` on `main`. An additional independent [PR #244](https://github.com/Yahballon/tmp_lap/pull/244) adds a metadata consistency regression and re-tests the native build. **Physical PS5 screenshot of correct rendered glyphs NOW PROVIDED (23 October 2026).** X action and exit logs remain unverified.
- **PS5 VISUAL ACCEPTANCE PASSED:** User screenshot `20261023_083016_00527039.png` independently shows actual native Godot rendering of five separate Labels with the bundled Press Start 2P TrueType font, correct palette, ASCII and umlauts `Ä Ö Ü ß`. **Still open for complete runtime acceptance:** verify X changes the title from cyan to pink, check `GODOT_PS5_M10B_FONT_METRICS_OK`, `GODOT_PS5_M10B_LABEL_TREE_READY`, `GODOT_PS5_M10B_FONT_TEST_FINISHED`, native `GODOT_RETURN=0` and `EGL_CLOSED` in the updated three `gles3-*.log` files. Do not extrapolate to all fonts, all Unicode scripts or all Godot UI components.
- Remaining known nonblocking errors: `res://project.binary` and global script cache diagnostics. Investigate separately from native FreeType.

## M11 – Audio + persistent savegames (23 October 2026)

**Status: 🟡 Both genuine Godot 4.7.2 PCKs pass Linux host acceptance; physical PS5 audio and save behavior unverified.** [GitHub Actions #39911102004](https://github.com/Yahballon/tmp_lap/actions/runs/39911102004) is fully **SUCCESS**; artifact `Godot-PS5-M11-Audio-Saves-HOST-VALIDATED-PS5-UNTESTED` (ID `12483290213`). Source, separate fixture folders and detailed user instructions: [`samples/M11_README.md`](samples/M11_README.md). Already user-tested `PPSA99847 v0.1.4` is **not changed**.

- **M11a audio:** `samples/m11-audio/` creates a real 44,100 Hz 16-bit mono `AudioStreamWAV` (529,200 bytes), uses original Godot `AudioStreamPlayer` with six distinctive notes, X replay and moving color bars. Desktop console logs `GODOT_PS5_M11_AUDIO_PCM_READY`, `GODOT_PS5_M11_AUDIO_PLAYER_STARTED`, `GODOT_PS5_M11_AUDIO_HOST_API_PASS`, and deliberately `GODOT_PS5_M11_AUDIO_HARDWARE_AUDIBILITY_UNCONFIRMED`. **Do not claim PS5 audio from playing=true or visual motion.** The PS5 platform currently does not register a dedicated native audio driver; if silent, implement/register a real PS5 audio output backend after examining logs.
- **M11b saves:** `samples/m11-saves/` uses the actual Godot `FileAccess` API to write, flush and reopen a versioned+checksummed `user://m11-save-v1.txt`. The first **fresh host process** logged `SAVE_FIRST_LAUNCH_PASS new=1` and `SAVE_VERIFY_READBACK_OK`. The **second independent host process** logged `SAVE_PERSIST_OK previous=1` and `SAVE_RESTART_PERSISTENCE_PASS old=1 new=2`. **Do not count initial write/readback as persistence.** Existing PS5 `FileAccessPS5` uses native kernel I/O for reads but delegates writes to `FileAccessUnix`; PS5 success is untested, and `SAVE_WRITE_UNAVAILABLE` would require native kernel-backed write support.
- **Test ZIPs**: `GodotPS5-M11a-AUDIO-TEST.zip` and `GodotPS5-M11b-SAVES-TEST.zip`, both generated and CRC/SHA verified. Extract ONE and copy `GodotPS5/` contents to `/data/GodotPS5/`, which adds a PCK and changes only `launch.txt`. Run existing `PPSA99847 v0.1.4`. Previous PCKs remain installed.
- **M11a PS5 hardware gate:** tester must **hear** six ascending/descending tones from TV/headphones, optionally X to replay; collect `gles3-stdout.log`/`gles3-stderr.log`/`gles3-runtime.log` to distinguish actual output from dummy driver. No hardware status assigned until user confirms audibility.
- **M11b PS5 hardware gate:** start `m11-saves.pck` **twice with a complete PS5 homebrew exit and relaunch between runs**, without changing `launch.txt`. First blue/cyan screen plus `GODOT_PS5_M11_SAVE_FIRST_LAUNCH_PASS`, then green screen plus `GODOT_PS5_M11_SAVE_RESTART_PERSISTENCE_PASS old=1 new=2` (or incrementing previous counter if already run). Require native `GODOT_RETURN=0` and `EGL_CLOSED` separately for both sessions; keep other user saves untouched. A red test/fail marker indicates a real missing platform capability.

## M11b2 PS5 save persistence ACCEPTED (23 October 2026)

The user confirmed saves work and provided `bfpilot-download (25)(1).tar`, which **independently contains three successful M11b2 restarts** and a live save file. The direct-read workaround bypasses the broken libc `file_exists` metadata query; on-console stdout proves `DIRECT_READ_OK previous=1`, `RESTART_PERSISTENCE_PASS old=1 new=2`, then `previous=2`/`old=2 new=3`, finally `previous=3`/`old=3 new=4`. The TAR's stored `userdata/GodotPS5M11Saves/m11-save-v1.txt` is `GODOT_PS5_M11_SAVE_V1|4|999\n`, which validates the final counter/checksum. At least two complete M11b2 sessions in `gles3-runtime.log` have `GODOT_RETURN=0`, `NORMAL_SHUTDOWN`, `EGL_CLOSED`. **Mark M11b2 physical hardware gate PASSED**. This fixture demonstrates Godot `user://` persistence by direct file opening; it does **not** make Godot's generic `FileAccessUnix.file_exists` reliable on PS5 and does not prove every filesystem API.

**M11a audio remains NOT WORKING** on the user's PS5. The active implementation issue is [#247](https://github.com/Yahballon/tmp_lap/issues/247). No new native audio driver build/release has been verified; do not tell the user the old audio PCK can fix muted sound without a FreeBSD/PS5 AudioOut backend.

## M11 PS5 diagnostics and M11b2 save recovery (23 October 2026)

**PS5 evidence from user TAR `bfpilot-download (24).tar`:**

- **Tracking:** [M11c native AudioOut driver issue #247](https://github.com/Yahballon/tmp_lap/issues/247) records the confirmed silent PS5 hardware result, native integration scope and hearing-based acceptance.
- M11a `m11-audio.pck` launched correctly with 529,200 bytes of actual PCM; `AudioStreamPlayer` started; console runtime `GODOT_RETURN=0`, clean EGL shutdown. User reports **SILENCE** (no audible tones). Source inspection confirms `OS_PS5` does not register a native `AudioDriver`. **M11a audio hardware acceptance FAIL**. A proper, separately tested PS5 AudioOut bridge (e.g. `libSceAudioOut`) must be implemented rather than treating `playing=true` as audio success. Reference [PS5 SDK audio beep probe](https://github.com/Rufidj/PS5_DEV_HOMEBREW/blob/main/examples/ps5_sdk/audio_beep.c) demonstrates native AudioOut entry points but is **not an integrated Godot audio backend**.
- M11b `m11-saves.pck` launched **twice**. Each session logged `GODOT_PS5_M11_SAVE_WRITE_OK current=1`, `GODOT_PS5_M11_SAVE_VERIFY_READBACK_OK`, `GODOT_PS5_M11_SAVE_FIRST_LAUNCH_PASS new=1`, `GODOT_RETURN=0`. Actual TAR includes valid `userdata/GodotPS5M11Saves/m11-save-v1.txt` content `GODOT_PS5_M11_SAVE_V1|1|960\n`. This rules out a general filesystem write failure. Upstream `FileAccessUnix::file_exists()` calls `stat` and `access` on PS5 `user://` paths, where POSIX metadata probing is unreliable; `FileAccessUnix` was registered for ACCESS_USERDATA and `FileAccessPS5` only for RESOURCES/FILESYSTEM. **The current evidence supports a read/existence-detection issue; do not state persistent restore is proven yet.**
- **M11b2 fixed external PCK:** [PR #246](https://github.com/Yahballon/tmp_lap/pull/246). Same private `user://m11-save-v1.txt` name and checksum, no deletion. It attempts a real `FileAccess.open(..., READ)` **before any write**, tolerating only `ERR_FILE_NOT_FOUND` as the fresh first-launch case. Unexpected read/corrupt errors halt without overwriting the existing save. A real FreeType `Label` display clearly shows FIRST SAVE CREATED (cyan), SAVE RESTORED with PREVIOUS/NEW counts (green), or a visible red error. Successful official Godot host acceptance [#39913555804](https://github.com/Yahballon/tmp_lap/actions/runs/39913555804) has **two different processes**, with exact markers `GODOT_PS5_M11B2_FIRST_LAUNCH_PASS new=1` then `GODOT_PS5_M11B2_DIRECT_READ_OK previous=1`, `GODOT_PS5_M11B2_RESTART_PERSISTENCE_PASS old=1 new=2`, `GODOT_PS5_M11B2_VISIBLE_STATUS_READY phase=2`.
- **Installable PS5 ZIP:** `GodotPS5-M11b2-SAVES-VISIBLE-FIX.zip`, real PCK SHA256 `8c914bbbb9f5f0c6deb5477e9e6f173a558dd1e9420bb52524eed3de4022e3bf`. Copy its `GodotPS5/` contents to `/data/GodotPS5/`, run the already confirmed `PPSA99847 v0.1.4`. It changes only the selected `launch.txt`, preserves all previous PCKs and saved data. Because a valid save with count 1 already exists, **first M11b2 PS5 launch should display GREEN SAVE RESTORED PREVIOUS 1 NEW 2** if direct read truly works on console. Collect screenshot plus all three `gles3-*.log` files; otherwise patch native ACCESS_USERDATA. No PS5 persistent success claim until that acceptance.

## M11c – Native AudioOut PS5 candidate (23 October 2026)

**Status: in development; NO physical PS5 audible sound confirmed.**

- User's M11a hardware logs showed actual AudioStreamPlayer PCM but NO sound. Root issue: OS_PS5 registered no real AudioDriver. Tracked in [issue #247](https://github.com/Yahballon/tmp_lap/issues/247).
- [PR #248](https://github.com/Yahballon/tmp_lap/pull/248) adds an opt-in AudioDriverPS5 derived from the genuine Godot 4.7.2 AudioDriver. It registers with AudioDriverManager prior to Main::setup. A dedicated thread invokes audio_server_process for 256 frames at 48,000 Hz stereo, converts the fixed-point 32-bit stream to signed 16-bit interleaved PCM, and passes buffers to the PS5 AudioOut kernel via its public SDK import stub. Blocking kernel I/O occurs outside the audio mix Mutex.
- Separate [native v0.1.5 workflow](../../.github/workflows/build-godot-ps5-m11c-native-audioout.yml) retains PhysicsServer2D, GLES3, FreeType and the existing PCK loader; it checks the public libSceAudioOut.so stub, compiles AudioDriverPS5, and must link and sign a PPSA99847 installer with contentVersion 01.000.006. The old v0.1.4 title remains a rollback option.
- **Physical PS5 audio acceptance is mandatory:** select m11-audio.pck, install a signed v0.1.5 candidate only AFTER successful CI, listen for six notes and press X to replay. Capture gles3-stdout.log, gles3-stderr.log, gles3-runtime.log. Require AUDIOOUT_DRIVER_REGISTERED, successful nonnegative AudioOut handle, actual OUTPUT_OK blocks, native clean exit and **user-audible sound**. Driver initialization or AudioStreamPlayer.playing alone does NOT establish working audio.
- [Implementation notes](M11C_AUDIOOUT.md) and ABI reference link to Rufidj PS5 audio probes. No Sony .sprx binary or fake playback is shipped.
## M11d PS5 native audio hardware ACCEPTED (23 October 2026)

**Status: ✅ real PS5 heard audio and successful X replay, verified against user-supplied `bfpilot-download (27).tar`.** The user installed signed PPSA99847 **v0.1.6** and explicitly confirmed audible six-note Godot playback plus repeated playback from DualSense X. This is genuine upstream Godot 4.7.2 `AudioStreamPlayer` flowing through the native `AudioDriverPS5` into `libSceAudioOut`, **not** an API-only/dummy-driver confirmation.

Only consider the **last M11d session** in the cumulative console logs, as older v0.1.5 sessions still contain dummy fallbacks, malformed `%llu` error formatting and AudioOut thread misclassification. The last v0.1.6 stdout segment confirms:

```text
GODOT_PS5_M11C_AUDIOOUT_INIT rc=0
GODOT_PS5_M11C_AUDIOOUT_OPEN handle=536870912
GODOT_PS5_M11D_AUDIOOUT_THREAD_STARTED
GODOT_PS5_M11D_AUDIOOUT_OUTPUT_OK blocks=1
GODOT_PS5_M11C_AUDIOOUT_READY rate=48000 channels=2 frames=256
GODOT_PS5_M11C_AUDIOOUT_START
GODOT_PS5_M11_AUDIO_MIX_RATE=48000.0
GODOT_PS5_M11_AUDIO_PCM_READY bytes=529200 sample_rate=44100
GODOT_PS5_M11_AUDIO_PLAYER_STARTED
GODOT_PS5_M11D_AUDIOOUT_OUTPUT_OK blocks=2048
GODOT_PS5_M11_AUDIO_X_REPLAY  # occurs nine times in final session
GODOT_PS5_M11D_AUDIOOUT_CLOSE rc=0 blocks=2831 errors=0
```

Its matching `gles3-runtime.log` shows the selected external `/data/GodotPS5/games/m11-audio.pck`, `GODOT_RETURN=0`, `NORMAL_SHUTDOWN`, `EGL_CLOSED`. **No M11d native AudioOut output-error markers and no dummy driver fallback in this session.** The latest stderr retains nonfatal `Could not load global script cache` and two leaked ObjectDB instances at exit; these do **not** block audible sound and should be investigated as separate compatibility/cleanup issues.

- **Acceptance met:** audibility, X repeat, successful nonnegative AudioOut handle, 2,831 output blocks, 0 AudioOut output failures and graceful shutdown.
- **Preserved:** native GLES3/Canvas2D, 2D Physics, TileMapLayer, FreeType labels and Savegames were previously hardware-confirmed; no inference that every previous feature was re-tested in the *audio* session.
- **Next separate gates:** longer running audio/stop-resume, different sample formats and real game audio, and optional nonfatal script-cache cleanup.
- **Distribution VERIFIED:** signed CI [#39924377575](https://github.com/Yahballon/tmp_lap/actions/runs/39924377575), merged [PR #249](https://github.com/Yahballon/tmp_lap/pull/249); **public [v0.1.6 GitHub prerelease](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gles3-canvas-v0.1.6) and TESTBUILD main `version.json` catalog now both confirmed**. Published 2026-10-23 08:48:34 UTC, `PPSA99847.zip` (22,657,378 bytes), SHA256 `e15323c7736eaeead0bad1158de33dd1a7f439e6510928b6661d34219ca96026`. This public-release ZIP may differ bytewise from the initially downloaded raw Actions artifact; keep separate checksums.

## M11d – Repaired real PS5 AudioOut Thread lifetime (23 October 2026)

- **Hardware log evidence:** `bfpilot-download (26).tar` contains two v0.1.5 audio boot attempts. Both report `GODOT_PS5_M11C_AUDIOOUT_INIT rc=0`, `AUDIOOUT_OPEN handle=536870912`, then `AUDIOOUT_THREAD_START_FAIL`. STDERR explicitly says `All audio drivers failed, falling back to the dummy driver`; user hears nothing. Secondary problem: `vformat` rejects `%llu` and hides follow-up PS5 AudioOut return codes. Both attempts exit cleanly with `GODOT_RETURN=0` despite dummy audio.
- **Verified upstream contract:** Official Godot **4.7.2** `core/os/thread.cpp` defines `Thread::ID Thread::start(...)` and returns an allocated nonzero ID on success; `bool Thread::is_started() const` checks against `UNASSIGNED_ID`. The v0.1.5 implementation incorrectly compared the returned ID with `OK=0`, thus always closing a perfectly valid handle and entering a race with its actually created AudioOut worker. **This—not AudioOutOpen or PCM format—is the identified primary root cause.**
- **Existing working repo references:** `Yahballon/PS5NESX` (`nes/src/shelf_runtime.cpp`) and `Yahballon/PS5GBCX` (`gbc/src/shelf_runtime.cpp`) use `sceAudioOutOpen(255,0,0,256,48000,1)` and independent audio threads. Their PS5 AudioOut API configuration matches the one successfully opened in the Godot log. Do not randomly change the port format.
- **Fix in progress:** `fix/godot-ps5-m11d-audio-thread-v016` changes `thread.start(...); if (!thread.is_started())`, retains valid handle, permits the true Godot mixer to feed PS5 stereo PCM, replaces all invalid `%llu` diagnostic formatting, and adds `tests/test_m11d_audio_thread_fix.py`. Dedicated signed experimental `PPSA99847 v0.1.6` build workflow checks `contentVersion=01.000.007` and preserves all known-good Physics2D/GLES3/FreeType.
- **Acceptance still open:** v0.1.6 signed native build CONFIRMED in Actions #39924377575; STILL REQUIRE PS5 screenshot/log with `GODOT_PS5_M11D_AUDIOOUT_THREAD_STARTED`, `GODOT_PS5_M11C_AUDIOOUT_READY`, `GODOT_PS5_M11D_AUDIOOUT_OUTPUT_OK`, no dummy fallback, `GODOT_PS5_M11_AUDIO_MIX_RATE=48000.0` expected when hardware driver active, and **audible six notes**. Only then confirm M11d audio on real PS5. Keep v0.1.4 installer as rollback.

## M12 – Real third-party Godot platformer compatibility (23 October 2026)

**Status: ✅ host build/real Godot scene boot; ⏳ physical PS5 hardware acceptance still OPEN.**

- **Asset:** [Godot Asset Library #2201](https://godotengine.org/asset-library/asset/2201) "2D Platformer – Starter Kit 1.1.1" by G2P Studios/AdilDevStuff, **MIT licensed**, upstream GitHub commit `a48fc994cbcb168be472df84f2e13b55d2a2792f`. Original Kenney sprite art and Gdfxr effects credited in README. Do not substitute new lookalike sprites or a fake smoke scene.
- **Full original gameplay:** 2 levels, real `CharacterBody2D`/TileMapLayer ground+traps, coins/score, Camera2D, level transition, original `.wav` sounds and TrueType custom fonts, particles and sprite animations.
- **Small PS5 adaptation:** an autoload `PS5Controls.gd` maps existing Left/Right/Jump actions to **left stick/D-Pad/Cross**, a `gl_compatibility` renderer setting replaces Forward Plus, and a desktop-only tutorial label is updated. Original platformer gameplay scripts and asset files remain unchanged.
- **Original Godot 4.7.2 CI [#39930320591](https://github.com/Yahballon/tmp_lap/actions/runs/39930320591) SUCCEEDED:** imported upstream textures/fonts/WAV, packed **92** files, `GODOT_PS5_M12_INPUT_READY`, `SCENE_READY Level_01`, `PLAYER_FOUND position=(150,318)`, `FRAME tick=180 player=(150,447.959) grounded=true`, no script errors, produced data-only PS5 installer ZIP.
- **User ZIP:** `GodotPS5-M12-Platformer-Asset2201-PS5-TEST.zip` (553 KB), contains `GodotPS5/games/m12-platformer-asset2201.pck`, `launch.txt` selecting it, original MIT license, instructions, checksum. PCK SHA256 `df286a34ac6df63950a7b73cd394dc5ee9975c1251dac53bcab940eab3a240ac`. No native PS5 eboot modification.
- **PS5 next acceptance:** user copies ZIP's GodotPS5/ contents into /data/GodotPS5/, starts existing `PPSA99847 v0.1.6`, checks actual two-level gameplay, graphics imported tiles, left-stick/D-Pad movement and Cross jump, coins/score, audible original jump/coin effects, level changes and clean shutdown. Request screenshot/video and `gles3-stdout.log`, `gles3-stderr.log`, `gles3-runtime.log`. **Desktop scene boot does NOT establish PS5 imported texture or audio compatibility.**
- **Source guide:** [`samples/m12-platformer-2201/M12_README.md`](samples/m12-platformer-2201/M12_README.md). [PR #250](https://github.com/Yahballon/tmp_lap/pull/250).

## M12b – Third-party platformer image decoder fix (2026-10-23)

Actual PS5 TAR bfpilot-download (28).tar proves the initial M12 platformer cannot load imported lossless CompressedTexture2D assets. The native PS5 engine opens the PCK and boots GLES3 but scene/resources/compressed_texture.cpp:343 reports null/empty Image for imported sprites and tilesheets. Original Level_01 fails to load, GODOT_RETURN=1. This is not a controller or scene-switch issue.

Godot 4.7.2 imported compress/mode=0 textures embed PNG or WebP and require Image::png_unpacker or Image::webp_unpacker, unavailable or nonworking in this PS5 engine. Upstream compress/mode=3 (VRAM Uncompressed) writes raw CompressedTexture2D::DATA_FORMAT_IMAGE, bypassing both image unpackers. M12b rebuilds all eight upstream PNG assets plus one SVG icon with mode 3 and checks every resulting GST2 .ctex data-format field equals 0 at byte offset 36. Original MIT game logic is unchanged.

The optional visible PS5Boot.tscn shows individual texture/font/player/Level_01 load progress and errors; original heavy audio/scene transition autoloads are replaced with lightweight API-compatible lazy versions for diagnosis. Gameplay remains the real third-party project.

Official Godot 4.7.2 GitHub CI #39933593514 PASSED: 9 raw images validated, 99 project/import files packed, actual player and grounded floor at tick 180, all original WAV effects load, no script errors. New distinct data-only package GodotPS5-M12b-Platformer-SplashFix-PS5-TEST.zip (625858 bytes) contains m12b-platformer-asset2201.pck (13271676 bytes), MIT original license, launch.txt and checksum. PCK SHA256 d2b62dd7c26dc77f8d187c05973e8aaba0da4335e73c2c6e9cec1ec121f4f7b7. The installed PPSA99847 v0.1.6 engine is unchanged.

NEXT: Copy the ZIP GodotPS5/ contents into /data/GodotPS5/, preserving old PCKs and saves; start Godot PS5 v0.1.6. Confirm staged loader proceeds to the *visible original game*, test controls, original sound, coin HUD and level change. Send screenshot and gles3-stdout.log, gles3-stderr.log, gles3-runtime.log. PS5 M12b success must not be claimed based only on host tests.

Source: [PR #251](https://github.com/Yahballon/tmp_lap/pull/251). Later engine feature: build native PNG/WebP unpackers for broad Godot lossless-texture compatibility, independent of this PCK-level workaround.
## M12c – optimize original PS5 Platformer boot (2026-10-23)

**User PS5 result:** M12b now loads and becomes controllable, but takes approximately 30–60 seconds. A new, timestamped PS5 performance TAR was not yet accessible in this turn; do not guess which operation dominates. The older bfpilot-download (28).tar predates the M12b success and only documents missing PNG/WebP decoders in original M12.

**Exact old PCK binary analysis:** M12b had 99 files and 13,271,676 bytes. The now-disabled startup splash `.ctex` consumed 5.93 MiB and unused `Icon.png` raw `.ctex` consumed 3.34 MiB. Neither is referenced by original gameplay scenes. The SVG game icon `.ctex` was also unused. Together these account for about 70% of old package bytes. The previous M12b diagnostic boot additionally probed textures/font/player/scene separately before loading the original level.

**M12c code:** Independent `prepare_project_fast.py` / `pack_m12_fast.gd` / `package_platformer_fast.py` generate a different `m12c-platformer-asset2201.pck`, leaving proven M12b untouched. Six original scene-referenced textures retain PS5-compatible Godot raw DATA_FORMAT_IMAGE import. Unused icon/splash source and imports are omitted from game PCK. `PS5BootFast.gd` directly loads original Level_01 ONCE and logs LEVEL_LOAD_BEGIN / LEVEL_LOAD_DONE duration_ms / SCENE_SWITCH_REQUESTED. `PS5ControlsFast.gd` logs PLAYABLE_SCENE_READY total_ms. `AudioManagerFast.gd` logs AUDIO_LOAD_DONE duration_ms. Original game mechanics, physics, WAV and MIT license retained.

**Host validation:** [GitHub Actions #39936285140](https://github.com/Yahballon/tmp_lap/actions/runs/39936285140) success: six gameplay `.ctex` with raw payload, 87 files, PCK 3,323,440 bytes (25% of old size), original game Level_01 starts, grounded player, WAV audio; desktop load scene 8 ms and boot-to-player 17 ms. These numbers are NOT PS5 measurements.

**Download:** `GodotPS5-M12c-Platformer-FAST-PS5-TEST.zip` (347,780 bytes), contains separate game PCK and launch.txt, retains M12b and savegames, requires only existing PPSA99847 v0.1.6. PCK SHA256 a44b5c60b613e770ffd1b7a277c30e410310a58eade3cf0935c89deff80ab551.

**PS5 acceptance still open:** user should compare actual seconds to gameplay vs old 30–60s, capture current gles3-stdout.log and gles3-runtime.log, check markers M12C_LEVEL_LOAD_DONE, M12C_PLAYABLE_SCENE_READY, M12C_AUDIO_LOAD_DONE, confirm actual sprites, DualSense controls, coins and sound. Do not mark startup optimization hardware successful without user timings.

## M13 – Diagnose real PS5 133-ms/Gallium frame stalls before attempting cache or RAM work (2026-10-23)

New physical PS5 user TAR `bfpilot-download (31).tar` proves M12d scene initialization and original Level_02 work: Level_01 player ready after 5.712s from BootFast, after 2.803s of level resource load and ~1.228s of scene construction. Original WAV load 1.584s. Both original TileMap layers per level confirm navigation disabled while collision is still enabled. This eliminates the earlier 22.523-second M12c scene-tree gap, but **severe repeated 133-ms frames (≈7.5 FPS) and individual ~150-ms hitches remain**, even with the player stationary.

41+ five-second frame statistic windows show intermittent normal ~60fps and isolated 1–6fps slices; actual last-run metrics: 43 summaries, 38 explicitly logged >=80ms hitches, 13+ native Gallium shader compile messages (mostly initial game frame). One later shader variant compile is close to a 108-ms hitch, but shader compile is NOT yet the confirmed cause of all 133-ms periods. The archive's cumulative stderr holds historical nav-map errors and MUST NOT be interpreted as current M12d failures; the newest M12d scene logs show both ground/trap navigation disabled.

**M13 source** (`native/gles3_canvas_main.cpp`) is an independent experimental native build based on the proven v0.1.6 Godot 4.7.2 + Physics2D + FreeType + libSceAudioOut. It uses `CLOCK_MONOTONIC` to time CPU-side interval since last completed frame separately from time blocked inside the REAL PS5 EGL/Gallium `display.swap()`. Logs limited to 8 spikes per 5s plus 5-second stats, no per-frame log spam, glFinish, glReadPixels, or forced GPU synchronization. See [M13_PERFORMANCE.md](M13_PERFORMANCE.md) and [PR #254](https://github.com/Yahballon/tmp_lap/pull/254). The **full native signed v0.1.7 build passed** [Actions #39945288503](https://github.com/Yahballon/tmp_lap/actions/runs/39945288503), with `contentVersion=01.000.008`; independently verified `PPSA99847.zip` has correct title ID, 72,399,248-byte signed PS5 eboot, and CRC-clean resources. **Public experimental [v0.1.7 release](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gles3-canvas-v0.1.7) and main TESTBUILD catalog have been independently confirmed**, with publisher run #39946767134 successful. Official release ZIP SHA256 `14fbeb713ef6f6cf7dc50c214eddfe0fd0e8bfe6961907c9b956f099be272705`, 22,657,871 bytes. Keep physically tested v0.1.6 available as rollback, because **native M13 perf logging and lag reduction have not yet been tested on console**.

**Hardware next:** install only verified signed v0.1.7 experimental test; leave `launch.txt=m12d-platformer-asset2201.pck`; reproduce a still-idle stall and active Level_02 stutters, and capture current `gles3-stdout.log` and `gles3-runtime.log`. Compare `M12D_FRAME_HITCH` and native `M13_FRAME_SPIKE cpu_before_swap_ms / egl_swap_ms`, plus Gallium shader compiles. Only then choose native driver/swap/shader cache mitigation vs Godot scene/physics/IO. Whole PCK is already ~3.3MB, and RAM preloading would not explain stalls in the idle state without evidence. No performance improvement claimed yet.

## Roadmap: Was als Nächstes zu tun ist

### P0 – M13 hardware-native CPU/EGL frame timings then targeted Gallium/renderer performance fix

- [x] `PPSA99847 v0.1.2` auf realer PS5 starten: vom Nutzer bestätigt.
- [x] Pong-Bildschirm mit zwei Schlägern, bewegtem Ball, Spielfeld und Punktestand nachweisen: Video `20261022_234930_00248487(1).webm` bestätigt.
- [ ] Restliche Pong-Einzeltests bei Gelegenheit mit `/data/GodotPS5/gles3-stdout.log`, `gles3-runtime.log`, `gles3-stderr.log` erfassen: X-Aufschlag, Analog/D-Pad, Kollision/Punkte, Kreis-Reset, Options-Exit, Framezeiten und `GODOT_RETURN=0` / `EGL_CLOSED`. **Nicht mit dem jetzt vorliegenden kurzen Video gleichsetzen.**
- [x] M8c-GitHub Actions erfolgreich: Original-Godot-4.7.2-PCK erzeugt und auf Linux/headless vollständig durch zwei Szenen getestet. Run `39866584380`; PCK 4,828 Bytes, PCK format 4, engine 4.7, SHA-256 `137f4c5722e385c04c4f36a84fcd8548e5038a348f68d91ca2c3310c21527591` verified from downloaded Actions artifact.
- [x] **M8c physical PS5 test**: user reports the externally selected PCK works, both scenes switch correctly and X changes their colors, without rebuilding `PPSA99847 v0.1.2`.
- [ ] Supplement M8c with `PACK_SOURCE=CONFIG`, `GODOT_PS5_EXTERNAL_*` markers and `NORMAL_SHUTDOWN` console logs if further diagnostic evidence is needed; no logs uploaded for this run.
- [x] **M9a host acceptance:** standalone `CharacterBody2D` + `StaticBody2D` + `CollisionShape2D` real Godot 4.7.2 collision test built, executed, signed-off by CI run `39869677215`, and ready-to-copy external PCK produced.
- [x] **M9a PS5 hardware acceptance:** Die native v0.1.3 besteht den realen Kollisionstest zweimal mit `REAL_COLLISION_OK`, `TEST_PASS`, Exit-Code 0 und vollständigem EGL-Shutdown; mit v0.1.2 war der Dummy-Server das bestätigte Hindernis.
- [x] **M9b:** Original GodotPhysics2D-Modul in PS5-Engine integriert; separater Build 39872101079 grün; physische PS5-Kollision in zwei Sessions bestätigt.
- [x] **M10a host:** official Godot 4.7.2 PhysicsServer2D RigidBody2D + Area2D PCK complete, real collision/trigger markers and rest-state verified; CI 39876290256 green and install ZIP available.
- [x] **M10a PS5:** zwei erfolgreiche Hardware-Sessions mit realer Schwerkraft, Area-Eintritt/-Austritt, RigidBody-Bodenkontakt, stillstehendem Körper und sauberem Exit aus `bfpilot-download (22).tar`.
- [x] **M10b Host CI:** zwei unabhängige Godot-4.7.2-PCKs mit echten TileMapLayer-Kollisionen und FontFile/Label-Objekten erzeugt, ausgeführt und strukturell validiert. GitHub Actions 39878279649 vollständig grün.
- [x] **M10b-a PS5:** `GODOT_PS5_M10B_TILE_CONTACT_OK` und `...TILE_TEST_PASS` plus Exit-Code 0 und sauberer EGL-Shutdown in `bfpilot-download (23).tar` bestätigt.
- [x] **M10b-b PS5 / M10c Font-Pfad:** v0.1.4 mit Original-FreeType auf echter PS5 visualisiert; fünf Labels inklusive `Ä Ö Ü ß` im Nutzer-Screenshot `20261023_083016_00527039.png` sichtbar.
- [ ] **M10c Detailabnahme:** X verändert Titel-Farbe/Text und danach optional stdout-/runtime-Logs für FONT_TEST_FINISHED, GODOT_RETURN=0, EGL_CLOSED nachreichen.
- [x] **M11 host CI:** echte AudioStreamWAV/AudioStreamPlayer-Szene plus originale FileAccess-Save-Szene, inklusive erfolgreicher Persistenz über zwei getrennte Godot-Prozesse; Actions #39911102004 grün.
- [x] **M11a/M11d native AudioOut:** ursprünglich stumm unter v0.1.4/0.1.5; **jetzt unter v0.1.6 auf PS5 hörbar bestätigt**, nativer AudioDriverPS5 erfolgreich geöffnet, Ausgangspuffer fehlerfrei und X-Replay funktionsfähig.
- [x] **M11c implementation:** Godot AudioDriverPS5 source + SDK AudioOut binding + standalone v0.1.5 CI workflow committed; static host tests pass.
- [x] **M11c/M11d PS5 AudioOut final:** v0.1.5-Thread-Fehler als Ursache nachgewiesen, mit v0.1.6 behoben und auf Hardware durch hörbare Audioausgabe samt erfolgreichem Exit bestätigt.
- [x] **M11d root-cause analysis:** Real v0.1.5 PS5 log inspected; AudioOut init/open succeeded; upstream Godot 4.7.2 Thread::start ID-vs-Error mismatch and unsupported logger fixed in source.
- [x] **M11d signierter Build:** Cross-CI 39924377575 erfolgreich; PPSA99847 v0.1.6 mit m11-audio.pck validiert, PR #249 gemergt.
- [x] **M11d PS5-Hardware-Audio:** v0.1.6, Nutzer bestätigt hörbare Töne und DualSense-X-Replays; letzter Lauf in `bfpilot-download (27).tar` zeigt 2.831 erfolgreiche AudioOut-Puffer, 0 Ausgabefehler, 9 X-Replays, `GODOT_RETURN=0`, `EGL_CLOSED` und `NORMAL_SHUTDOWN`.
- [x] **M12 third-party host:** pinned MIT upstream asset #2201, 92-file genuine Godot 4.7.2 imported PCK, Level 1 player floor collision and output ZIP, CI #39930320591 passed.
- [x] **M12 original console failure:** user screenshot and TAR #28 prove unsupported PNG/WebP .ctex, Level_01 load fails.
- [x] **M12b host fix:** 9 raw data-format-0 textures, 99-file PCK, staged loader and original Level_01/WAV host pass in Actions #39933593514.
- [x] **M12b first real console gameplay:** user confirms Level_01 loads and becomes controllable, but 30–60 s latency; other compatibility features still open.
- [x] **M12c compact PCK host:** 75% smaller, original Level_01/physics/WAV and timing instrumentation validated in Actions #39936285140.
- [ ] **M12c actual console speed:** measure cold boot and M12C playable/scene/audio duration_ms markers, check coins, jump, audio and Level_02.
- [x] **M11b original PS5 diagnostic:** native file WRITE+immediate READBACK passed and a real file is preserved; existing file NOT recognized upon restart.
- [x] **M11b2 host:** direct-open save recovery and visible status, two standalone Godot 4.7.2 processes PASS, Actions #39913555804.
- [x] **M11b2 PS5 hardware:** Nutzer-TAR `bfpilot-download (25)(1).tar` bestätigt reale bestehende Save-Leseöffnung und persistente Zählerfolge 1→2→3→4 auf physischer PS5; mindestens zwei saubere App-Exits, tatsächlicher Save-Inhalt validiert.

### P1 – Echte eigene Godot-4-PCKs laden

- [ ] Ein kleines selbst erstelltes **Godot 4.7.2**-Projekt als `.pck` testen, ohne nativen Neu-Build.
- [ ] `/data/GodotPS5/games/MyGame.pck` mit `/data/GodotPS5/launch.txt` auswählen; alternativ ausdrücklich freigegebene USB-Pfade.
- [ ] Auswahl im Log `PACK_SOURCE=CONFIG` und Start einer **fremden** `main.tscn` auf PS5 bestätigen.
- [ ] Ungültige PCK, fehlende Assets, Szenenwechsel, Neustart und Rückfall aufs interne Test-PCK prüfen.
- [ ] Mehrere echte Open-Source-Demos sukzessive testen; **nicht** jede Godot-4-Datei als automatisch kompatibel bezeichnen.

### P2 – Fehlende Grundlagen zum echten Spielen

- [ ] **2D-Physik:** Godots echten `PhysicsServer2D` anbinden; `CharacterBody2D`, `CollisionShape2D`, Kollisionen und TileMaps auf PS5 nachweisen.
- [ ] **Text/Fonts:** FreeType und TextServer-Build reparieren; `Label`, Umlaute/Unicode, UI-Schrift und dynamische Fonts testen. (Im alten Scene Bridge v0.1.0 verursachte ein Label den schwarzen Bildschirm.)
- [ ] **Audio:** einen PS5-Audiotreiber mit PCM-Playback, niedriger Latenz und Godot-`AudioStreamPlayer` testen.
- [ ] **Eingaben:** Achsen/Trigger, mehrere Controller, Controller-Trennung/-Wiederverbindung, D-Pad und geringe Verzögerung getrennt bestätigen.
- [ ] **Dateisystem/Saves:** `user://`, Schreibrechte, Speichern/Laden nach Neustart, externes PCK mit Ressourcen und unterschiedliche USB-Mounts validieren.
- [ ] **Lebenszyklus:** mehrfacher Start/Exit ohne Hänger, sichere GL/EGL-Zerstörung, Logs, Fehlerdialoge und Absturzdiagnose.

### P3 – Kompatibilität, Leistung und Distribution

- [ ] Rendering-Features erweitern: Canvas2D-Shader, Viewports, UI-Controls, Animationen, Bildformate, Transparenz und Performance unter Last.
- [ ] **3D** getrennt evaluieren; mit einer einfachen `MeshInstance3D`-Szene beginnen. Kein pauschaler Vulkan- oder 3D-Support ohne Hardwaretest.
- [ ] Eingabe-Latenz, Framezeiten, GL-Shader-Cache, RAM/VRAM-Verbrauch und längere Sessions messen.
- [ ] Mehrere exportierte Open-Source-Godot-Spiele mit definierter Kompatibilitätsmatrix prüfen.
- [ ] **Lizenz/Release-Audit:** Original-Godot MIT; PS5-GPU-Glüe/DevBridge GPL-3.0-or-later; Herkunft und Lizenz des inoffiziellen OpenGL-SDK-Mirrors einschließlich vollständiger korrespondierender Quellen und Notices prüfen.
- [ ] Dokumentation, Screenshots, Installationsanleitung, eindeutige Releases und automatische TESTBUILD-Katalogpflege vervollständigen.

## Wann gilt der Godot-PS5-Port als „spielbar“?

**Nicht nur ein grüner GitHub Actions Build.** Für den ersten **spielbaren 2D-Port** müssen auf echter PS5 mindestens ein vollständiges Godot-Spiel (Pong zählt als erste interne Referenz), reale Controllersteuerung, Szene/Renderer, reproduzierbare Frameausgabe und sauberer Exit demonstriert sein. Für einen **breiter nutzbaren Godot-4-2D-Port** kommen externe PCKs, Physik, Fonts/UI, Audio und Savegames hinzu. **3D und Vulkan** sind danach eigenständige Meilensteine.

## Technische Ankerpunkte

- **Godot-Plattform:** [`engine/platform/ps5/`](engine/platform/ps5/), insbesondere `os_ps5.cpp`, `display_server_ps5.cpp`, `pad_ps5.cpp`, `detect.py`.
- **Grafik-Einstieg:** [`native/gles3_canvas_main.cpp`](native/gles3_canvas_main.cpp) – EGL/Swap-Wrapper; **keine eigene Sprite-Rasterisierung**.
- **Godot-Testprojekte:** [`samples/visual-smoke/`](samples/visual-smoke/) und [`samples/pong-smoke/`](samples/pong-smoke/).
- **GLES3-Build:** [`build-godot-ps5-gles3-canvas.yml`](../../.github/workflows/build-godot-ps5-gles3-canvas.yml) (im Repo-Root `.github/workflows/`).
- **Testapp-Dokumentation:** [`gles3-canvas/README.md`](gles3-canvas/README.md).
- **Ältere Detailanalysen:** [`GRAPHICS_BRINGUP.md`](GRAPHICS_BRINGUP.md), [`docs/DISPLAYSERVER_INTEGRATION.md`](docs/DISPLAYSERVER_INTEGRATION.md), [`docs/PS5_GPU_HARDWARE_ACCEPTANCE.md`](docs/PS5_GPU_HARDWARE_ACCEPTANCE.md).

## Dokumentation nach jedem neuen Konsolentest aktualisieren

1. Neue Version/Title-ID, Commit und Actions-Build eintragen.
2. Unterscheiden: **nur gebaut**, **auf PS5 sichtbar**, **vollständig spielbar**.
3. Screenshot/Video und exakte `/data/GodotPS5/`-Logmarker dokumentieren; keine Erfolgsbehauptung allein aus CI ableiten.
4. Neue Fehler mit reproduzierbaren Schritten und Fix-Commit festhalten.
5. Das jeweils **nächste offene P0-Ziel** hier ändern und alte Erfolgstests für Regression erhalten.

---

**Summary (2026-10-23):** PS5 Godot v0.1.6 proves GDScript, GLES3, DualSense, original physics2D, FreeType, savegames, audible AudioOut and now full third-party G2P Platformer Level_01→Level_02. M12d disabled four unused TileMap navigation updates and reduced real user scene/player startup from 27.004s to **5.712s**, but TAR #31 shows **severe intermittent 133–150ms frames / 1–6 FPS bursts**; shader compiles are suspicious but cannot explain every block. M13 signed experimental v0.1.7 profiler measures CPU-before-EGL vs EGL-swap time in native wrapper. No performance fix yet, PS5 measurement pending. Keep stable v0.1.6 for rollback.

## M14 – Reversible EGL frame pacing experiment (2026-10-23)

Physical M12d TAR #31(1) contains 38 frame hitches and zero M13 profiler markers, so a CPU-vs-EGL attribution **is not proven**. M14 v0.1.8 branch `perf/godot-ps5-m14-present-pacing` / [PR #255](https://github.com/Yahballon/tmp_lap/pull/255) adds reversible `eglSwapInterval(0)` comparison against original `eglSwapInterval(1)` plus M13 CPU/swap logging. Write `vsync` in `/data/GodotPS5/present_mode.txt` for rollback to original presentation scheduling; absent config selects experimental `immediate`; invalid config selects conservative `vsync`. Hardware startup, glitch/fps improvements, signing and native test acceptance are **UNVERIFIED** until workflow/PS5 testing. Refer to [M14_PERFORMANCE.md](M14_PERFORMANCE.md) for risks/acceptance. Preserve original v0.1.6/v0.1.7 PCK/installer and user saves.

## M15 – Safe VSync rollback + native main loop timing (2026-10-24)

Physical PS5 TAR `bfpilot-download (33).tar` has `GODOT_PS5_M14_PRESENT_MODE requested=immediate effective=immediate`; the v0.1.8 regression is real. The newest M14 game session contains 66 reported `M13_FRAME_SPIKE` events; all 66 have `cpu_before_swap_ms>80` (21 events >1s total), while just one has `egl_swap_ms>80`. The slowest >2s spikes are *outside* the timed EGL swap, so no claim of a swap-blocked GPU; earlier v0.1.6 M12d was already imperfect. The user reported severe gameplay degradation.

M15 v0.1.9 reverts the default to **VSync=1** on missing `/data/GodotPS5/present_mode.txt`, keeps opt-in immediate A/B, caps unbuffered successful PCK `OPEN_OK` logging to eight records (real IO and errors preserved) and adds `GODOT_PS5_M15_ITER_PROFILER_READY`, `GODOT_PS5_M15_ITER_SPIKE` / `M15_ITER_5S` native `OS_PS5::run()` timestamps for controller, events, Godot `Main::iteration` and outside-loop timing. Existing M13 pre-swap vs EGL timing remains. The exact source of previous v0.1.6 ~133–150ms hitch is still **not proven**.

Hardware gate: cross-build original Godot 4.7.2, sign PPSA99847 contentVersion 01.000.010; publish TESTBUILD only on successful trusted `push` artifact; verify on physical console with original M12d PCK and AudioOut. Keep v0.1.7 rollback. Compare new M15 iteration phase timings and M13 present timings over at least 60 seconds. See `perf/godot-ps5-m15-safe-pacing` and signed workflow `build-godot-ps5-m15-safe-pacing.yml`. **PS5 M15 performance not yet validated.**

## M16 – Native kernel-backed Godot frame pacing (2026-10-24)

New physical M15 `bfpilot-download (34).tar` shows effective `vsync`, M15 Main::iteration up to ~1923ms, outside-loop up to 948ms, 34 logged M15 spikes, while `M13 egl_swap_ms` usually ~0.1ms. Level_02 startup remains slow (24.549s). VSync-off previously made stutters worse; DO NOT make it default. M16 v0.2.0 candidate in branch `perf/godot-ps5-m16-kernel-sleep-trace` overrides only the native GLES3 PS5 `OS_PS5::delay_usec` with `sceKernelUsleep` and explicit Unix fallback, leaving existing GodotPhysics2D, audio, external PCK and VSync=1 intact. Adds bounded `GODOT_PS5_M16_SLEEP_5S` for requested/actual sleep analysis. Signed CI and actual PS5 improvement still **UNVERIFIED**. See [M16_PERFORMANCE.md](M16_PERFORMANCE.md).

## M17 – Identify exact blocking Godot frame phase (2026-10-24)

New real-console archive `bfpilot-download (35).tar` demonstrates M16 v0.2.0 has **0 native sleep requests** in all nine five-second intervals while it continues to hitch at ~1 FPS: `Main::iteration()` ~1.92s, `eglSwapBuffers` ~0.1ms in the worst intervals. Physically tested Level_01/Level_02 and confirmed v0.2.0 TESTBUILD; no confirmed performance gain. M17 experimental `v0.2.1` adds opt-in *inside original Godot 4.7.2 Main::iteration* phase profiler to separate Physics, Scene/GDScript, RenderingServer::sync, RenderingServer::draw, tail and frame delay. The overlay is strict and testable against upstream, retains M13+M15 profilers, standard VSync=1, original M12d PCK, native AudioOut and rollback releases. Signed native CI and physical PS5 observations are still pending. Read [M17_PERFORMANCE.md](M17_PERFORMANCE.md), feature branch `perf/godot-ps5-m17-render-phase-profiler`. **Do not claim stutter fixed until hardware logs confirm it.**

## M18 – Main thread CPU-vs-wall + optional AudioOut isolation (2026-10-24)

Fresh physical PS5 `bfpilot-download (36).tar` M17 experiment logs show **28** main-frame phase spikes in latest session, reaching **~981ms Scene/process** and **~1912ms Renderer::draw** (2.86s total), despite `RenderingServer::sync` ~0 and 11 five-second windows with native M16 sleep calls=0. Physical PS5 still has significant unmitigated hitches. This invalidates VSync toggles, sleep changes and physics-only tuning as a solution. M18 v0.2.2 experimental candidate records CLOCK_THREAD_CPUTIME_ID CPU usage vs wall clock within `Main::iteration()`, and supports reversible `/data/GodotPS5/m18_audio_mode.txt` value `dummy` for diagnostic A/B (native AudioOut otherwise unchanged). Maintains Godot 4.7.2 original render code, VSync default, M12d platformer/controls/physics, older logs and rollback. **Hardware performance NOT YET VERIFIED.** See [M18_PERFORMANCE.md](M18_PERFORMANCE.md) and PR #259.


## M18 hardware QA #37 – CPU starvation/wait evidence (2026-10-24)

The real hardware archive `bfpilot-download (37).tar` **confirms the v0.2.2 binary is running**, not a stale TESTBUILD installation: `GODOT_PS5_M18_AUDIO_AB_MODE mode=native_audioout`, VSync confirmed via `GODOT_PS5_M14_PRESENT_MODE requested=vsync effective=vsync`, and M18/M17/M15 profiler output all present. `launch.txt` continues selecting `m12d-platformer-asset2201.pck`. Both original Godot GLES3 and AudioOut initialized.

In the ten recorded M18 five-second summaries following native AudioOut initialization, the sum of **Godot Main::iteration() wall clock** was **42,717.54 ms**, but **main-thread CPU time** totaled only **854.09 ms** (approximately **2.0%** CPU-vs-wall). Thus **41,863.46 ms / 98.0%** consisted of non-CPU-execution time inside the call (thread descheduling, kernel blocking, mutex/condition waits or GPU/driver waits; these mechanisms are not distinguished by CLOCK_THREAD_CPUTIME_ID). Worst individual main frame: `wall_ms=4813.88 cpu_ms=10.51 noncpu_ms=4803.37`; later M17 DRAW elapsed 7700.18ms and M13 frame before-swap elapsed 7628ms with EGL swap ~0.1ms. M16 sleep call count remains zero. No evidence that physics computation or a busy CPU loop is the primary bottleneck. The cause of the wait is **still unknown**; do not describe this as a proven GPU or AudioOut fault.

**Next two already-supported controlled A/B tests (no code/build changes):**

1. Keep `/data/GodotPS5/launch.txt` unchanged; create `/data/GodotPS5/m18_audio_mode.txt` with exact content `dummy`; restart title and reproduce for at least 60 seconds. Verify stdout `GODOT_PS5_M18_AUDIO_AB_MODE mode=dummy`. This intentionally disables sound for *one diagnostic run only*. Delete the config file afterwards and restart to restore normal audio.
2. With native audio restored, temporarily rename `/data/GodotPS5/launch.txt` to `launch.txt.backup` and restart: existing launcher falls back to bundled **`/app0/assets/godot/visual-smoke.pck`** (`PACK_SOURCE=BUNDLED_VISUAL`). If this simple scene is also slow, the issue lies below the large M12d platformer scene; restore `launch.txt` afterwards. If it is fast, compare M12d-specific rendering/data access.

Compare `GODOT_PS5_M18_MAIN_CPU_5S`, `GODOT_PS5_M17_PHASE_5S`, `GODOT_PS5_M13_FRAME_5S`, and mode markers between fresh sessions; do not conflate historic append-only log entries. Do not introduce another VSync or kernel sleep tweak without new causal evidence. PS5 v0.2.2 still **severely hitches**; performance acceptance NOT met.


## M24 – Roll back GL interception and isolate Godot renderer sub-stages (2026-10-24)

User TAR `bfpilot-download (43).tar` directly confirms **two M23 v0.2.7 real PS5 Pong tests**, worse than M22: first M13 report only 6 frames; M17 draw stalls up to 7,653 ms and M18 thread CPU ~39ms during 8.58s frame. At the time of each severe stall, all 23 older GL wrappers together take only 3.6–3.8ms and all 32 newly added M23 wrapper calls add just 0.18–0.20ms. This **rules out measured GL API timing as the direct cause**; driver or Godot's unmeasured renderer remains possible. M22 GL buffer ring was not reached on hardware and must not be treated as a confirmed memory leak.

**M24 v0.2.8** branches afresh from M18 (original buffer ring, no M19/M23 API interceptors, no M20 timestamp bypass, M21 fence status replacement or M22 orphaning), and adds exactly seven coarse phase durations around original `RenderingServerDefault::_draw` via guarded `patch_ps5_m24_render_stages.py`: begin/scene/prepare/viewport/end/post/profile. `GODOT_PS5_M24_RENDER_READY`, `M24_RENDER_SPIKE`, and `M24_RENDER_5S` in bounded logs. Retains original game packs, native AudioOut, DualSense, real physics, VSync default and earlier M13/M15/M17/M18 timing. Host and native CI are independent gates, and actual PS5 FPS acceptance remains **UNVERIFIED**. Read [M24_PERFORMANCE.md](M24_PERFORMANCE.md), PR #265, keep v0.2.7 rollback package.


## M25 – Isolate Canvas2D drawing from framebuffer blit and GL frame end (2026-10-24)

Actual PS5 firmware 5.10 hardware TAR #44 contains the first M24 v0.2.8 original-engine `GODOT_PS5_M24_RENDER_5S` samples. Bundled Pong reaches 149 frames in initial five-second summary (M23 had 6), but later falls to 6,4,3,3,1,1. Crucially, M24's seven original `RenderingServerDefault::_draw` phases show the **only large wall-clock stall inside `RSG::viewport->draw_viewports()`**. In the first interval its max is 3,238.37ms, while begin, scene, prepare, end, post and profile sections all peak below ~0.24ms. The console remains largely unplayable. EGL buffer swap eventually measures ~0.1ms; this does NOT include the separate original GLES3 framebuffer blit.

Experimental M25 signed v0.2.9 source branch `perf/godot-ps5-m25-viewport-blit-trace` strictly retains M24's original Godot 4.7.2 renderer, no per-GL-API wrappers, no speculative GPU fence/timer/orphaning tweaks, and adds guarded monotonic timings inside the ORIGINAL upstream `RendererViewport::draw_viewports` and `_draw_viewport`: explicit canvas->render_canvas, context make-current, other per-viewport work, GLES3 blit_render_targets_to_screen, gl_end_frame, and remaining viewport list/setup time. New `GODOT_PS5_M25_VIEWPORT_READY`, `M25_VIEWPORT_SPIKE` and `M25_VIEWPORT_5S` reported with max and mean per sub-stage. Keep original VSync, native audio, GDScript/Physics2D, input and M13/M17/M18/M24 logs. **This is a diagnostic, NOT a hardware-proven frame-time fix**. Only a signed successful native CI and TESTBUILD publisher may expose v0.2.9. See `M25_PERFORMANCE.md` and PR #266. Preserve prior v0.2.8 release as rollback.

## M26 – Test unbuffered diagnostics as a potential render-thread I/O stall (2026-10-24)

Physical PS5 firmware 5.10 TAR `bfpilot-download (45).tar` was directly extracted. The latest two v0.2.9 M25 built-in Pong sessions repeatedly show first 121–124 frames per 5-second interval, then degradation to **1 frame per 5-second interval**. New original Godot viewport timers finally isolate late freezes to `gl_end_frame` (8,658.45ms in a single frame), rather than `RSG::canvas->render_canvas` (1.85ms) or render-target blit (0.06ms); separate EGL swap itself ~0.1ms. The enclosing M24 renderer sometimes reports **24,884ms** inside viewport while M25's pre-log inner timer shows **8,660ms**, leaving ~16 seconds not attributed by internal viewport timings. In original PS5 native `present()`, the M13 logger runs `printf` AFTER timing `display.swap()`. All launcher's stdout and stderr streams were configured unbuffered (`_IONBF`), writing every printed line to `/data` from the rendering thread. This is a **credible but not proven storage-I/O blocking hypothesis**; native printf/stdio timings, mutexes and callback entry/exit need hardware evidence.

Experimental **M26 v0.2.10** based on M25 changes *only* stdout/stderr behavior: default 128KiB fully buffered output, reversible to original unbuffered by creating `/data/GodotPS5/m26_log_mode.txt` containing exactly `unbuffered`. Records mode in `gles3-runtime.log` through independent file handle. No changes to original Godot GLES3 draw, GL buffer and fence management, Vulkan, physics, GDScript, controller, audio, VSync, PCK loader or diagnostic message content. Buffered lines can be lost if app is forcibly terminated; judge frame responsiveness first. Host CI + signed PS5 release and TESTBUILD catalog gates remain mandatory. Device FPS improvement **NOT yet verified**. See [M26_PERFORMANCE.md](M26_PERFORMANCE.md).


## M26 actual PS5 hardware 60 FPS ACCEPTANCE – TAR #46 (2026-10-24)

**First convincing, verified performance success of the native Godot 4.7.2 PS5 GLES3 port**: the user tested the signed `PPSA99847` **v0.2.10** on firmware 5.10, and confirmed that the built-in Pong gameplay now runs without lags. Direct archive `bfpilot-download (46).tar` analysis verifies native `M26_IO_A_B_MODE=1` (`buffered`), original 1080p Godot renderer, native AudioOut, and the following *new-session* results: first five-second report **301 frames, one startup spike ~150ms**; next **nine complete five-second reports are 300 frames each and zero >=80ms spikes** (at least **2,700 successive frames across 45 steady seconds**; ten windows ~3,001 frames total). Normal frame time ~16.6ms, viewport/C​​anvas drawing ~1.7ms, display swap ~0.12ms, all original M24/M25 scene/viewport reports stable. Pong heartbeats reach frames 600, 1200, 1800, 2400 and 3000, plus recorded hits/scores; actual game simulation continues. Prior v0.2.9 degraded to ~1–3 frames per five-second interval.

Only planned behavioral difference from M25 is **fully buffered 128KiB stdout/stderr on /data instead of synchronous line-by-line unbuffered output from rendering callbacks**. This is strong causal evidence that diagnostic log I/O was a major performance killer, though no controlled M26 unbuffered A/B hardware run or per-write latency study has yet proven exclusivity. Buffered logs may remain unwritten after an abrupt kill; the fresh M26 marker may share a line with stale buffered pre-session log fragments. **Do not interpret stale max_draw_ms fragments before the M26 boot marker as fresh M26 regressions**.

Signed release [godot-ps5-gles3-canvas-v0.2.10](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gles3-canvas-v0.2.10) and main `version.json` version `0.2.10` published successfully. Preserve this **KNOWN-GOOD 60 FPS PONG BASELINE** for rollback and future work; do not silently reset to M19–M25 or resurrect unbuffered diagnostic output. Next explicit testing gate is the external M12d platformer and longer sessions, not automatically claiming every Godot project is stable. See [M26_PERFORMANCE.md](M26_PERFORMANCE.md).


## M27 – M26 60 FPS baseline: external Platformer hardware acceptance prepared (2026-10-24)

**Keep M26 v0.2.10 source/binary intact** (confirmed 60 FPS Pong on real firmware 5.10, TAR #46). The user's uploaded TAR #46 also preserves `launch.txt.bak` containing `m12d-platformer-asset2201.pck`, and old runtime history resolves it to `/data/GodotPS5/games/m12d-platformer-asset2201.pck`. The previously uploaded TAR #31 contains the exact PCK (3,325,680 bytes, SHA256 `6d2145876d9c73e9d33c5c98336c56bb6e0339636e38b5ea58367c7f28ed05f2`). **No engine rebuild/version bump** is needed for the next platformer test: keep signed TESTBUILD PPSA99847 v0.2.10 installed and rename `/data/GodotPS5/launch.txt.bak` to `launch.txt`; preserve buffered mode (no `m26_log_mode.txt`) and VSync default. Physically run both platformer levels 3–5 minutes to check sustained ~60 FPS, input, physics, audio and camera; collect TAR logs. To restore known-good Pong, rename `launch.txt` to `launch.txt.bak` and restart. The packaged companion game PCK and launch config were verified separately, but **external game hardware acceptance is pending**. See [M27_PLATFORMER_ACCEPTANCE.md](M27_PLATFORMER_ACCEPTANCE.md). This doc-only test branch does not alter M26 FPS, engine source, version.json or TESTBUILD catalog.


## M27 PHYSICAL PS5 HARDWARE ACCEPTANCE PASS – M12d Platformer at 60 FPS (2026-10-24, TAR #47)

**Confirmed by the user's direct physical test and independently measured in `bfpilot-download (47).tar`:** Original external Godot 4.7.2 platformer on untouched **M26 v0.2.10 / PPSA99847**, PS5 fw 5.10, **starts quickly and plays without progressive lag**. The user expressly confirms the game works fully for their test. Last-session `gles3-runtime.log` confirms `M26_IO_A_B_MODE=1` (128KiB fully buffered stdout/stderr), `PACK_SOURCE=CONFIG PACK=/data/GodotPS5/games/m12d-platformer-asset2201.pck` and native PS5 AGC 1920x1080 GL4.6. This verifies the external platformer, **not another Pong demo**.

The six complete game `M12D_FRAME_5S` summaries report **60.0 FPS** each with frames **302,300,299,300,300,300**. First window contains one 136.9ms M12d startup hitch, and M13 first window includes two startup spikes (161.1ms and 456.4ms), but **the next five complete five-second windows are zero >=80ms stutters**, 299–300 game frames and exactly **300 M13 engine frames per interval**, sustaining roughly **25 hitch-free measured seconds** after warmup. M24, M25 and M17 phase window summaries agree. Console prints `GODOT_PS5_M12D_NAV_DISABLED_CONFIRMED scene=Level_01 physics_ground=true physics_traps=true` and the matching `Level_02` marker, plus player-position/grounded/jump heartbeats through tick 1800 and native AudioOut successful blocks 1/2048/4096. Strong evidence for rendering, scripts, real 2D physics, controls and live audio after load, unlike the prior catastrophic progressively decreasing FPS.

**VERIFIED BASELINE:** 60FPS Pong (TAR #46, ~45 stable measured seconds) **and** real 2D Platformer in Level 01/02 (TAR #47, ~25 stable measured seconds after warmup), same frozen signed M26 engine. The user reports fast loading and no noticeable lags. Not yet a 3–5 minute endurance test, 3D certification or general Godot-4.x compatibility. **Do not roll back buffered logging, introduce per-frame filesystem writes, or rebuild/overwrite the signed v0.2.10 that passes hardware.** Maintain M27 as documentation-only branch. Full acceptance detail: [M27_PLATFORMER_ACCEPTANCE.md](M27_PLATFORMER_ACCEPTANCE.md), PR #268.
