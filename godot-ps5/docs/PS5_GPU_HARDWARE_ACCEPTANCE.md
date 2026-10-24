# PS5 native graphics hardware acceptance — 22 October 2026

| Area | Tested PS5 title | Console confirmation | Remaining work |
| --- | --- | --- | --- |
| GDScript VM, PCK and main loop | PPSA99843 v0.3.2 | Bundled pack, clean exit | Combine with renderer |
| DualSense → Godot Input → GDScript | PPSA99843 v0.3.2 | 38 X presses in GDScript | Other controls + analog |
| EGL 1920×1080, OpenGL 4.6 Mesa PS5 AGC | PPSA99844 v0.1.5 | Fullscreen RGB color changes and 1,800 frames | EGL ownership inside Godot |
| GLSL shaders, triangle, VBO/VAO | PPSA99844 v0.1.6 | Gradient triangle screenshot, zero draw error, 645 frames and Circle exit | Use Godot GLES3 renderer |
| RGBA8 textured quad, UV, blending | PPSA99844 v0.1.7 | Screenshot shows magenta/cyan checkerboard with the gradient triangle visible through it | Real Godot 2D scene |

**Evidence for v0.1.7:** User-provided 2026-10-22 screenshot shows a red
viewport, multi-colored triangle and translucent checkerboard covering its
lower-left area. This proves visible texture and compositing output on a
physical PS5 in the user's test. It does **not** prove the Godot engine
rendered this frame. No v0.1.7 `graphics-probe.log` was supplied; do not
claim its new log markers were observed.

**Known build status:** v0.1.7 GPU test compiled successfully and its
`PPSA99844.zip` was published by
[build 39771721890](https://github.com/Yahballon/tmp_lap/actions/runs/39771721890)
and [publisher 39772102882](https://github.com/Yahballon/tmp_lap/actions/runs/39772102882).
Its prerelease was registered into TESTBUILDS `version.json`.

**Compatibility caveat:** The GPU test uses a GPL-3.0-or-later DevBridge
template with a checksum-pinned unofficial OpenGL SDK mirror whose
provenance has not been independently verified. The proven headless
Godot-engine source remains MIT. Do not silently combine GPL binary
components into MIT-only distribution claims; preserve corresponding
source, all notices and compatible distribution licensing.
