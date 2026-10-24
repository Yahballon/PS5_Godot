#!/usr/bin/env python3
"""PS5 sandbox cwd regression: avoid upstream FreeBSD getcwd crash."""
from pathlib import Path

root=Path(__file__).resolve().parents[1]/"engine/platform/ps5"
header=(root/"os_ps5.h").read_text()
code=(root/"os_ps5.cpp").read_text()

for name in ("get_cwd()", "get_executable_path()"):
    assert f"String {name} const override;" in header, name
    assert f"String OS_PS5::{name} const" in code, name
assert 'Error set_cwd(const String &path) override;' in header
assert 'String OS_PS5::get_cwd() const { return "/app0"; }' in code
assert 'String OS_PS5::get_executable_path() const { return "/app0/eboot.bin"; }' in code
assert 'return path == "/app0" ? OK : ERR_UNAVAILABLE;' in code
print("PASS: PS5 sandbox cwd/executable path overrides during Godot Main::setup")
