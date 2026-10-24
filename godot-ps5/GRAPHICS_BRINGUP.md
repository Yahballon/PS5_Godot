# Next major milestone: native Godot display + controller for PS5

Status: **PS5 EGL/OpenGL 4.6 clear/swap is now confirmed on firmware 5.10**; native Godot DisplayServer and Godot renderer remain unimplemented. Source baseline:
Godot 4.7.2; PS5 firmware 5.10; homebrew `PPSA99843`. The console
already executed `GODOT_PS5_SMOKE_READY` three times with v0.2.11.

## PS5 GPU Probe v0.1.7 — textured 2D accepted (2026-10-22)

User tested [GPU Probe v0.1.7](https://github.com/Yahballon/tmp_lap/releases/tag/godot-ps5-gpu-probe-v0.1.7)
on real PS5 hardware and supplied a screenshot showing the GLSL-rotating
gradient triangle plus an RGBA checkerboard 2D sprite, with the triangle
visibly showing through the partially transparent checkerboard. The image
confirms **textured quad rendering and alpha blending on the PS5 display**.
The screenshot alone does not prove all inputs, exact animation speed,
or lifecycle behavior: no new v0.1.7 text log was supplied.

The independent headless Godot v0.3.2 runtime proved GDScript input; the
independent GPU title v0.1.7 proved GL 2D textured drawing. **These have not
yet been combined into one Godot process.** The next milestone is *actual
Godot 4.7.2 engine DisplayServer PS5 + GLES3 compatibility renderer*, not
another stand-alone shader demo. Keep existing PPSA99843 and PPSA99844
stable until integration hardware testing is successful.

See [integration contract](docs/DISPLAYSERVER_INTEGRATION.md) for
tracked engine APIs, EGL lifetime, GPL/MIT boundaries, and acceptance gates.

## October 22, 2026 PS5 hardware input acceptance passed

Real `v0.3.2` console logs confirm `PACK_SOURCE=BUNDLED_SMOKE`,
`GODOT_PS5_DUALSENSE_TEST_WAITING`,
`GODOT_PS5_DUALSENSE_CONNECTED`, and 38 actual GDScript
`GODOT_PS5_DUALSENSE_CROSS_PRESSED` messages, followed by
`GODOT_PS5_DUALSENSE_TEST_FINISHED`, `NATIVE_GODOT_RETURN=0`,
and clean shell exit. This verifies native PS5 pad → original Godot
Input → GDScript. It **does not** establish display/renderer/audio support.

A standalone PS5 GPU-probe scaffold is at `gpu-probe/`. It is
GPL-3.0-or-later, uses the existing DevBridge EGL/OpenGL adapter and keeps
the known-good `PPSA99843` runtime completely independent. Its CI artifact
has **now been verified on physical PS5 hardware** for EGL/GL clear/swap by the v0.1.5 color-screen test; Godot integration is still pending.

## First isolated GPU build (22 October 2026)

GitHub Actions [run 39767154442](https://github.com/Yahballon/tmp_lap/actions/runs/39767154442)
**PASSED**: isolated host tests, checksum-verified unofficial SDK 1.0.2
fetch, native PS5 cross-compile, link, SELF signature, and ZIP validation.
The separate [PPSA99844 test artifact](https://github.com/Yahballon/tmp_lap/actions/runs/39767154442/artifacts/12420847267)
is available for manual PS5 testing. This is still a **GPU clear/swap
probe only**, not a functional Godot DisplayServer. Its library provenance
is unverified beyond a pinned mirror SHA256 plus embedded manifest check.
Keep the verified headless Godot title PPSA99843 unchanged.

## Shader/triangle GPU proof passed on PS5 (2026-10-22)

User supplied a physical PS5 screenshot clearly showing the interpolated RGB
triangle on a colored framebuffer. Native shader-test log confirms OpenGL 4.6
core, GLSL 4.60, vertex and fragment compilation, program link,
`GL_GEOMETRY_READY`, `GL_FIRST_DRAW_ERROR=0`, `GL_TRIANGLE_SUBMITTED`,
`TOTAL_PRESENTED=645` and `CLEAN_SHUTDOWN`. Thus **actual shader
rasterization** is hardware-proven, not only clear/swap.

Next isolated test adds a procedurally generated RGBA8 checkerboard texture,
a moving UV-mapped quad, and conventional alpha blending. These are Godot 2D
renderer prerequisites, but **not yet a Godot renderer**. The next actual
integration still requires enabling and linking Godot's GLES3 compatibility
renderer and implementing a true PS5 DisplayServer that owns EGL presentation,
input/window methods, and render-thread context lifecycle.

## Firmware 5.10 graphics bring-up proven (2026-10-22)

User physically observed the blue, green and red fullscreen color transitions
and supplied a `graphics-probe.log` showing `EGL_OPEN_OK`,
`GL_VERSION=4.6 (Core Profile) Mesa 26.2.0`, `GL_RENDERER=PS5 AGC`,
`GLSL_VERSION=4.60`, `SURFACE_WIDTH=1920`,
`SURFACE_HEIGHT=1080`, `PAD_OPEN_OK`,
`FIRST_FRAME_PRESENTED`, `TOTAL_PRESENTED=1800`,
`CLEAN_SHUTDOWN`. This validates the EGL/GL clear/swap GPU path.
**No Godot renderer or visible Godot scene has been proven.**

Next safe hardware acceptance is a GLSL 4.60 vertex/fragment shader,
VAO/VBO geometry upload, GL link and draw, animated triangle, and clean
resource teardown in the same standalone GPU probe. The Godot GDScript
runtime title `PPSA99843` must remain independent.

## Current execution contract

The native Godot VM / GDScript / scene lifecycle is verified headlessly.
Experimental v0.3.0 adds external .pck selection and bundle fallback; this
is kernel-backed file discovery only, not a game browser or graphics backend.
The next acceptance test must launch an external PCK and show
`PACK_SOURCE=CONFIG` or `PACK_SOURCE=AUTOSCAN`, then verify the script
output and a clean PS5 shell exit. No renderer or pad support yet.

## Choose a real graphics path — two distinct options

**Candidate A: Godot Vulkan RenderingDevice.** Original Godot 4.7.2
sources: `drivers/vulkan/rendering_context_driver_vulkan.cpp`,
`drivers/vulkan/rendering_device_driver_vulkan.cpp` and
`drivers/vulkan/vulkan_hooks.cpp`. The port needs a real PS5
DisplayServer, a native Vulkan surface/swapchain bridge, function
dispatch without assuming a desktop Vulkan ICD, device features, shader
compilation, memory mapping, synchronization and teardown. Candidate
public graphics stacks to investigate:

- `mihawk-99/PS5_VulkanTemplate`: experimental Vulkan RADV-based PS5
  homebrew reference with framebuffer and pad examples; repository is MIT,
  **but third-party graphics components retain their own licenses**.
- `mpereiraesaa/ps5-vulkan`: experimental PS5 graphics/compute implementation;
  its static SDK is GPL-3.0 and **does not provide a conventional loader/ICD**.
  It requires compatibility work and GPL compliance if its library is linked.

**Candidate B: OpenGL compatibility renderer.** Godot's compatibility
renderer depends on a working OpenGL context + EGL window and Godot
DisplayServer integration. A live experimental PS5 EGL/OpenGL stack now exists at
[blackbearreloaded/ps5-opengl](https://github.com/blackbearreloaded/ps5-opengl),
with a published **OpenGL 4.6 SDK v1.0.2**, SDL2 bridge and native
1080p/1440p/4K display modes. Its own tests report native console results;
**these do not prove it works with Godot or firmware 5.10**. The stack is
**GPL-3.0-or-later** and includes dependencies with their own notices: do
not silently link its binaries into this currently MIT-licensed PS5 port
without an explicit compatible distribution/licensing decision. First
validate a separate GL/EGL display probe against one pinned release,
then assess Godot Compatibility RenderingDevice's API/context requirements
and core profile compatibility before enabling `opengl3=yes`. The current PS5 SCons target intentionally
sets `vulkan=no opengl3=no` to keep GDScript bring-up stable.

## Hardware-gated implementation steps

1. **Isolated GPU probe title** — verify a framebuffer/swapchain clear and
   present on the actual console, with an identifiable frame colour and
   clean Close Game behavior. Keep this separate from `PPSA99843` so the
   proven GDScript headless runtime is not regressed.
2. **DisplayServerPS5 minimal native API** — device/screen/window sizing,
   event pump, lifecycle, presentation, and renderer context ownership.
   Add validation for unimplemented virtual methods and fail at compile
   time rather than providing bogus successes.
3. **Godot 2D frame** — enable renderer in a separate experimental build,
   display an upstream Godot-generated scene, and verify visible motion
   at a stable refresh rate. Record a console screenshot and diagnostic
   `PRESENTED_FRAME` marker; a green CI build alone is insufficient.
4. **DualSense Input bridge** — create the real pad device, map pressed /
   released buttons plus analog axes to Godot Input, handle disconnect and
   reconnect, and verify events via a game scene (not just a raw pad poll).
5. **Audio + saves** — port PS5 AudioOut, buffer/latency handling,
   user:// writable directory behavior and crash-safe shutdown.
6. **First actual Godot game** — one small 2D project with animations,
   controls, audio, and persistent settings; only then attempt larger 3D
   content and renderer feature compatibility.

## Release discipline

- Never label headless GDScript success as graphical gameplay success.
- Keep `GODOT_PS5_SMOKE_READY` as a regression oracle.
- Continue signed `PPSA99843.zip` via GitHub Actions and TESTBUILDS only
  when link, packaging and signature tests pass.
- Keep graphics probe releases separate from the proven headless engine.
- Record which firmware and SDK commit each native witness used.
- Track license compliance for every linked graphics component and its
  transitive dependencies; no third-party GPU binaries or vendor SDK
  headers should be redistributed without a compatible license.

## Primary code and reference repositories

- [Godot Engine](https://github.com/godotengine/godot) — engine renderer
  and DisplayServer integration.
- [PS5 Vulkan Template](https://github.com/mihawk-99/PS5_VulkanTemplate)
  — experimental graphics/launcher examples (inspect exact versions).
- [ps5-vulkan](https://github.com/mpereiraesaa/ps5-vulkan) —
  experimental PS5 Vulkan implementation (GPL-3.0).
- [ps5link-sdk](https://github.com/Rufidj/ps5link-sdk) — PS5 GPU, VideoOut,
  and DualSense working examples; GPL-3.0.

## Graphics implementation decision (October 2026)

**Candidate chosen for first isolated PS5 framebuffer test:** the OpenGL
SDK v1.0.2 path, because the upstream release advertises a real EGL
context/SDL2 bridge and multiple tested native display modes. This is
**not** a claim that Godot's 2D renderer is already ported. Keep the existing
Godot headless `PPSA99843` operational while bringing up a separate
GPU-probe application; build and test against a frozen SDK hash. Do not
package any GPL graphics SDK binaries or source into the MIT port until
licensing and attribution are reviewed.

A later option is Mesa RADV/Vulkan 1.4 via
[mihawk-99/PS5_Vulkan](https://github.com/mihawk-99/PS5_Vulkan),
which reports native PS5 VideoOut/Winsys and Vulkan compliance test data.
That route still needs a Godot Vulkan RenderingDevice implementation and a
DisplayServer; it is not a substitute for a PS5-native surface/swapchain.

**Next PS5 firmware 5.10 acceptance steps:** (1) verify open pad bridge
through the `GODOT_PS5_DUALSENSE_CROSS_PRESSED` GDScript log; (2) in an
isolated graphics title, create EGL context and clear/swap one frame;
(3) add a true `DisplayServerPS5` implementation and platform rendering
hooks; (4) show a native Godot 2D scene with a visual screenshot and
controller interactions; (5) audio and project persistence.
