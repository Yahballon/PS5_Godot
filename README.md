<div align="center">

# GODOT PS5

### Native Godot 4.7.2 Homebrew Runtime
**by YAHBALLON**

**Real GDScript · 2D Physics · OpenGL/GLES3 · DualSense · Native AudioOut**

[Download v0.2.10](https://github.com/Yahballon/PS5_Godot/releases/tag/v0.2.10) · [Source](godot-ps5/) · [Sample Games](#sample-games) · [Build Notes](#building-from-source)

</div>

> **Experimental PS5 port.** Hardware-confirmed on a jailbroken PS5 (firmware 5.10). Not an official Godot or Sony product. No guarantees for every firmware, 3D game, or Godot 4.x feature.

## Highlights

- **Godot 4.7.2 GLES3/Compatibility renderer** on native PS5 via community homebrew SDK / PS5 OpenGL stack.
- **Actual GDScript**, real engine-driven drawing and **CharacterBody2D / TileMapLayer collisions**.
- **DualSense**: left stick or D-pad, Cross/X to jump in the 2D Platformer.
- **Native PS5 AudioOut** and Godot WAV/audio playback.
- Installable homebrew title **`PPSA99847`**, distributed as a signed installer ZIP.
- External `.pck` loading from `/data/GodotPS5/games/`, without rebuilding the engine.
- Critical **M26 buffered logging fix**: avoids blocking every frame on synchronous stdout/stderr disk writes. **Do not revert the 128 KiB fully buffered logs to unbuffered** for normal gameplay.

## Real PS5 performance

The two samples were tested on real PS5 firmware 5.10 with the same signed v0.2.10 engine:

| Game | Result | Hardware evidence |
| --- | --- | --- |
| **Pong** (bundled default) | ~60 FPS, nine consecutive 5-second intervals with **300 frames and 0 ≥80ms stalls** after start | `M26_PERFORMANCE.md`, PS5 TAR #46 |
| **2D Platformer Starter Kit** | ~60 FPS, Level 1 + Level 2, five consecutive ~5-second steady windows, working jumps/collisions and native audio | `M27_PLATFORMER_ACCEPTANCE.md`, PS5 TAR #47 |

The tests also recorded some short **startup/loading hitches**. Longer endurance, other Godot games and 3D rendering are **not yet certified**.

## Download and install

Find the following assets in **[Releases – v0.2.10](https://github.com/Yahballon/PS5_Godot/releases/tag/v0.2.10)**:

| Asset | Purpose |
| --- | --- |
| `PPSA99847.zip` | **The tested signed PS5 engine/homebrew installer** (Pong is included and starts by default) |
| `GodotPS5-Pong-v0.2.10.zip` | Separately selectable external Pong `.pck`, `launch.txt`, and instructions |
| `GodotPS5-M12d-Platformer-v0.2.10.zip` | External 2D Platformer 1.1.1 with PS5 controls/navigation fix, its license, and `launch.txt` |
| `pong.pck` / `m12d-platformer-asset2201.pck` | Raw Godot game packages for custom launch setups |
| GitHub's **Source code (zip / tar.gz)** | Complete port overlays, build scripts, sample sources, adapters and milestone history from this tag |

Install `PPSA99847.zip` with a compatible jailbroken PS5 homebrew installer, or use the same TESTBUILD-delivered title. Only the **engine** is a PS5 homebrew title. The games are data-only Godot packages, not separate PS5 title IDs.

### Select a game

For **bundled Pong**, remove or rename `/data/GodotPS5/launch.txt` and restart the app.

For **Platformer**, extract the Platformer archive and copy the contents of its `GodotPS5` folder under `/data/GodotPS5/`. The result should look like:

```text
/data/GodotPS5/
├── games/
│   ├── m12d-platformer-asset2201.pck
│   └── pong.pck                      # optional
└── launch.txt                        # m12d-platformer-asset2201.pck
```

To select a package yourself, put its basename on one line of `launch.txt`. The engine verifies paths before loading. Restart the title after changing selection.

### Controls

**Pong:** DualSense controls as defined in [the Godot Pong GDScript](godot-ps5/samples/pong-smoke/main.gd). **Platformer:** left stick / D-pad to move, X to jump. The Platformer has its original two levels.

### Keep the 60 FPS fix enabled

By default no configuration change is necessary. Do **not** create `/data/GodotPS5/m26_log_mode.txt` with `unbuffered`: this switches back to the problematic synchronous log path. Leave `present_mode.txt` absent or set to `vsync`. Logs are found in `/data/GodotPS5/gles3-stdout.log`, `gles3-stderr.log` and `gles3-runtime.log`. Fully buffered stdout/stderr can lose a recent tail if the process is killed without a flush; this trade-off is documented.

## Source tree

```text
godot-ps5/
  engine/                PS5 Godot platform module and engine overlays
  native/                PS5 EGL/GLES3 launcher and buffered log fix
  scripts/               Native build, engine-patch and package scripts
  gpu-probe/             OpenGL SDK setup and diagnostic sources
  samples/pong-smoke/    Complete Pong project (Godot/GDScript)
  samples/m12-platformer-2201/
                         PS5 Platformer scene/input/audio/source adapters
  tests/                 Regressions and build verification
  MILESTONES.md          Reproducible development history
  M26_PERFORMANCE.md     Pong hardware verification and logging fix
  M27_PLATFORMER_ACCEPTANCE.md
                         Platformer hardware verification
samples/2d-platformer-ps5-source/
                         MIT-licensed original game source, assets and PS5 adaptations
.github/workflows/        Release/import automation
```

**Source provenance:** Frozen, hardware-tested Godot PS5 overlay [`Yahballon/tmp_lap` M26 at `39edf0e`](https://github.com/Yahballon/tmp_lap/tree/39edf0e42adbfa367cb08a22f3eed8c19030a769/homebrew/godot-ps5). Original third-party Platformer at [`AdilDevStuff/2D-Platformer-Starter-Kit` commit `a48fc99`](https://github.com/AdilDevStuff/2D-Platformer-Starter-Kit/tree/a48fc994cbcb168be472df84f2e13b55d2a2792f). The original [Godot Engine](https://github.com/godotengine/godot/tree/4.7.2-stable) upstream engine is fetched at build time; its entire source is not vendored here.

## Building from source

Reproduction requires a Linux build host, `clang-18`, the community [PS5 payload SDK](https://github.com/ps5-payload-dev/sdk) and the pinned toolchain/OpenGL dependencies. This repository retains the actual `build-engine.sh`, staged Godot PS5 platform sources and the known-good workflow `godot-ps5/` with the **M26** configuration. The original native build reference is [M26 GitHub Actions in tmp_lap](https://github.com/Yahballon/tmp_lap/actions/runs/40131425332).

For the full source path, see `godot-ps5/README.md`, `godot-ps5/ENGINE_PORTING.md`, `godot-ps5/M26_PERFORMANCE.md` and the pinned SDK setup scripts. The GitHub release republishes the already hardware-confirmed signed engine ZIP byte-for-byte, checking its original SHA-256:

```text
e5d9e2107424cc949bdaae59a6afd7e6c66be5bc15ebeab5afd564e714ffcf2e  PPSA99847.zip
```

## Licenses and credits

The Godot engine and the PS5 overlay include MIT-licensed code; some homebrew-native components declare **GPL-3.0-or-later**, and the repository root retains the GPL-3.0 license. Review per-file SPDX headers before distributing a modified build. Source and notices remain included.

**Platformer:** © G2P Studios / AdilDevStuff, **MIT**; game asset credits include **Kenney.nl** artwork and **Gdfxr** sounds. The external source is pinned and its original MIT LICENSE is preserved. This is a community port with attribution to the upstream creators, not an original game by YAHBALLON.

**Godot:** Godot Engine contributors (MIT). **PS5 port:** by YAHBALLON and the named community dependencies. No Sony SDK binaries or proprietary firmware files are included in the source repo.

---

**by YAHBALLON · Godot 4.7.2 PS5 GLES3 · Hardware-tested v0.2.10**
