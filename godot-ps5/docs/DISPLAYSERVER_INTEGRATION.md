# Godot 4.7.2 → PS5 EGL/GLES3 integration contract

**Status: PS5 v0.1.1 hardware-proven GDScript → native GL bridge; Godot's
own GLES3 renderer is not running yet.**

Two independent console-tested paths now exist:

- `PPSA99843`: actual native Godot 4.7.2 GDScript engine + PS5 controller.
- `PPSA99844`: non-Godot EGL/OpenGL 4.6 accelerated rendering and
  textured alpha-blended geometry.

The goal is to integrate these *without* silently swapping Godot
GDScript output for a stand-alone renderer.

## 1. Platform build and renderer dependencies

Godot platform overlay `engine/platform/ps5/detect.py` currently advertises
`opengl3=False`, and `scripts/build-engine.sh` forces `opengl3=no`.
Both intentionally produce a headless smoke library. Build a separate
**experimental** engine configuration with `opengl3=yes`, enabling the
upstream `drivers/gles3` and shader/compiler resources required by the
Compatibility rendering method. Do not change stable headless defaults.

Upstream Godot 4.7.2 reference code:

- `servers/display/display_server.h` — registration of create function,
  main window/display contracts, `process_events`, `swap_buffers`.
- `platform/linuxbsd/x11/display_server_x11.cpp` — an example of
  choosing an EGL/GL manager, `RasterizerGLES3::make_current(...)`,
  registering a display backend and defining swap behavior.
- `drivers/gles3/rasterizer_gles3.cpp` — upstream GLAD/EGL symbol loading,
  GL-over-GLES configuration, renderer setup.
- `servers/display/display_server_headless.cpp` — existing dummy
  backend, **not** a graphical implementation.

## 2. PS5 DisplayServerPS5

Implement `engine/platform/ps5/display_server_ps5.{h,cpp}` with
the real Godot 4.7.2 `DisplayServer` interface. At minimum:

- Register `ps5` backend through `DisplayServer::register_create_function`.
  Fail with a useful `Error` and log if EGL startup fails.
- Own exactly one main window and return actual `1920×1080` size (or
  queried mode), usable rect, focus status, DPI, display refresh and
  window drawing state. Do not return fictitious success for unsupported
  subwindows or native handles.
- Create the EGL display/context/surface before constructing the GLES3
  compositor; choose the GL-over-GLES mode suited to the PS5 Mesa
  **OpenGL 4.6 Core Profile** path (`RasterizerGLES3::make_current(true)`
  should be tested against Godot's actual GLAD path).
- Ensure that `glGetString(GL_RENDERER)` still reports `PS5 AGC` after
  context transfer to the Godot renderer; expose detailed diagnostics.
- Own `swap_buffers`/presentation, thread affinity and orderly EGL
  teardown. Destroy Godot GL objects **before** destroying EGL context.
- Bind the existing `ps5_pad::Bridge` to Godot's event loop without
  duplicate input delivery. Preserve the 38-X-press regression fixture.

## 3. Independent integration build

Provide a separate experimental signed PS5 title / unique Title-ID,
not overwriting `PPSA99843` or `PPSA99844`.
CI must build *upstream Godot* with `GLES3_ENABLED`, link its actual
rendering libraries, package a real Godot-created `.pck`, and run
host-side binary, ZIP, metadata and linkage validations. If compilation
fails, keep it an Actions diagnostic, not a TESTBUILD release.

Any GPL-linked graphics binaries must be distributed with compatible
licenses and corresponding sources. Review the OpenGL SDK mirror first.

## 4. Hardware acceptance gates

1. Confirm the same Godot PS5 binary prints an actual
   `DisplayServerPS5` initialization marker and renderer identity.
2. Render a **Godot-generated** packed scene with `Sprite2D`,
   `ColorRect`, `Label`, animation or rotation from GDScript.
3. Verify scene changes when X is pressed via the Godot Input singleton;
   capture real PS5 screenshot and engine logs.
4. Validate graceful exit, context cleanup, resource loading and user://
   save writes; check repeated launches.

`GL_TRIANGLE_SUBMITTED` and `SPRITE_2D_DRAW_SUBMITTED` from the
stand-alone GPU probe alone are **not** evidence of a functional Godot
DisplayServer.

## Stage 1 committed: native DisplayServerPS5 ABI scaffold

`display_server_ps5.h/.cpp` now implements an **opt-in, genuinely
Godot-derived** display backend for the first Godot 4.7.2 cross-compile.
`OS_PS5` registers the driver in its constructor (matching upstream
LinuxBSD driver registration timing). The new platform code declares a
logical 1920×1080 single-window screen, but **rejects all non-dummy
renderers and reports `window_can_draw=false`** until a real EGL
context is owned by Godot.

The production/headless `PPSA99843` binary is unaffected. Enabling
`GODOT_PS5_DISPLAY_EXPERIMENT=1` only adds the display backend and
compiles the real upstream Godot static archives. The separate
`Validate Godot PS5 DisplayServer ABI` workflow performs this isolated
cross-compile; it does **not** publish a TESTBUILD or claim Godot 2D
works. Next stage will replace RasterizerDummy with actual Godot GLES3
and transfer EGL ownership via native PS5 glue.

## 22 October 2026: ABI builder diagnostics fixed

[ABI run 39774451360](https://github.com/Yahballon/tmp_lap/actions/runs/39774451360)
compiled the *real upstream Godot 4.7.2 sources* and
`platform/ps5/display_server_ps5.cpp` successfully; it created 10 actual
PS5 static archives. The job's final assertion failed because it searched
for the SCons object under `/tmp/godot/platform/ps5`, but the platform
library is at `/tmp/godot/bin/libgodot_ps5.ps5.template_debug.x86_64.a`.
CI now checks its object members with `llvm-ar-18 t` instead.

The separate headless full-engine build [39774451141](https://github.com/Yahballon/tmp_lap/actions/runs/39774451141)
linked and signed a native PS5 binary after applying the known optional
weak TLS fix, but its metadata verification still expected
`contentVersion=01.000.014` instead of the staged `01.000.015`.
The test now matches staging, and a host regression test prevents that
specific mismatch from recurring. Neither result establishes Godot GLES3
rendering; the native DisplayServer is still dummy-only.


## 22 October 2026: Same-process scene + GPU accepted

`PPSA99845 v0.1.1` runs native Godot 4.7.2 and PS5 OpenGL 4.6 together.
The user saw the checkerboard and background color change from X.
`bfpilot-download (16).tar` confirms 24 GDScript X press events,
`BOOT_FRAME_PRESENTED`, `GODOT_GDSCRIPT_SCENE_FRAME_DRAWN`,
`FIRST_DRAW_GL_ERROR=0` and at least 600 presented frames.
A later user-supplied complete `scene-bridge.log` confirms
`GDSCRIPT_CROSS_COUNT=24`, `PRESENTED_FRAME_COUNT=600`,
`GODOT_ENGINE_RETURN=0`, `TOTAL_PRESENTED=1156`,
`GPU_SHUTDOWN`, and `NORMAL_SHUTDOWN`. **Normal engine exit and
EGL GPU cleanup are now hardware-confirmed on v0.1.1.**
The source remains under GPL-3.0-or-later+MIT obligations
and an unofficial GPU SDK mirror requires provenance review.

### Next real renderer gate: upstream GLES3 archive cross-compilation

`GODOT_PS5_GLES3_ARCHIVES=1` is an experimental **CI-only** switch
for compiling Godot's actual `drivers/gles3` and `drivers/egl` sources
together with the upstream GLAD loaders. It does not install an app or
turn on a rendering backend on existing title IDs.
The normal PS5 archive build still has `opengl3=no`.
The experimental compile must establish and validate native PS5
`libdrivers` GLES3 objects **before** DisplayServer ownership,
EGL context creation, texture uploads, GLAD pointer initialization,
Canvas rendering or an installable graphical Godot title is attempted.

### Dynamic EGL loader correction — 2026-10-22

[Native GLES3 compile 39828096451](https://github.com/Yahballon/tmp_lap/actions/runs/39828096451)
compiled most upstream renderer objects but failed in `egl_manager.cpp`:
`eglSetBlobCacheFuncsANDROID` and `eglGetPlatformDisplayEXT` were
redeclared by `EGL_STATIC` as C functions, conflicting with GLAD's
function-pointer globals. The CI-only GLES3 mode now uses
`EGL_ENABLED + GLAD_ENABLED` **without** `EGL_STATIC`, leaving
actual EGL function loading for the later DisplayServer runtime stage.


## First real GLES3 DisplayServer test available in TESTBUILD

The next isolated title is `PPSA99847`, **Godot PS5 GLES3 Canvas v0.1.0**:
[release](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gles3-canvas-v0.1.0) |
[native compile](https://github.com/Yahballon/tmp_lap/actions/runs/39839623074).
The signed ZIP is in `main/version.json` for the TESTBUILD app.
This experimental binary compiles and invokes Godot's actual
`RasterizerGLES3` and `DisplayServerPS5` backed by a native PS5 EGL
context. It **does not** contain the custom Scene Bridge Sprite2D
rasterizer. A successful build does not prove the PS5 shows a Godot frame.

Console acceptance for PPSA99847 requires a real screenshot of its
GDScript-driven Sprite2D/ColorRect, `GODOT_SWAP_FIRST` in
`/data/GodotPS5/gles3-runtime.log`, `DISPLAY_SERVER_PS5_EGL_READY`
in `gles3-stderr.log`, `GODOT_PS5_REAL_2D_SCENE_READY` in
`gles3-stdout.log`, button-driven background transitions, and
normal engine+GPU shutdown. If only the blue boot background shows,
EGL setup is proven but Godot's Canvas2D is not.


## 22 Oct 2026: REAL Godot GLES3 + Canvas2D works on PS5

PS5 test `PPSA99847 v0.1.0` passed with an independently supplied
screenshot of upstream Godot's Canvas2D Sprite2D checkerboard.
User's `bfpilot-download (18).tar`: four complete sessions with
1001/1145/1136/1106 Godot swaps, normal shutdown and 223
real GDScript X press markers. No standalone native renderer exists
in the GLES3 title; actual GLES3 frames are presented through
DisplayServerPS5 and the PS5 EGL graphics callbacks.

**v0.1.1** adds explicit external Godot 4 PCK selection via
`/data/GodotPS5/launch.txt`, preserving the known-good bundled
visual PCK by default. External game support is not yet hardware
verified; text fonts, audio, physics and advanced features remain
porting targets.
