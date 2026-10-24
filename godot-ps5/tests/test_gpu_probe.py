#!/usr/bin/env python3
"""Guard the PS5 isolated-GPU experiment against accidental engine mixing."""
from pathlib import Path
root = Path(__file__).resolve().parents[1]
src = (root / "gpu-probe/main.cpp").read_text()
wf = (root.parent.parent / ".github/workflows/build-godot-ps5-gpu-probe.yml").read_text()
readme = (root / "gpu-probe/README.md").read_text()
for symbol in ("egl", "display.open", "glClear(", "display.swap()",
               "FIRST_FRAME_PRESENTED", "PRESENTED_FRAME_COUNT", "CLEAN_SHUTDOWN",
               "kCross", "kCircle", "graphics-probe.log"):
    assert symbol in src, symbol
assert "PPSA99844" in wf and "PPSA99844" in readme
assert "PPSA99843.zip" not in wf
assert "publish" not in wf.lower().split("jobs:",1)[1].split("name:",1)[0]
assert "godot_ps5_run_pack" not in src and "os_ps5" not in src

mirror = (root / "gpu-probe/fetch-mirrored-opengl-sdk.sh").read_text()
assert "30d8e51dd062739b629346102be5932728ba714bc50b1bdcdf08306c8843d9a4" in mirror
assert "KernelForgeLabs/ps5-opengl-sdk-mirror" in mirror
assert "sha256sum --check --strict --quiet" in mirror
assert "manifest.sha256" in mirror
assert "PS5_OPENGL_PREFIX" in wf and "fetch-mirrored-opengl-sdk.sh" in wf
assert "ps5-opengl-sdk-mirror" in readme
assert "Godot-PS5-Isolated-GPU-Probe-v0.1.${{ github.run_number }}-UNVERIFIED-ON-CONSOLE" in wf
assert "j['contentVersion']=f'01.000.{patch+1:03d}'" in wf
assert "github.run_number" in wf
for symbol in ("#version 460 core", "glCreateShader", "glShaderSource", "glCompileShader",
               "GL_COMPILE_STATUS", "glLinkProgram", "GL_LINK_STATUS",
               "glGenVertexArrays", "glGenBuffers", "glBufferData",
               "glVertexAttribPointer", "glDrawArrays(GL_TRIANGLES", "glGetError()",
               "VERTEX_COMPILE_OK", "FRAGMENT_COMPILE_OK", "PROGRAM_LINK_OK",
               "GL_GEOMETRY_READY", "GL_TRIANGLE_SUBMITTED",
               "GEOMETRY_FAILED_BACKGROUND_FALLBACK"):
    assert symbol in src, symbol
assert src.index("geometry.release();") < src.index("display.close();")
for symbol in ("Texture2DProbe", "glTexImage2D", "GL_RGBA8", "GL_UNPACK_ALIGNMENT",
               "glPixelStorei", "GL_TEXTURE_2D", "GL_NEAREST", "GL_CLAMP_TO_EDGE",
               "glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)",
               "glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)",
               "SPRITE_PROGRAM_LINK_OK", "SPRITE_TEXTURE_UPLOAD",
               "SPRITE_2D_READY", "SPRITE_FIRST_DRAW_ERROR",
               "SPRITE_2D_DRAW_SUBMITTED", "sprite.release();"):
    assert symbol in src, symbol
assert src.index("sprite.release();") < src.index("display.close();")
print("PASS: isolated GPU probe source & release separation + GL 4.6 geometry")
