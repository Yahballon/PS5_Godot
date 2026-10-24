# Godot PS5 Pong — Real GLES3 Canvas2D Gameplay Test

An experimental **Godot 4.7.2 Godot/GDScript Pong mini-game** intended
as the default bundled PCK of PPSA99847 v0.1.2. It uses the **actual
Godot `Node2D._draw()` commands** (rectangles, lines, circles, alpha),
Godot `Input` and GDScript game logic. No standalone OpenGL quad renderer,
no Font/FreeType dependency, and no unverified Godot PhysicsServer2D.

Controls:

- **Left stick up/down or D-pad up/down:** player paddle.
- **X:** serve ball after start or each score.
- **Circle:** reset match.
- **Options:** quit cleanly.
- Bot controls the other paddle. The score is rendered with custom
  seven-segment vector digits rather than unsupported native fonts.
- Automatic shutdown after 180 seconds for hardware validation.

Expected PS5 logs in `/data/GodotPS5/gles3-stdout.log`:
`GODOT_PS5_PONG_READY`, `GODOT_PS5_PONG_SERVE`,
`GODOT_PS5_PONG_PADDLE_INPUT`, `GODOT_PS5_PONG_60_FRAMES`,
`GODOT_PS5_PONG_HIT`, `GODOT_PS5_PONG_SCORE`,
`GODOT_PS5_PONG_OPTIONS_EXIT`, or
`GODOT_PS5_PONG_TIMELIMIT_EXIT`.
`gles3-runtime.log` must show `GODOT_SWAP_FIRST` and
`NORMAL_SHUTDOWN`.

**Hardware update (23 October 2026):** User reports Pong works on a real
PS5 and supplied a 13.88-second gameplay video named
`20261022_234930_00248487(1).webm`. Review confirms visible moving ball,
changing paddle positions, pitch, and vector scoreboard. Therefore **visual
Pong gameplay is PS5-confirmed**, not merely CI-tested. This short video
does not independently verify every control mapping, paddle/ball collision,
score transition, frame pacing or clean engine exit. Preserve those as
outstanding acceptance checks until the three GLES3 logs and/or longer
hardware evidence are available. Known-good v0.1.1 remains for regression.

Technical caveats: hand-coded paddle/ball collisions only;
no claim that native Godot physics, fonts, 3D, audio, or
exported third-party games are fully compatible.
