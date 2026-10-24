# Genuine Godot 4.7.2 PS5 Visual Integration Acceptance Scene

This is a **real Godot scene with GDScript, Sprite2D, ColorRect, Label,
and a runtime-created RGBA8 checkerboard texture**. This sample is intended
to be run in a future actual DisplayServerPS5 + Godot GLES3 renderer build.

It is NOT the separately proven GPU Probe title PPSA99844. The native
PS5 Godot v0.3.2 title PPSA99843 is still headless, and cannot visibly draw
this scene yet.

Controls: DualSense X changes the background and counter; animated sprite
rotates and oscillates horizontally. GDScript exits after 20 seconds.

Host CI uses official upstream Godot 4.7.2 to build the real
`visual-smoke.pck` and run it headlessly, verifying
`GODOT_PS5_REAL_2D_SCENE_READY`. The `GODOT_PS5_REAL_2D_CROSS_PRESSED`
marker can only occur when a controller press reaches GDScript.

**PS5 acceptance requires actual visible screenshot + engine logs from
a graphical Godot binary**. Passing headless Linux PCK generation does
not demonstrate PS5 graphics or a working Godot Renderer.
