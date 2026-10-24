#!/usr/bin/env python3
"""Prevent native PS5 PCK I/O from falling back to libc stdio."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
h=(root/"engine/platform/ps5/file_access_ps5.h").read_text()
cc=(root/"engine/platform/ps5/file_access_ps5.cpp").read_text()
os=(root/"engine/platform/ps5/os_ps5.cpp").read_text()
sc=(root/"engine/platform/ps5/SCsub").read_text()
assert "file_access_ps5.cpp" in sc
for method in ("open_internal", "get_buffer", "seek", "seek_end", "get_length", "file_exists", "get_position", "close"):
    assert method in h and "FileAccessPS5::"+method in cc
for kernel_fn in ("sceKernelOpen", "sceKernelRead", "sceKernelLseek", "sceKernelClose"):
    assert kernel_fn in cc, kernel_fn
assert "FileAccess::make_default<FileAccessPS5>(FileAccess::ACCESS_RESOURCES)" in os
assert "FileAccess::make_default<FileAccessPS5>(FileAccess::ACCESS_FILESYSTEM)" in os
assert "FileAccessUnix::open_internal" in cc, "Non-native file accesses must fall back"
assert 'p_mode_flags == READ && native_mount(native_path)' in cc
assert '"[GodotPS5 IO] OPEN_OK %s' in cc
assert '"[GodotPS5 IO] OPEN_FAILED %s' in cc
print("PASS: Godot native PS5 PCK read/seek + resource provider registration")
