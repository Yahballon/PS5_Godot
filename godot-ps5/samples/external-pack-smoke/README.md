# Godot PS5 M8: external PCK + scene/asset acceptance

This is a **separate Godot 4.7.2 project** for testing the real
Godot GLES3/Canvas2D engine in `PPSA99847`, **without rebuilding the PS5
native executable**. It packages two Godot scenes, two GDScripts and
`res://palette.json` into `external-smoke.pck`.

## Verified host build (23 October 2026)

**PASS** — [M8c GitHub Actions run #39866584380](https://github.com/Yahballon/tmp_lap/actions/runs/39866584380) completed successfully, including real Godot 4.7.2 pack generation, headless execution of both scenes with asset reading, bundle tests and artifact publication. CI artifact: [`Godot-PS5-M8c-External-PCK-PS5-READY-HOST-TESTED`](https://github.com/Yahballon/tmp_lap/actions/runs/39866584380/artifacts/12464481166). Real PCK 4,828 bytes; SHA-256 `137f4c5722e385c04c4f36a84fcd8548e5038a348f68d91ca2c3310c21527591` confirmed in the extracted PS5 installation ZIP. Dedicated acceptance [PR #235](https://github.com/Yahballon/tmp_lap/pull/235) merged into the development branch.

**PS5 hardware acceptance (23 October 2026): USER CONFIRMED.** After installing the external PCK and running the unmodified `PPSA99847 v0.1.2`, the user reported that **both scenes and the X-driven color change work exactly as intended**. This independently establishes real console behavior beyond green host CI. No separate `gles3-*` logs/video from this M8c run were attached, so FPS metrics, exact log markers and native clean shutdown are not independently measured. No new native binary was required.

## Build / download

Open [Build External Godot PS5 PCK](https://github.com/Yahballon/tmp_lap/actions/workflows/build-godot-ps5-external-pck.yml)
and download the **Godot-PS5-M8c-External-PCK-PS5-READY-HOST-TESTED**
artifact from a **successful branch push run**. The workflow is stored on
the feature branch, so the GitHub **Run workflow** button may not appear
until the workflow is also present on the default branch. The feature
branch's pushes run it automatically.

The downloadable Actions artifact contains:

- `GodotPS5-M8c-External-PCK-PS5-TEST.zip` — unpack this nested starter ZIP;
  it already contains the correct `/data/GodotPS5/` directory layout,
  `launch.txt`, `games/external-smoke.pck`, a SHA-256 checksum and instructions.
- `external-smoke.pck` — standalone PCK for custom path/USB testing.

The workflow uses **official Godot 4.7.2** to generate the actual PCK,
loads that PCK in a host/headless runtime, checks scene/asset and clean
completion markers, then checks its ZIP and PCK header. **Green CI does not
prove PS5 hardware compatibility.**

Or use official Godot 4.7.2 on a PC:

```sh
godot --headless --path homebrew/godot-ps5/samples/external-pack-smoke \
      --script res://make_pack.gd
```

## Hardware test (PS5)

1. Install `PPSA99847 v0.1.2` from TESTBUILD; this is the existing native runner.
2. Extract the `GodotPS5-M8c-External-PCK-PS5-TEST.zip` inside the Actions
   artifact. Copy its `GodotPS5/` **contents** into `/data/GodotPS5/`.
   The ZIP supplies these two files automatically:

   ```text
   /data/GodotPS5/launch.txt
   /data/GodotPS5/games/external-smoke.pck
   ```

3. Verify `/data/GodotPS5/launch.txt` contains `external-smoke.pck` on its
   first line. Alternatively put the standalone PCK in
   `/mnt/usb0/godot/external-smoke.pck` and write that *full absolute path*
   in `launch.txt`.
4. Launch PPSA99847. The first screen is a magenta ring on a deep-blue
   background. After 180 frames (about 3 s at 60 fps) it becomes a cyan
   circle around a dark square; after 240 more frames the app exits.
   Press **X** during either scene for a visible color change.
5. Inspect `/data/GodotPS5/gles3-runtime.log` for
   `PACK_SOURCE=CONFIG PACK=/data/GodotPS5/games/external-smoke.pck`,
   `GODOT_SWAP_FIRST`, `GODOT_RETURN=0`, `NORMAL_SHUTDOWN`,
   `EGL_CLOSED`.
6. Inspect `gles3-stdout.log` for
   `GODOT_PS5_EXTERNAL_MAIN_READY`,
   `GODOT_PS5_EXTERNAL_ASSET_OK`,
   `GODOT_PS5_EXTERNAL_SCENE_CHANGE_REQUESTED`,
   `GODOT_PS5_EXTERNAL_SECOND_SCENE_READY`,
   `GODOT_PS5_EXTERNAL_FINISHED`.
   `GODOT_PS5_EXTERNAL_GAMEPAD_X` or
   `GODOT_PS5_EXTERNAL_SECOND_SCENE_GAMEPAD_X` confirms the input test.
   Save `gles3-stderr.log` too.
7. **Remove launch.txt** to go back to the bundled Pong demo; the PCK
   may remain installed. An invalid file falls back to bundled Pong.

A failure to open the JSON file, load the second scene, or exit cleanly
is useful diagnostic evidence. Neither this fixture nor green CI proves
general third-party Godot compatibility, fonts, physics, audio or saving.
