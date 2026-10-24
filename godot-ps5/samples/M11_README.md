# M11 – Real Godot Audio API and Restart-Persistent Saves (PS5)

Two **independent Godot 4.7.2 PCKs** for previously console-tested
**PPSA99847 v0.1.4**. No new native eboot; each package only adds one
game under `/data/GodotPS5/games/` and switches `launch.txt`.

## M11a: AudioStreamPlayer

`m11-audio.pck` creates a real Godot `AudioStreamWAV` (44.1 kHz
16-bit PCM) with six audible notes and plays it with `AudioStreamPlayer`.
Cyan/green audio bars appear. Press X to replay the notes.

**Audibility is the acceptance criterion.** A green headless CI and
`GODOT_PS5_M11_AUDIO_PLAYER_STARTED` prove only the engine API reached the
playback state. Godot may use a dummy AudioDriver on this PS5 port.
They do NOT prove that TV speakers or headphones can produce sound.

The console tester should explicitly report whether the ascending notes
are **audible**. Also collect `gles3-stdout.log`,
`gles3-stderr.log`, and `gles3-runtime.log`.

## M11 real PS5 results and fixed visible save PCK (23 October 2026)

The user's `bfpilot-download (24).tar` confirms **NO AUDIBLE AUDIO**:
original Godot `AudioStreamPlayer` successfully reached the play state
but the PS5 platform has no implemented native audio output driver.
Development/acceptance is tracked in [M11c issue #247](https://github.com/Yahballon/tmp_lap/issues/247).

The same archive has **two save runs** with successful writes/readbacks
but both incorrectly identified as first launch; the actual archive
contains valid `userdata/GodotPS5M11Saves/m11-save-v1.txt`.
Upstream `FileAccessUnix::file_exists()` uses `stat/access`, which is
unreliable on PS5. **Do not delete the data or infer a write failure.**

**M11b2 repair**: new `samples/m11-saves-v2` PCK, available as
`GodotPS5-M11b2-SAVES-VISIBLE-FIX.zip`. It directly attempts
`FileAccess.open(READ)` *before any write*, accepts only a genuine
not-found error as first launch, protects corrupt/unreadable data, and
shows readable TrueType labels: cyan FIRST SAVE CREATED or green
SAVE RESTORED with previous/new counts. Host CI [#39913555804](https://github.com/Yahballon/tmp_lap/actions/runs/39913555804)
passed two independent processes (`new=1` then `old=1 new=2`).
Requires unchanged `PPSA99847 v0.1.4`. Preserve the save path and
install new PCK + `launch.txt` only. Native PS5 persistence acceptance
**still OPEN** pending green on-screen report plus console logs.

## M11b: user:// Savegame Persistence

`m11-saves.pck` writes a small versioned/checksummed save in a private
`user://m11-save-v1.txt` file. It immediately reopens and byte-verifies
the write. **You MUST run the app twice, in two independent launches:**

1. On first launch the display turns **cyan** and stdout should show
   `GODOT_PS5_M11_SAVE_FIRST_LAUNCH_PASS new=1` and
   `GODOT_PS5_M11_SAVE_VERIFY_READBACK_OK`.
2. Fully exit the PS5 homebrew, then start it again with the SAME
   `launch.txt`. The screen should become **green** and stdout should show
   `GODOT_PS5_M11_SAVE_PERSIST_OK previous=1` and
   `GODOT_PS5_M11_SAVE_RESTART_PERSISTENCE_PASS old=1 new=2`.
3. A third launch increments the counter again. Existing save data
   is deliberately never overwritten with a fake success message.

The PS5 FileAccess layer currently implements kernel-backed **reads**
but delegates **writes** to Unix libc. If the console test reports
`GODOT_PS5_M11_SAVE_WRITE_UNAVAILABLE`, that is a genuine native
compatibility bug requiring a separate eboot fix. Do not mark persistence
supported based on the successful host CI.

**No automatic deletion of old or unrelated user data** is performed.
This uses Godot's own per-project `user://` namespace.

## Build and test artifacts

[GitHub Actions](https://github.com/Yahballon/tmp_lap/actions/workflows/build-godot-ps5-m11-audio-saves.yml)
runs genuine Godot 4.7.2 and refuses to create an artifact unless:
- M11a has valid PCM and the actual Godot AudioStreamPlayer starts.
- M11b actually writes and reopens a save in the first Godot process,
  then a **separate second Godot process** reads the persisted data and
  increments it. This avoids confusing temporary RAM state with disk saves.

The artifact contains two separate ZIPs:

- `GodotPS5-M11a-AUDIO-TEST.zip`
- `GodotPS5-M11b-SAVES-TEST.zip`

Extract ONE inner ZIP, copy its `GodotPS5/` contents to
`/data/GodotPS5/` and run PPSA99847 v0.1.4.
Repeat with the other ZIP afterward. Each ZIP replaces `launch.txt`,
so always reinstall/reselect the saves PCK before the second save launch.

Logs: `/data/GodotPS5/gles3-stdout.log`,
`gles3-stderr.log`, `gles3-runtime.log`. Inspect marker segments by
launch rather than old accumulated warnings.

**Physical PS5 acceptance stays OPEN** until there is an actual audio
hearing report and a two-launch save persistence result. A successful
host build is not general audio or write compatibility proof.

To restore bundled Pong, remove `/data/GodotPS5/launch.txt`.
