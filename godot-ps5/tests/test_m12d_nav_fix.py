#!/usr/bin/env python3
"""M12d PS5 regression: real native TileMapLayer navigation OFF, collision ON.

Real PS5 TAR #30 has 332 navigation_map.is_null() errors and 22.5 sec
during scene tree initialization. Keep original physics and gameplay.
"""
from pathlib import Path
import hashlib,importlib.util,sys,tempfile,zipfile,struct
root=Path(__file__).resolve().parents[1]/"samples/m12-platformer-2201"
sys.path.insert(0,str(root))
import prepare_project_navfix as opt
prep=(root/"prepare_project_navfix.py").read_text()
controls=(root/"PS5ControlsSmooth.gd").read_text()
packer=(root/"pack_m12_navfix.gd").read_text()
for marker in ("navigation_enabled = false", "LEVELS=", "LAYER_NAMES=",
               "GODOT_PS5_M12D_NAV_DISABLED", "GODOT_PS5_M12D_MANIFEST_OK"):
    assert marker in prep,marker
assert 'shutil.copy2(SOURCE/"PS5ControlsSmooth.gd"' in prep
assert "GODOT_PS5_M12D_NAV_DISABLED_CONFIRMED" in controls
assert "GODOT_PS5_M12D_FRAME_HITCH" in controls
assert "GODOT_PS5_M12D_FRAME_5S" in controls
assert "GODOT_PS5_M12C_PLAYABLE_SCENE_READY" in controls
assert "navigation_enabled" in controls
assert "collision_enabled" in controls
assert "m12d-platformer-asset2201.pck" in packer
assert "GODOT_PS5_M12D_PCK_WRITTEN" in packer
with tempfile.TemporaryDirectory() as tmp:
    proj=Path(tmp)
    lv=proj/"Scenes"/"Levels"
    lv.mkdir(parents=True)
    sample='[sub_resource type="TileSet" id="TileSet_1"]\nphysics_layer_0/collision_layer = 1\n[node name="Ground" type="TileMapLayer" parent="Level"]\ntile_set = SubResource("TileSet_1")\n[node name="Traps" type="TileMapLayer" parent="Level"]\ntile_set = SubResource("TileSet_1")\n'
    for name in opt.LEVELS:
        (lv/name).write_text(sample)
    opt.disable_navigation(proj)
    for name in opt.LEVELS:
        text=(lv/name).read_text()
        assert text.count("navigation_enabled = false")==2, name
        assert text.count('tile_set = SubResource(')==2
        assert 'physics_layer_0/collision_layer = 1' in text
    before={name:(lv/name).read_text() for name in opt.LEVELS}
    opt.disable_navigation(proj)
    after={name:(lv/name).read_text() for name in opt.LEVELS}
    assert before==after, "Navigation transform must be idempotent"
    pack=root/"package_platformer_navfix.py"
    spec=importlib.util.spec_from_file_location("m12d_package",pack)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    f=proj/module.PCK
    b=b"GDPC"+struct.pack("<III",4,4,7)+bytes(130000)
    f.write_bytes(b)
    license=proj/"LICENSE";license.write_text("MIT License\nCopyright upstream\n")
    z,sha=module.pack(f,license,proj/"out")
    assert sha==hashlib.sha256(b).hexdigest()
    with zipfile.ZipFile(z) as zipf:
        assert zipf.testzip() is None
        assert zipf.read("GodotPS5/launch.txt")==(module.PCK+"\n").encode()
        assert zipf.read("GodotPS5/games/"+module.PCK)==b
        assert b"MIT License" in zipf.read("GodotPS5/M12d-Platformer-Original-LICENSE.txt")
print("GODOT_PS5_M12D_STATIC_NAV_AND_PACKAGE_PASS")
