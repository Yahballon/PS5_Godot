# Godot 4.7.2 → PS5 Homebrew: engineering status

## Source tree
- Upstream [godotengine/godot](https://github.com/godotengine/godot), pinned to tag `4.7.2-stable`.
- PS5 target triple from PS5-DevBridge: `x86_64-sie-ps5`.
- `engine/platform/ps5/` is an external SCons platform overlay.
- `scripts/build-engine.sh` initiates a REAL experimental cross-compile of the Godot core, GDScript modules and the PS5 headless entry. No fake minimal game interpreter.
- `GODOT_PS5_NATIVE_IO` enables PS5 libkernel directory and PCK-header discovery, avoiding sandbox-incompatible libc scanning. This does not replace Godot's internal `FileAccessUnix` / `DirAccessUnix` yet.

## Acceptance gates
1. CI cross-compile Godot's actual engine source and pinned third-party modules with the public SDK; fix compiler errors as seen in CI logs.
2. Link Godot static archives into a native DevBridge `eboot.bin` via real CRT/import stubs; confirm the start/exit logs on jailbroken PS5.
3. Register PS5-native file/directory backends within Godot itself. Merely finding a PCK with kernel functions does **not** make Godot able to open its resources.
4. Run `samples/script-smoke` exported PCK and observe `GODOT_PS5_SMOKE_READY` on console.
5. Implement real Godot DisplayServer and renderer; next DualSense + audio driver; validate 2D scene, then 3D.
6. Only then distribute a homebrew title with an icon, README screenshot and live games launcher. Do not add TESTBUILDS early.

## Experimental manual build
```sh
git clone --depth=1 --branch 4.7.2-stable https://github.com/godotengine/godot.git /tmp/godot
GODOT_SOURCE=/tmp/godot \
PS5_PAYLOAD_SDK=/path/to/PS5-DevBridge/templates/simple-calc/.deps/native/ps5-payload-sdk \
BUILD_JOBS=4 bash homebrew/godot-ps5/scripts/build-engine.sh
```
This script may fail in SDK/toolchain API incompatibilities until fixed through the cross-compile CI job. Do not label a static archive a working executable or playable emulator.

## Current limitations
No PS5 native app is linked, no Title ID, no real renderer or audio, no console runtime/screenshot, and no public gameplay release. GDExtension, C#, 3D Vulkan and per-game compatibility not claimed.

## PS5 POSIX compile compatibility

- `PTHREAD_NO_RENAME` disables optional POSIX thread naming because the PS5 SDK lacks the expected `pthread_setname_np` signature.
- `compat.cpp` defines `getentropy()` using FreeBSD `sysctl(CTL_KERN,KERN_ARND)`. It returns an explicit error if secure kernel randomness is unavailable; no predictable PRNG fallback.
- `compat.h` is pre-included by the Godot PS5 platform C/C++ compiler settings so upstream Unix code can compile unchanged. This is not evidence of the shim working in a PS5 app sandbox; native testing and link import validation are pending.


## First full upstream PS5 cross-compile (verified)

The PR build at [GitHub Actions run 39638963254](https://github.com/Yahballon/tmp_lap/actions/runs/39638963254)
successfully cross-compiled **58** static archive components for the target
`x86_64-sie-ps5` using Godot 4.7.2 on CI. This **does not mean gameplay works**.
A packaging defect only uploaded the small `bin/libgodot_ps5.*.a` shim.
The new `scripts/package_static_engine.py` gathers the whole SCons
`bin/obj` tree (including core, scene, servers, main, drivers and GDScript),
adds SHA-256 verification and a response file for a future native link,
and rejects missing or corrupt component archives.

The package remains **a toolchain artifact**, not a console-installable ZIP.
A complete link into DevBridge's `eboot.bin`, PS5 runtime initialization,
and the actual `GODOT_PS5_SMOKE_READY` PS5 log remain outstanding.

## Hardware confirmation from Godot PS5 Probe v0.1.0

Console diagnostic `PPSA99842` showed `smoke.pck` under
`/mnt/usb0/godot/smoke.pck`, and the console log reported
`PCK_READ_OK` after a DualSense X press. This validates standalone
header discovery with PS5 libkernel I/O and the diagnostic renderer.
It **does not** mean `FileAccessUnix`, `DirAccessUnix`, GDScript or
other runtime components have been exercised on console.

## Native engine link integration (new)

The PS5 diagnostic already confirmed native `getdents` and PCK header reads
on hardware. The next test is a **different PS5 title**, `PPSA99843`,
that invokes `godot_ps5_run_pack()` from the *original compiled Godot
engine* instead of a PCK header-only checker.

The CI job in `.github/workflows/build-godot-ps5.yml` now:

- Cross-compiles Godot 4.7.2 and verifies every archive is present.
- Generates a manifest listing static libraries and their SHA-256 hashes.
- Stages all archives in a PS5-DevBridge native app, adds `--start-group`
  and `--end-group` to resolve interdependent engine components.
- Copies a genuine Godot 4 GDScript smoke PCK into
  `/app0/assets/godot/smoke.pck` to avoid USB I/O complicating the very
  first engine-execution test.
- Attempts a **real signed native PS5 link**, retains linker diagnostics,
  and builds `PPSA99843.zip` *only if the linker succeeds*.

If a working headless installer is produced, PS5 hardware validation must
check `/data/GodotPS5/engine-smoke.log`,
`/data/GodotPS5/engine-stdout.log`, and
`/data/GodotPS5/engine-stderr.log`. The critical acceptance condition
is observing the Godot GDScript output `GODOT_PS5_SMOKE_READY`
**on the console**. A successful linker output or archive build is not that
test. There is still no native Godot DisplayServer, renderer, or audio driver.

Do **not** add PPSA99843 to TESTBUILDS until the build is verified and
clearly labeled as an engine smoke test; never describe it as a playable
Godot game port before hardware testing.
