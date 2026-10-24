#!/usr/bin/env python3
"""Host static gate: native v0.1.4 PS5 explicitly links FreeType with fallback TextServer."""
from pathlib import Path

root=Path(__file__).resolve().parents[1]
build=(root/"scripts/build-engine.sh").read_text()
ci=(root.parent.parent/".github/workflows/build-godot-ps5-m10c-freetype-fonts.yml").read_text()
baseline=(root.parent.parent/".github/workflows/build-godot-ps5-m9b-native-physics.yml").read_text()

for marker in ("GODOT_PS5_FREETYPE:-0",
    "module_freetype_enabled=yes", "builtin_freetype=yes",
    "module_text_server_fb_enabled=yes", "module_text_server_adv_enabled=no"):
    assert marker in build, marker

for marker in ("GODOT_PS5_FREETYPE: '1'", "GODOT_PS5_PHYSICS2D: '1'",
    "libfreetype_builtin.", "FT_Init_FreeType", "MODULE_FREETYPE_ENABLED",
    "libmodule_text_server_fb.", "libmodule_godot_physics_2d.",
    "GODOT_PS5_M10B_FONT_TTF_LOADED", "GODOT_PS5_M10B_FONT_METRICS_OK",
    "GODOT_PS5_M10B_FONT_TEST_FINISHED",
    "contentVersion='01.000.005'",
    "Godot-PS5-M10c-NATIVE-FREETYPE-v0.1.4-PS5-HARDWARE-UNTESTED"):
    assert marker in ci, marker

assert "GODOT_PS5_FREETYPE:" not in baseline
assert "contentVersion='01.000.004'" in baseline
assert "module_freetype_enabled=yes" not in baseline
assert "assert meta['contentVersion']=='01.000.005'" in ci
assert "GODOT_PS5_FREETYPE" not in (root/"engine/platform/ps5/detect.py").read_text()

assert "GODOT_PS5_M10B_FONT_FAIL_GLYPH_A" in (root/"samples/m10b-font-ui/main.gd").read_text()
print("PASS M10c FreeType-only opt-in, native module/link checks, old PS5 v0.1.3 unchanged")
