#!/usr/bin/env python3
"""Source/API and ZIP regression checks; host CI must also execute real Godot."""
from pathlib import Path
import hashlib
import importlib.util
import struct
import tempfile
import zipfile

root = Path(__file__).resolve().parents[1]
audio = (root / "samples/m11-audio/main.gd").read_text()
save = (root / "samples/m11-saves/main.gd").read_text()
for token in ("AudioStreamPlayer.new()", "AudioStreamWAV.new()", "FORMAT_16_BITS",
              "player.play()", "GODOT_PS5_M11_AUDIO_PCM_READY",
              "GODOT_PS5_M11_AUDIO_PLAYER_STARTED", "AUDIO_HARDWARE_AUDIBILITY_UNCONFIRMED"):
    assert token in audio, token
for token in ('FileAccess.open(FILE, FileAccess.WRITE)', 'FileAccess.open(FILE, FileAccess.READ)',
              'FileAccess.file_exists(FILE)', 'writer.flush()', 'GODOT_PS5_M11_SAVE_PERSIST_OK',
              'GODOT_PS5_M11_SAVE_WRITE_OK', 'GODOT_PS5_M11_SAVE_RESTART_PERSISTENCE_PASS',
              'GODOT_PS5_M11_SAVE_WRITE_UNAVAILABLE'):
    assert token in save, token
assert 'user://m11-save-v1.txt' in save
for part in ("m11-audio", "m11-saves"):
    p = root / "samples" / part / "make_pack.gd"
    text = p.read_text()
    for name in ("project.godot", "main.gd", "main.tscn"):
        assert name in text
spec = importlib.util.spec_from_file_location("pack_m11",root/"scripts/package_m11_external_pcks.py")
assert spec and spec.loader
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
with tempfile.TemporaryDirectory() as folder:
    folder = Path(folder)
    for mode,(pck_name,zip_name) in tool.TESTS.items():
        pck = folder / pck_name
        raw = b"GDPC" + struct.pack("<III",3,4,7) + bytes(96)
        pck.write_bytes(raw)
        target,digest = tool.bundle(mode,pck,folder/mode)
        assert target.name == zip_name
        assert digest == hashlib.sha256(raw).hexdigest()
        with zipfile.ZipFile(target) as archive:
            assert archive.testzip() is None
            assert archive.read("GodotPS5/launch.txt") == (pck_name+"\n").encode()
            assert archive.read("GodotPS5/games/"+pck_name) == raw
        pck.write_bytes(b"FAKE"+bytes(96))
        try: tool.bundle(mode,pck,folder/mode)
        except ValueError: pass
        else: raise AssertionError("bad PCK accepted")
print("GODOT_PS5_M11_STATIC_PACKAGING_OK")
