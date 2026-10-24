# Godot PS5 Probe v0.1.0 — experimental hardware test (NOT PLAYABLE)

This **native PS5 test package** is intended for PS5 jailbreak / homebrew only.
It is **not** the Godot 4 engine and will not launch Godot games.

It tests the PS5 window / renderer, DualSense buttons, access to USB and
`/data` with PS5-native kernel directory scanning, and Godot 4 PCK header
recognition. An original Godot 4 PCK can be placed at one of:

- `/data/GodotPS5/games/my-game.pck`
- `/mnt/usb0/godot/my-game.pck`
- `/mnt/usb1/godot/my-game.pck`

The test discovers the first valid PCK in each configured directory.
Press **Square** to rescan, **X** to check a PCK header, **Circle** to exit.
View `/data/GodotPS5/probe.log` for diagnostic results.

The true Godot engine cross-compilation lives in
[PR #207](https://github.com/Yahballon/tmp_lap/pull/207).
No PS5 GDScript/gameplay support, audio backend or renderer integration is claimed.
