#!/usr/bin/env python3
"""Regression for fast real third-party Godot platformer PCK, distinct from M12b."""
from pathlib import Path
import hashlib
import importlib.util
import struct
import tempfile
import zipfile

root=Path(__file__).resolve().parents[1]/"samples/m12-platformer-2201"
fast=(root/"prepare_project_fast.py").read_text()
boot=(root/"PS5BootFast.gd").read_text()
controls=(root/"PS5ControlsFast.gd").read_text()
audio=(root/"AudioManagerFast.gd").read_text()
packer=(root/"pack_m12_fast.gd").read_text()
workflow=(root.parents[3]/".github/workflows/build-godot-ps5-m12c-fastboot.yml").read_text()
for needle in ("run/main_scene", "PS5BootFast.tscn", "config/icon",
               "unused_ctex_prefixes", "2D Platformer Starter Kit Splash.png-",
               "Icon.png-", "icon.svg-", "raw_count != 6", "GODOT_PS5_M12C_MANIFEST_LIGHT"):
    assert needle in fast,needle
assert 'pack_m12_fast.gd' in fast
assert 'PS5ControlsFast.gd' in fast
assert 'AudioManagerFast.gd' in fast
assert "M12C_LEVEL_LOAD_DONE duration_ms=" in boot
assert "GODOT_PS5_M12C_SCENE_SWITCH_REQUESTED" in boot
assert "ResourceLoader.load(ORIGINAL_LEVEL)" in boot
assert "GODOT_PS5_M12B_PROBE_BEGIN" not in boot
assert "GODOT_PS5_M12C_PLAYABLE_SCENE_READY total_ms=" in controls
assert "GODOT_PS5_M12C_AUDIO_LOAD_DONE duration_ms=" in audio
assert 'GODOT_PS5_M12C_PCK_WRITTEN' in packer
for marker in ["GODOT_PS5_M12C_GAMEPLAY_TEXTURES_ONLY","GODOT_PS5_M12C_LEVEL_LOAD_DONE",
               "GODOT_PS5_M12C_PLAYABLE_SCENE_READY",
               "GodotPS5-M12c-Platformer-FAST-PS5-TEST.zip"]:
    assert marker in workflow,marker
module_path=root/"package_platformer_fast.py"
spec=importlib.util.spec_from_file_location("fastplatformer",module_path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
with tempfile.TemporaryDirectory() as temp:
    d=Path(temp)
    original=b"GDPC"+struct.pack("<III",4,4,7)+bytes(131072)
    pck=d/module.PCK
    pck.write_bytes(original)
    license=d/"LICENSE"
    license.write_text("MIT License\nCopyright G2P Studios\n")
    result,digest=module.pack(pck,license,d/"out")
    assert digest==hashlib.sha256(original).hexdigest()
    with zipfile.ZipFile(result) as z:
        assert z.testzip() is None
        assert z.read("GodotPS5/launch.txt")==(module.PCK+"\n").encode()
        assert z.read("GodotPS5/games/"+module.PCK)==original
        assert b"MIT License" in z.read("GodotPS5/M12c-Platformer-Original-LICENSE.txt")
print("GODOT_PS5_M12C_FASTBOOT_STATIC_PASS")
