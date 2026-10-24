#!/usr/bin/env python3
"""Keep the signed native Godot package version in sync with CI assertions."""
from pathlib import Path
root = Path(__file__).resolve().parents[1]
stage = (root / "scripts/stage_native_link.py").read_text()
wf = (root.parent.parent / ".github/workflows/build-godot-ps5.yml").read_text()
import re
found = re.search(r'contentVersion="([0-9.]+)"', stage)
assert found, "No native staged contentVersion found"
version = found.group(1)
assert f'assert meta["contentVersion"]=="{version}"' in wf, (
    f"CI package version does not match stage_native_link.py ({version})"
)
assert 'Godot-PS5-GDScript-Engine-Smoke-v0.3.2-UNVERIFIED-ON-CONSOLE' in wf
print("PASS: Godot PS5 signed package version + catalog release artifact contract", version)
