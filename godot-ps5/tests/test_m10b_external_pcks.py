#!/usr/bin/env python3
"""M10b source and ZIP packaging regression only (not hardware acceptance)."""
from pathlib import Path
import hashlib
import importlib.util
import struct
import tempfile
import zipfile

root=Path(__file__).resolve().parents[1]
tiles=(root/"samples/m10b-tilemap/main.gd").read_text()
for expected in ("TileMapLayer.new()", "TileSetAtlasSource.new()", "TileSet.new()",
    "set.add_physics_layer()", "data.set_collision_polygon_points(0, 0",
    "layer.set_cell(", "mover.move_and_collide(", "target == layer",
    "GODOT_PS5_M10B_TILE_CONTACT_OK", "GODOT_PS5_M10B_TILE_TEST_PASS"):
    assert expected in tiles, expected
fonts=(root/"samples/m10b-font-ui/main.gd").read_text()
for expected in ("FontFile.new()", "load_dynamic_font(TEST_FONT_PATH)",
    "Label.new()", 'add_theme_font_override("font", test_font)',
    "GODOT_PS5_M10B_FONT_TTF_LOADED", "GODOT_PS5_M10B_LABEL_TREE_READY",
    "GODOT_PS5_M10B_FONT_TEST_FINISHED"):
    assert expected in fonts, expected

tool=root/"scripts/package_m10b_external_pcks.py"
spec=importlib.util.spec_from_file_location("m10b_packager",tool)
assert spec and spec.loader
packager=importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)

with tempfile.TemporaryDirectory() as tmp:
    td=Path(tmp)
    for name,(pck_name, zip_name) in packager.TESTS.items():
        pck=td/pck_name
        data=b"GDPC"+struct.pack("<III",3,4,7)+bytes(160)
        pck.write_bytes(data)
        target, digest=packager.bundle(name,pck,td/name)
        assert target.name==zip_name
        assert digest==hashlib.sha256(data).hexdigest()
        with zipfile.ZipFile(target) as z:
            assert z.testzip() is None
            assert z.read("GodotPS5/launch.txt")==(pck_name+"\n").encode()
            assert z.read("GodotPS5/games/"+pck_name)==data
        pck.write_bytes(b"FAKE"+bytes(160))
        try: packager.bundle(name,pck,td/name)
        except ValueError: pass
        else: raise AssertionError("invalid PCK accepted")
print("PASS M10b independent TileMap and Label source gates / two PS5 ZIP structures")
