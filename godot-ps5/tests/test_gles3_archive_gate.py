#!/usr/bin/env python3
"""Guard the isolated GLES3 *cross-compile*, not proof of PS5 rendering."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]
platform=p/"engine/platform/ps5"
detect=(platform/"detect.py").read_text()
build=(p/"scripts/build-engine.sh").read_text()
scsub=(platform/"SCsub").read_text()
gl=(platform/"platform_gl.h").read_text()
egl=(platform/"platform_egl.h").read_text()
workflow=(p.parent.parent/".github/workflows/validate-godot-ps5-gles3-archives.yml").read_text()
assert 'GODOT_PS5_GLES3_ARCHIVES' in detect and 'GLES3_ENABLED' in detect
assert 'GLAD_ENABLED' in detect and 'EGL_ENABLED' in detect
assert '"EGL_STATIC"' not in detect, "GLAD dynamic EGL and static declarations clash"
assert 'opengl3="$gl_backend"' in build and 'gl_backend=no' in build
assert '"#thirdparty/glad/gl.c"' in scsub and '"#thirdparty/glad/egl.c"' in scsub
assert '<thirdparty/glad/glad/gl.h>' in gl
assert '<thirdparty/glad/glad/egl.h>' in egl
assert 'GODOT_PS5_GLES3_ARCHIVES: "1"' in workflow
assert "libdrivers.ps5.template_debug.x86_64.a" in workflow
assert "rasterizer_gles3" in workflow and "godot_ps5_glad" in workflow
assert "upload-artifact" in workflow and "gh release create" not in workflow
print("PASS: opt-in real Godot GLES3 compilation isolated from stable PS5 titles")
