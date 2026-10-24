# Godot PS5 – isolated GPU bring-up probe

**Experimental, not Godot gameplay.** This is a completely separate test
title **PPSA99844** (initial build v0.1.0); the proven headless Godot
GDScript runtime stays PPSA99843 and is never changed by this probe.

## Firmware 5.10 GPU acceptance — REAL HARDWARE SUCCESS (22 October 2026)

The PS5 user confirmed **visible blue/green/red fullscreen changes** in
GPU Probe v0.1.5. Console log verified:

```text
[GodotPS5 GPU 0.1.0] EGL_OPEN_OK
[GodotPS5 GPU 0.1.0] SURFACE_WIDTH=1920
[GodotPS5 GPU 0.1.0] SURFACE_HEIGHT=1080
[GodotPS5 GPU 0.1.0] GL_VERSION=4.6 (Core Profile) Mesa 26.2.0
[GodotPS5 GPU 0.1.0] GL_RENDERER=PS5 AGC
[GodotPS5 GPU 0.1.0] GLSL_VERSION=4.60
[GodotPS5 GPU 0.1.0] PAD_OPEN_OK
[GodotPS5 GPU 0.1.0] FIRST_FRAME_PRESENTED
[GodotPS5 GPU 0.1.0] PRESENTED_FRAME_COUNT=600
[GodotPS5 GPU 0.1.0] TOTAL_PRESENTED=1800
[GodotPS5 GPU 0.1.0] CLEAN_SHUTDOWN
```

Thus **native PS5 EGL context, GL 4.6, display mode, clear/swap,
DualSense open, 1800 presented frames, and clean shutdown are confirmed**.
Not yet evidence of Godot's own renderer.

## Next GPU milestone: GL shader + rotating triangle

The new probe should show **a large rotating three-color triangle** over the
blue/green/red fullscreen background. This tests actual compiled GLSL 4.60
vertex/fragment shaders, program linking, VAO/VBO uploads, uniform updates
and `glDrawArrays(GL_TRIANGLES,...)` on the PS5 GPU. It preserves the
previous color background as a fallback if shader compilation fails. Logs:
`VERTEX_COMPILE_OK`, `FRAGMENT_COMPILE_OK`, `PROGRAM_LINK_OK`,
`GL_GEOMETRY_READY`, `GL_FIRST_DRAW_ERROR=0`,
`GL_TRIANGLE_SUBMITTED`, `FIRST_FRAME_PRESENTED`.
On hardware also **visually verify the triangle**; successful GL calls
alone are insufficient.

## Acceptance conditions on PS5 hardware

After installing `PPSA99844.zip`, a real PS5 screen should display a sequence
of **blue → green → red fullscreen frames**, switching automatically about
every two seconds. DualSense **X** moves to the next color, and **Circle**
exits cleanly. The app also closes after at most 1800 frames.

The test writes `/data/GodotPS5/graphics-probe.log`. The critical markers
are `EGL_OPEN_OK`, `FIRST_FRAME_PRESENTED`, `PRESENTED_FRAME_COUNT=60`
and `CLEAN_SHUTDOWN`. Capture a real console screenshot and this log; CI
cross-link and package validation alone do not prove display works on PS5.

## Implementation & licenses

Uses the existing `Yahballon/PS5-DevBridge` native
`templates/simple-calc` as a **GPL-3.0-or-later** base, with its
`ps5-homebrew-ui` EGL/GL adapter and pinned `ps5-opengl` SDK. This
probe itself is GPL-3.0-or-later; third-party code stays under its own
licenses. Its source, native OpenGL dependencies, corresponding source and
notices must be reviewed before any broad public release.

- GPU app source: `main.cpp`
- CI: `.github/workflows/build-godot-ps5-gpu-probe.yml`
- Output: `PPSA99844.zip`, attached only as a GitHub Actions test artifact
- **No catalog entry** until signed build and real firmware 5.10 validation
- This GPU test is not compiled into the MIT-licensed Godot engine

Next milestone after hardware success: implement real `DisplayServerPS5`
and connect to the upstream Godot 4.7.2 OpenGL compatibility renderer.

## GitHub Actions build gate (2026-10-22)

The previous upstream OpenGL SDK `v1.0.0` fetch failed with HTTP 404
([failed run 39765770533](https://github.com/Yahballon/tmp_lap/actions/runs/39765770533)).
The pinned unofficial SDK `v1.0.2` mirror workaround and its validation
passed, and the independent native probe **built, linked, signed, and
packaged successfully** in [run 39767154442](https://github.com/Yahballon/tmp_lap/actions/runs/39767154442).

The first workflow uploaded the signed `PPSA99844.zip` as an Actions artifact:
[download GPU test artifact](https://github.com/Yahballon/tmp_lap/actions/runs/39767154442/artifacts/12420847267).
The initial wording above describes the first CI artifact before the
subsequent console success. The GPU probe is **now in TESTBUILDS** and
v0.1.5 fullscreen color output was verified on PS5 hardware.
Please collect `/data/GodotPS5/graphics-probe.log` and a screenshot of
the first blue/green/red framebuffer test before claiming rendering support.
The GPL license/provenance audit for the unofficial SDK mirror remains open.

The known-good Godot headless/runtime title `PPSA99843` is unaffected.

## SDK mirror recovery (2026-10-22)

The original `blackbearreloaded/ps5-opengl` v1.0.0 download endpoint now
returns HTTP 404. This CI experiment uses the *unofficial* archival mirror
`KernelForgeLabs/ps5-opengl-sdk-mirror`, release `sdk-v1.0.2`. Its archive
is pinned by SHA-256
`30d8e51dd062739b629346102be5932728ba714bc50b1bdcdf08306c8843d9a4`,
and its SDK's embedded `manifest.sha256` is verified after extraction.
The repository's assertion that this is byte-for-byte upstream is **not
independently verified**, so provenance and licenses remain a pre-release
review gate. Native build success and actual console graphics are separate
acceptance gates. The original MIT Godot engine remains separate.

## Automatic TESTBUILD publishing

The first hardware-unverified standalone v0.1.0 GPU test was published as a
GitHub prerelease and added to `version.json` for PPSA99844.
Successful **future** native GPU CI builds produce unique
`0.1.<github.run_number>` versions and matching PS5 `contentVersion`.
The default-branch `Publish Godot PS5 GPU TESTBUILD` workflow verifies
the signed ZIP, creates a tagged GitHub prerelease and updates
`version.json` automatically. No manual Actions artifact download is
required for new builds. This remains an experimental GPU probe until
hardware validates actual display frames; provenance review is still open.

## Next GPU acceptance: textured 2D sprite with alpha (after v0.1.6)

The PS5 operator supplied an actual screenshot of the colored gradient triangle
and native console log confirming `VERTEX_COMPILE_OK`,
`FRAGMENT_COMPILE_OK`, `PROGRAM_LINK_OK`, `GL_GEOMETRY_READY`,
`GL_FIRST_DRAW_ERROR=0`, `GL_TRIANGLE_SUBMITTED`, and `CLEAN_SHUTDOWN`
for the v0.1.6 shader test. The log records 645 presented frames and
`CIRCLE_EXIT`: **shader rasterization is now proven on real PS5 hardware**.

This follow-up probe adds a moving magenta/cyan 64×64 checkerboard
RGBA8 texture drawn as a translucent 2D quad over the rotating triangle.
It tests 2D prerequisites: `glTexImage2D`, texture sampling with interpolated
UVs, VAO/VBO quad upload, GLSL 4.60, `GL_SRC_ALPHA` blending and uniform
animation. Look for `SPRITE_2D_READY`, `SPRITE_FIRST_DRAW_ERROR=0`,
`SPRITE_2D_DRAW_SUBMITTED` and *visible* checkerboard with transparency.

As before, this is an isolated native GPU test, **not** Godot's own 2D
renderer or DisplayServer. The proven GDScript binary `PPSA99843` remains
independent. On successful CI, the TESTBUILD publisher should create the
next version automatically without any manual ZIP installation.
