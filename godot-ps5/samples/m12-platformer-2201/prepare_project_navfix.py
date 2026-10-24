#!/usr/bin/env python3
"""M12d PS5 asset #2201: disable unused TileMapLayer NavigationServer2D.

Real physical PS5 log (30): 332 navigation_map.is_null() stderr errors,
plus a 22.5 second Level_01 instantiation stall after PCK resource load.
Original game uses TileMapLayer *physics* only, no NavigationAgent2D.
Godot 4.7.2 TileMapLayer has separate navigation_enabled and
physics_enabled; turning off navigation leaves collisions intact.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
import shutil
import prepare_project_fast as fast

SOURCE=Path(__file__).resolve().parent
LEVELS=("Level_01.tscn", "Level_02.tscn")
LAYER_NAMES=("Ground", "Traps")

def disable_navigation(project: Path) -> None:
    # Only authored scene TileMapLayers, never remove their TileSet physics.
    count=0
    for filename in LEVELS:
        path=project/"Scenes"/"Levels"/filename
        data=path.read_text(encoding="utf-8")
        for label in LAYER_NAMES:
            rgx=rf'(?m)^(\[node name="{label}" type="TileMapLayer"[^\n]*\]\n)'
            matches=list(re.finditer(rgx,data))
            if len(matches)!=1:
                raise RuntimeError(f"{filename}: expected exactly one {label} TileMapLayer; found {len(matches)}")
            header_end=matches[0].end()
            if not data[header_end:].startswith("navigation_enabled = false\\n"):
                data=data[:header_end] + "navigation_enabled = false\\n" + data[header_end:]
            count+=1
        if 'tile_set = SubResource(' not in data or 'physics_layer_0/collision_layer = 1' not in data:
            raise RuntimeError(f"{filename}: physics collisions unexpectedly missing")
        path.write_text(data,encoding="utf-8")
    if count != 4:
        raise RuntimeError("All four tile layers must have navigation disabled")
    print("GODOT_PS5_M12D_NAV_DISABLED layers=4 scenes=2 physics=preserved")

def prepare(project: Path) -> None:
    fast.prepare(project)
    disable_navigation(project)
    shutil.copy2(SOURCE/"PS5ControlsSmooth.gd", project/"PS5Controls.gd")
    shutil.copy2(SOURCE/"pack_m12_navfix.gd", project/"pack_m12.gd")
    print("GODOT_PS5_M12D_SMOOTH_PROJECT_PREPARED",fast.ASSET_COMMIT)

def manifest(project: Path) -> None:
    # Preserve all six native PS5-compatible uncompressed sprite textures.
    pack=project/"m12d-platformer-asset2201.pck"
    if pack.exists():
        pack.unlink()
    fast.manifest(project)
    data=(project/"ps5_m12_manifest.txt").read_text()
    assert "m12d-platformer-asset2201.pck" not in data
    print("GODOT_PS5_M12D_MANIFEST_OK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("command",choices=("prepare","manifest"))
    p.add_argument("project",type=Path)
    a=p.parse_args()
    target=a.project.resolve()
    prepare(target) if a.command=="prepare" else manifest(target)
