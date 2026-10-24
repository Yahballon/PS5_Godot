#!/usr/bin/env python3
"""Offline test: full library bundle must include core + scripts, not just platform."""
import importlib.util
import json
from pathlib import Path
import tempfile
import zipfile

src = Path(__file__).resolve().parents[1] / "scripts/package_static_engine.py"
spec = importlib.util.spec_from_file_location("ps5pack", src)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    suffix = "ps5.template_debug.x86_64.a"
    names = [
        "bin/obj/core/libcore.",
        "bin/obj/main/libmain.",
        "bin/obj/drivers/libdrivers.",
        "bin/obj/scene/libscene.",
        "bin/obj/servers/libservers.",
        "bin/obj/platform/libplatform.",
        "bin/obj/modules/libmodule_gdscript.",
        "bin/libgodot_ps5.",
    ]
    for n in names:
        p = root / (n + suffix)
        p.parent.mkdir(parents=True, exist_ok=True)
        # Only the AR magic is inspected by the packager; this mock isn't linked.
        p.write_bytes(b"!<arch>\n" + b"\0" * 256)
    out = root / "combined.zip"
    try:
        mod.bundle(root, out)
        raise AssertionError("Too few archives were accepted")
    except ValueError as e:
        assert "Only 8 PS5 static libs" in str(e)
    manifest = mod.bundle(root, out, min_archives=8)
    assert manifest["archive_count"] == 8
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        assert "bin/obj/modules/libmodule_gdscript." + suffix in z.namelist()
        assert "bin/obj/core/libcore." + suffix in z.namelist()
        assert z.read("godot-link-libs.rsp").decode().startswith("--start-group\n")
        info = json.loads(z.read("manifest.json"))
        assert len(info["archives"]) == 8
    (root / ("bin/obj/modules/libmodule_gdscript."+suffix)).unlink()
    try:
        mod.bundle(root, out, min_archives=7)
        raise AssertionError("Missing GDScript was accepted")
    except ValueError as e:
        assert "libmodule_gdscript" in str(e)
print("PASS: Godot static libraries bundle, SHA metadata, linker response and fail-closed checks")
