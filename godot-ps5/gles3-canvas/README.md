# Godot 4.7.2 PS5 native GLES3 / Canvas2D

**Real upstream Godot GLES3 Canvas2D verified on physical PS5 (22 Oct 2026)!**

The screenshot supplied by the user shows a magenta/cyan translucent
checkerboard from a real Godot Sprite2D rendered by Godot's upstream
DisplayServerPS5 and RasterizerGLES3, against a ColorRect controlled by
GDScript / DualSense. Unlike the earlier scene bridge, the
`native/gles3_canvas_main.cpp` wrapper has no custom sprite shader
or glDrawArrays renderer: it opens PS5 EGL for Godot and swaps only
the real Godot-generated frames.

The user's console TAR `bfpilot-download (18).tar` contains **four
successful complete Godot GLES3 sessions** with 1001, 1145, 1136 and
1106 actual Godot swaps (**4388 total**). All four have
`GODOT_RETURN=0`, `NORMAL_SHUTDOWN`, `EGL_CLOSED`. Logs also
contain four `GODOT_PS5_REAL_2D_SCENE_READY` and **223
`GODOT_PS5_REAL_2D_CROSS_PRESSED` messages** across the runs.
`RENDERER=PS5 AGC` and OpenGL 4.6 Core / GLSL 4.60 were confirmed.
The screenshot independently confirms that pixels reached the display.

Some nonfatal engine warnings remain: optional `project.binary`,
global script cache and dummy physics configuration. This establishes a
small 2D scene, *not* broad support for physics, audio, text/font
rendering, complex resources, 3D or arbitrary exported games.

## v0.1.1 — opt-in PCK loading

To test your **own Godot 4 project**, copy an exported compatible PCK to
`/data/GodotPS5/games/MyGame.pck`. Then create
`/data/GodotPS5/launch.txt` with one line:

```text
MyGame.pck
```

Alternatively the line can be the validated absolute path, for example
`/mnt/usb0/godot/MyGame.pck`. Only explicit paths are considered;
there is deliberately **no automatic USB scan** in this GLES3 title.
Remove `launch.txt` to restore the working internal checkerboard demo.
Invalid paths/packs also fall back to that bundled fixture. Logs in
`/data/GodotPS5/gles3-runtime.log` identify the selection:

```text
PACK_SOURCE=CONFIG PACK=/data/GodotPS5/games/MyGame.pck
PACK_SOURCE=BUNDLED_VISUAL PACK=/app0/assets/godot/visual-smoke.pck
```

This loader is experimental: native GLES3 drawing was proven for the
bundled scene, but **external game compatibility has not yet been
tested on PS5**. Only run projects you trust. The combined GPL/MIT
binary and unofficial third-party SDK mirror require license and
source provenance review before broader distribution.

## v0.1.2 — bundled native Godot Pong 2D gameplay

The **default** internal `visual-smoke.pck` now contains a complete
font-free, Godot-authored Pong game from `samples/pong-smoke/`. Unlike the
previous checkerboard this exercises real Godot Canvas2D primitive draw calls,
paddle movement, a scripted ball/bot and scoring. DualSense controls:

- Left stick / D-pad up and down to move paddle
- **X** to serve, **Circle** to reset, **Options** to exit
- Auto exit after 180 seconds for repeatable PS5 test

Remove `/data/GodotPS5/launch.txt` to select the bundled Pong game.
External configured PCK paths still take precedence, exactly as in v0.1.1.
The launcher intentionally retains the old internal file name
`visual-smoke.pck` for binary compatibility.

**Hardware update (23 October 2026):** the user confirmed Pong works and
supplied a 13.88-second PS5 gameplay video (`20261022_234930_00248487(1).webm`).
Visual Pong runtime is verified (moving ball, moving paddles and scoreboard).
Specific X/Circle/Options mapping, scoring collisions, long-term performance
and clean exit await standalone Pong logs/hardware acceptance.
The v0.1.1 release remains available for regression comparison.
See `samples/pong-smoke/README.md` for expected log markers.
