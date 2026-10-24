#!/usr/bin/env python3
"""Adapt the pinned MIT Godot Asset Library #2201 to an external PS5 PCK.

Never alter original upstream player/physics/audio/level code. Only augment
DualSense actions, renderer settings, and tutorial labels.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil

ASSET_COMMIT = "a48fc994cbcb168be472df84f2e13b55d2a2792f"
ASSET_REPO = "https://github.com/AdilDevStuff/2D-Platformer-Starter-Kit"
SOURCE = Path(__file__).resolve().parent

def prepare(project: Path) -> None:
    # PS5 hardware diagnostic bfpilot-download (28).tar:
    # platformPack_tilesheet.png and all other .ctex assets failed at
    # compressed_texture.cpp:343 because PS5 Godot has no usable PNG/WebP
    # Image unpacker. Original .png.import uses compress/mode=0 (lossless
    # PNG or WebP payload). Mode 3 is upstream 'VRAM Uncompressed':
    # CompressedTexture2D::DATA_FORMAT_IMAGE stores raw Image pixel data,
    # requiring NO PNG, WebP, BasisU, or GPU block decompressor on PS5.
    import_files = sorted([*project.rglob("*.png.import"), *project.rglob("*.svg.import")])
    if not import_files:
        raise RuntimeError("Original Godot PNG/SVG texture import descriptors not found")
    for import_file in import_files:
        cfg = import_file.read_text(encoding="utf-8")
        if 'importer="texture"' not in cfg or "compress/mode=0" not in cfg:
            raise RuntimeError("Unexpected Godot image import config: " + str(import_file))
        cfg = cfg.replace("compress/mode=0", "compress/mode=3")
        import_file.write_text(cfg, encoding="utf-8")
    print("GODOT_PS5_M12B_RAW_TEXTURE_IMPORT_SET files=", len(import_files))
    config = project / "project.godot"
    raw = config.read_text(encoding="utf-8")
    assert 'config_version=5' in raw
    assert 'run/main_scene="res://Scenes/Levels/Level_01.tscn"' in raw
    assert 'GameManager="*res://Scripts/GameManager.gd"' in raw
    assert '[autoload]' in raw
    assert 'config/features=PackedStringArray("4.7", "Forward Plus")' in raw
    raw = raw.replace(
        'config/features=PackedStringArray("4.7", "Forward Plus")',
        'config/features=PackedStringArray("4.7", "GL Compatibility")')
    # Native PS5 Godot was compiled with GLES3/Compatibility, not Vulkan.
    raw += (
        '\n; PS5 external PCK only: original game uses Godot Compatibility renderer.\n'
        '[rendering]\n'
        'renderer/rendering_method="gl_compatibility"\n'
        'renderer/rendering_method.mobile="gl_compatibility"\n'
    )
    raw = raw.replace('[autoload]\n', '[autoload]\n\n'
        'PS5Controls="*res://PS5Controls.gd"\n', 1)
    # Load a tiny visible diagnostic scene first. The initial upstream boot
    # splash could remain on PS5 forever with no indication of which asset
    # stalled while building Level_01. Disable it and defer heavy resources.
    raw = raw.replace(
        'run/main_scene="res://Scenes/Levels/Level_01.tscn"',
        'run/main_scene="res://PS5Boot.tscn"')
    raw = raw.replace(
        'boot_splash/image="res://Assets/Splash/2D Platformer Starter Kit Splash.png"',
        'boot_splash/show_image=false')
    raw = raw.replace(
        'SceneTransition="*res://Scenes/Managers/SceneTransition.tscn"',
        'SceneTransition="*res://SceneTransitionPS5.gd"')
    raw = raw.replace(
        'AudioManager="*res://Scenes/Managers/AudioManager.tscn"',
        'AudioManager="*res://AudioManagerPS5.gd"')
    # The boot splash and game icons are not used after launch and make up
    # >9 MiB (70%) of M12b raw .ctex payload. Do not ask Godot to import
    # or load them in the external console-focused game.
    raw = raw.replace('config/icon="res://Icon.png"', '')
    raw = raw.replace('run/main_scene="res://PS5Boot.tscn"',
                      'run/main_scene="res://PS5BootFast.tscn"')
    assert 'run/main_scene="res://PS5BootFast.tscn"' in raw
    assert 'config/icon="res://Icon.png"' not in raw
    assert 'boot_splash/show_image=false' in raw
    assert 'SceneTransition="*res://SceneTransitionPS5.gd"' in raw
    assert 'AudioManager="*res://AudioManagerPS5.gd"' in raw
    config.write_text(raw, encoding="utf-8")
    shutil.copy2(SOURCE / "PS5ControlsFast.gd", project / "PS5Controls.gd")
    shutil.copy2(SOURCE / "pack_m12_fast.gd", project / "pack_m12.gd")
    for name in ["PS5BootFast.gd", "PS5BootFast.tscn", "SceneTransitionPS5.gd"]:
        shutil.copy2(SOURCE / name, project / name)
    shutil.copy2(SOURCE / "AudioManagerFast.gd", project / "AudioManagerPS5.gd")
    # Replace desktop-only tutorial hints; preserve the actual level scenes.
    level1 = project / "Scenes/Levels/Level_01.tscn"
    scene = level1.read_text(encoding="utf-8")
    original = 'A & D To Move\nSpacebar To Jump'
    assert original in scene, "Original Level_01 tutorial text changed"
    scene = scene.replace(original, 'LEFT STICK / D-PAD\nX TO JUMP')
    level1.write_text(scene, encoding="utf-8")
    print("GODOT_PS5_M12_UPSTREAM_PREPARED", ASSET_COMMIT)
    print("GODOT_PS5_M12B_VISIBLE_BOOT_PREPARED", ASSET_COMMIT)
    print("GODOT_PS5_M12C_FASTBOOT_PREPARED", ASSET_COMMIT)

def manifest(project: Path) -> int:
    imported = project / ".godot/imported"
    if not imported.is_dir() or not any(imported.iterdir()):
        raise RuntimeError("headless Godot editor did NOT import images, fonts and WAV: cannot package unimported game")
    files = []
    excluded_unused_raw_bytes = 0
    # Confirmed against original Level_01/Level_02/Coin/Player .tscn:
    # Splash.png, Icon.png and icon.svg are unreferenced by gameplay scenes.
    # Their VRAM-uncompressed imports take ~9.3 MiB of M12b's 13.3 MiB PCK.
    # Exclude only these three non-game textures, preserving six gameplay .ctex.
    unused_icon_files = {"Icon.png", "Icon.png.import", "icon.svg", "icon.svg.import"}
    unused_ctex_prefixes = ("2D Platformer Starter Kit Splash.png-",
                           "Icon.png-", "icon.svg-")
    for file in sorted(project.rglob("*")):
        if not file.is_file():
            continue
        relative = file.relative_to(project)
        if relative.parts[0] == ".git":
            continue
        if relative.as_posix().startswith("Assets/Splash/"):
            excluded_unused_raw_bytes += file.stat().st_size
            continue
        if relative.name in unused_icon_files:
            excluded_unused_raw_bytes += file.stat().st_size
            continue
        if relative.parts[:2] == (".godot", "imported") and relative.name.startswith(unused_ctex_prefixes):
            excluded_unused_raw_bytes += file.stat().st_size
            continue
        if relative.name in ("m12-platformer-asset2201.pck", "m12b-platformer-asset2201.pck", "m12c-platformer-asset2201.pck", "ps5_m12_manifest.txt"):
            continue
        # Editor shader cache and internal per-host binary data are not game assets.
        if relative.parts[:2] == (".godot", "editor"):
            continue
        if relative.parts[:2] == (".godot", "shader_cache"):
            continue
        if relative.parts[:2] == (".godot", "mono"):
            continue
        if relative.suffix in (".tmp", ".lock"):
            continue
        files.append(relative.as_posix())
    import struct
    raw_count = 0
    for rel in files:
        if not rel.endswith(".ctex"):
            continue
        blob = (project / rel).read_bytes()
        if len(blob) < 48 or blob[:4] != b"GST2":
            raise RuntimeError("Bad native CompressedTexture2D header: " + rel)
        payload_format = struct.unpack_from("<I", blob, 36)[0]
        if payload_format != 0:
            raise RuntimeError("PS5-incompatible PNG/WebP/Basis texture payload " + rel + " = " + str(payload_format))
        raw_count += 1
    print("GODOT_PS5_M12B_RAW_CTEXTURES_VERIFIED", raw_count)
    print("GODOT_PS5_M12C_GAMEPLAY_TEXTURES_ONLY count=", raw_count,
          " excluded_unused_bytes=", excluded_unused_raw_bytes)
    if raw_count != 6:
        raise RuntimeError("Expected exactly six real gameplay textures after excluding three unused boot/icon atlases")
    if raw_count < 6:
        raise RuntimeError("Expected at least six PS5-compatible raw textures")
    if not any(x.endswith(".ctex") for x in files):
        raise RuntimeError("No imported Godot .ctex textures found")
    if not any(x.endswith(".sample") for x in files):
        raise RuntimeError("No imported Godot .sample WAV effects found")
    if not any(x.endswith(".fontdata") or x.endswith(".fontdata") for x in files):
        # Native TTF can be loaded directly; no need to fail if no fontdata.
        print("GODOT_PS5_M12_FONT_DIRECT_TTF")
    (project / "ps5_m12_manifest.txt").write_text("\n".join(files) + "\n", encoding="utf-8")
    print("GODOT_PS5_M12_MANIFEST_OK", len(files))
    print("GODOT_PS5_M12C_MANIFEST_LIGHT", len(files))
    return len(files)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare", "manifest"])
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.project.resolve())
    else:
        manifest(args.project.resolve())
