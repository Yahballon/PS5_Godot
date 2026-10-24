# M11c → M11d – Native PS5 Godot AudioOut (v0.1.6 HARDWARE CONFIRMED)

**M11d hardware result (23 October 2026): ✅ AUDIBLE NATIVE PS5 AUDIO AND X REPLAY CONFIRMED** on signed PPSA99847 v0.1.6. The user listened to the actual six tones and triggered successful DualSense X replay. Console archive `bfpilot-download (27).tar` shows a successful final run with `GODOT_PS5_M11D_AUDIOOUT_THREAD_STARTED`, `AUDIOOUT_READY rate=48000 channels=2 frames=256`, two `OUTPUT_OK` markers, **9 X replays**, and `AUDIOOUT_CLOSE rc=0 blocks=2831 errors=0`. Runtime confirms `GODOT_RETURN=0`, `NORMAL_SHUTDOWN`, and `EGL_CLOSED`. Signed [build #39924377575](https://github.com/Yahballon/tmp_lap/actions/runs/39924377575), [merged PR #249](https://github.com/Yahballon/tmp_lap/pull/249), audio implementation [issue #247 CLOSED](https://github.com/Yahballon/tmp_lap/issues/247). Known limitation: third-party Godot game compatibility, long-running streams and alternate formats have not yet been independently verified.

**Root cause of the older v0.1.5 silence:** Godot 4.7.2 `Thread::start` returns a **Thread::ID**, not an Error. The initial audio code compared a nonzero successful ID to `OK=0`, incorrectly closed the real AudioOut handle and fell back to the dummy driver. M11d uses `thread.start(...); if (!thread.is_started())` and repairs unsupported `%llu` log formatting. Historical v0.1.5 errors in the cumulative TAR are not present in the successful last v0.1.6 session.

The user's PS5 M11a hardware test created real 529,200-byte PCM and started AudioStreamPlayer but was SILENT. Godot OS_PS5 registered no real AudioDriver, leaving a dummy sink.

## Implementation

- Opt-in AudioDriverPS5 derives from original Godot 4.7.2 AudioDriver and registers with AudioDriverManager before Main::setup.
- A dedicated worker thread calls Godot audio_server_process for 256 frames at 48 kHz stereo. It converts 32-bit signed fixed-point mixer samples to interleaved 16-bit and submits to sceAudioOutOutput.
- The blocking AudioOut kernel call occurs only AFTER unlocking Godot's audio mixer mutex; there is no fake tone playback, audio file export or rumble workaround.
- The public PS5 payload SDK-generated libSceAudioOut.so stub is used for native imports; no proprietary Sony runtime binary is included.
- GODOT_PS5_AUDIOOUT=1 is opt-in for PPSA99847 v0.1.5 only. Known-good v0.1.4 physics, graphics, fonts and savegames remain the rollback build.

## Native CI

https://github.com/Yahballon/tmp_lap/actions/workflows/build-godot-ps5-m11c-native-audioout.yml

The workflow must validate a real compiled AudioDriverPS5, verify the public SDK audio import stub exists, link the real Godot engine with Physics2D + FreeType + GLES3, and only upload a signed installer ZIP if all package checks pass (PPSA99847 metadata content version 01.000.006). Passing host tests is NOT proof that audio is audible on console.

## PS5 acceptance

1. Install the signed v0.1.5 experimental test build when CI passes (retain v0.1.4 for rollback).
2. Keep /data/GodotPS5/games/m11-audio.pck and select it by putting m11-audio.pck in /data/GodotPS5/launch.txt.
3. Start the app, LISTEN for six notes and press X to replay. Real TV/headphone output must be heard to accept M11c.
4. Collect gles3-stdout.log, gles3-stderr.log and gles3-runtime.log, including driver registered/open/output diagnostics and any negative native AudioOut error codes.
5. Require nonnegative AudioOut handle, successful block writes, actual audible sound, clean GODOT_RETURN=0 and EGL_CLOSED. AUDIO_PLAYER_STARTED alone does not prove working sound.

Known probe ABI: sceAudioOutOpen user 0xff, port type 0, index 0, 256 frames, 48000 Hz, stereo signed 16-bit format 1. References: https://github.com/Rufidj/PS5_DEV_HOMEBREW/blob/main/ps5_sdk/ps5_sdk_audio_helpers.h and https://github.com/ps5-payload-dev/sdk/blob/master/sce_stubs/libSceAudioOut.c.

Status: M11c PS5 audibility remains OPEN pending native CI and real PS5 test. GitHub issue #247.