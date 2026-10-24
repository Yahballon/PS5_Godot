#!/usr/bin/env python3
"""Bundle ALL Godot PS5 SCons static libraries for native-link bring-up.

Do not confuse platform/libgodot_ps5.a (small entry-point shim) with the
entire Godot engine. This verifies and preserves core, main, scene, servers,
drivers, third-party and GDScript archives. No PS5 game is produced.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

DEFAULT_REQUIRED = (
    "bin/obj/core/libcore.",
    "bin/obj/main/libmain.",
    "bin/obj/drivers/libdrivers.",
    "bin/obj/scene/libscene.",
    "bin/obj/servers/libservers.",
    "bin/obj/platform/libplatform.",
    "bin/obj/modules/libmodule_gdscript.",
    "bin/libgodot_ps5.",
)

def bundle(build_root: Path, output: Path, min_archives: int = 50):
    root = build_root.resolve()
    bin_dir = root / "bin"
    if not bin_dir.is_dir():
        raise ValueError("Missing Godot bin/ directory")
    archives = sorted(
        (p for p in bin_dir.rglob("*.a") if p.is_file() and "ps5." in p.name),
        key=lambda p: p.relative_to(root).as_posix(),
    )
    if len(archives) < min_archives:
        raise ValueError(f"Only {len(archives)} PS5 static libs; need {min_archives}")
    names = [p.relative_to(root).as_posix() for p in archives]
    for required in DEFAULT_REQUIRED:
        if not any(n.startswith(required) for n in names):
            raise ValueError(f"Godot engine component missing: {required}")

    infos = []
    for path, name in zip(archives, names):
        if path.stat().st_size < 128:
            raise ValueError(f"Empty/tiny engine static archive: {name}")
        with path.open("rb") as stream:
            if stream.read(8) != b"!<arch>\n":
                raise ValueError(f"Not an AR static library: {name}")
            stream.seek(0)
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        infos.append({"path": name, "size_bytes": path.stat().st_size,
                      "sha256": digest})

    manifest = {
        "format": "godot-ps5-static-libs",
        "version": 1,
        "upstream": "godotengine/godot",
        "upstream_tag": "4.7.2-stable",
        "target": "x86_64-sie-ps5",
        "build_target": "template_debug",
        "status": "compile-only; no linked eboot.bin; no graphical or gameplay support",
        "archive_count": len(infos),
        "total_bytes": sum(i["size_bytes"] for i in infos),
        "archives": infos,
    }
    (root / "godot-ps5-full-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    # The file paths are relative to the *extracted package's root*.
    # Pass the response file to a linker from that directory and supply
    # PS5-DevBridge's CRT, imports and system SDK libs separately.
    linker_response = "\n".join([
        "--start-group", *names, "--end-group", ""
    ])
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=1, allowZip64=True) as z:
        for path, name in zip(archives, names):
            z.write(path, arcname=name)
        z.writestr("manifest.json", json.dumps(manifest, indent=2)+"\n")
        z.writestr("godot-link-libs.rsp", linker_response)
        z.writestr("READ_ME_FIRST.txt",
            "GODOT PS5 STATIC ARCHIVES - NOT A PS5 APP\n"
            "All upstream Godot 4.7.2 PS5 static components included.\n"
            "Use with PS5 DevBridge linker and runtime. The Godot engine\n"
            "has NOT been linked into an eboot.bin, and games cannot run.\n")
    with zipfile.ZipFile(output, "r") as z:
        if z.testzip() is not None:
            raise ValueError("Bundle ZIP CRC validation failed")
        check = json.loads(z.read("manifest.json"))
        if check["archive_count"] != len(archives):
            raise ValueError("Bundle manifest count mismatch")
    print(f"Packed {len(infos)} true PS5 static libraries "
          f"({manifest['total_bytes']:,} input bytes) into {output}")
    return manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("build_root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--min-archives", type=int, default=50)
    opts = parser.parse_args()
    bundle(opts.build_root, opts.output, opts.min_archives)
