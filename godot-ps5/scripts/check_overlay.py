#!/usr/bin/env python3
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
root=Path(__file__).resolve().parent.parent
platform=root/"engine/platform/ps5"
for file in ("detect.py","SCsub","platform_config.h","os_ps5.cpp","os_ps5.h","godot_ps5.cpp","pck_locator.hpp","logo.svg","compat.cpp","compat.h"):
    assert (platform/file).is_file(),file
ET.parse(platform/"logo.svg")
assert "Main::setup" in (platform/"godot_ps5.cpp").read_text()
assert "--main-pack" in (platform/"godot_ps5.cpp").read_text()
assert (root/"samples/script-smoke/project.godot").exists()
print("PASS platform overlay, Godot startup and sample fixture present")
