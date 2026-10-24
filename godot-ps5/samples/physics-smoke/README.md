# M9a – Godot 4.7.2 real 2D physics / CharacterBody2D on PS5

This **separate external PCK** tests whether the native Godot engine implements **REAL** Godot PhysicsServer2D. It revealed that **PPSA99847 v0.1.2** fell back to dummy physics; it now passes on physical PS5 with **PPSA99847 v0.1.3**, as verified by the user and console logs from `bfpilot-download (21).tar`.

The main Godot scene constructs CharacterBody2D, StaticBody2D, and
CollisionShape2D/RectangleShape2D. The character moves right with
`move_and_collide()`; real collision with the wall and the expected
surface normal are required for `GODOT_PS5_M9_REAL_COLLISION_OK`.
Purely visual changes and scripted Pong-style bounce do NOT count.

## Hardware result: PASS – 23 October 2026

The user confirmed the cyan square hit the pink wall and turned green on a
physical PS5 after installing **PPSA99847 v0.1.3** with the native
`godot_physics_2d` module. The uploaded `bfpilot-download (21).tar`
proves **two successful on-device sessions**, each with:

```text
GODOT_PS5_M9_REAL_COLLISION_OK x=1093.984375 normal=(-1.0, 0.0)
GODOT_PS5_M9_TEST_PASS physics_frames=369
GODOT_RETURN=0
NORMAL_SHUTDOWN
EGL_CLOSED
```

No dummy PhysicsServer2D warning appears in the two passing sessions.
The same cumulative TAR includes earlier **v0.1.2 failures** with dummy
physics, `GODOT_PS5_M9_TIMEOUT` and `GODOT_RETURN=43`; keep those as
regression evidence and do not count them as new failures. Optional script
cache messages remain in stderr even when physics succeeds.

The new native installer was compiled, signed and validated in
[CI run #39872101079](https://github.com/Yahballon/tmp_lap/actions/runs/39872101079).
This test does **not** certify other physics nodes, fonts, audio, saving,
performance or general third-party project compatibility.

## PS5 hardware test

After a successful [M9 host CI](https://github.com/Yahballon/tmp_lap/actions/workflows/build-godot-ps5-m9-physics-pck.yml),
download the artifact containing a PS5 setup ZIP.

1. Use `PPSA99847 v0.1.3` (native GodotPhysics2D enabled). Older v0.1.2 is a known **failure** for real collision.
2. Copy the ZIP's `GodotPS5/` contents to `/data/GodotPS5/`:
   `games/physics-smoke.pck` and `launch.txt`. This replaces the
   **previous M8c launch.txt** intentionally; the M8c PCK remains on disk.
3. Start the existing Godot PS5 GLES3 app.
4. The cyan square should move into the pink wall and **stop**.
   It changes green only when **real collision API** confirms wall contact;
   a green circle appears at the top. Press X optionally to log input.
5. After 300 physics ticks of the green result, the app exits.
6. Inspect `/data/GodotPS5/gles3-stdout.log` for
   `GODOT_PS5_M9_BODIES_READY`,
   `GODOT_PS5_M9_REAL_COLLISION_OK`, and
   `GODOT_PS5_M9_TEST_PASS`.
   Inspect `gles3-runtime.log` for `PACK_SOURCE=CONFIG`,
   `GODOT_RETURN=0`, `NORMAL_SHUTDOWN`, and `EGL_CLOSED`.
   Include `gles3-stderr.log` for failures.

**If the square passes through the wall or logs
`GODOT_PS5_M9_NO_COLLISION_PHYSICS_UNAVAILABLE`, that is a real regression.**
Verify the installed native app is **v0.1.3**, not the older dummy-physics v0.1.2, and capture the three GLES3 logs.

Remove `/data/GodotPS5/launch.txt` to restore built-in Pong, or write
`external-smoke.pck` in launch.txt to return to the verified M8c demo.

A green host CI run establishes that this **PCK has genuine Godot collision
logic** on desktop Godot 4.7.2. It does **not** prove PS5 physics support.
