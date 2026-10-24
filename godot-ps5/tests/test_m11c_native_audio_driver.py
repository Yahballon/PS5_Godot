#!/usr/bin/env python3
"""Static guardrails for *actual* PS5 AudioOut mixer integration.

This cannot prove audio audibility; require physical PS5 listening report.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
platform=root/"engine/platform/ps5"
driver=(platform/"audio_driver_ps5.cpp").read_text()
header=(platform/"audio_driver_ps5.h").read_text()
os_cpp=(platform/"os_ps5.cpp").read_text()
os_h=(platform/"os_ps5.h").read_text()
scons=(platform/"SCsub").read_text()
detect=(platform/"detect.py").read_text()
for entry in ["sceAudioOutInit()", "sceAudioOutOpen(", "sceAudioOutOutput(",
              "sceAudioOutClose(", "audio_server_process(BLOCK_FRAMES",
              "GODOT_PS5_M11C_AUDIOOUT_OPEN",
              "GODOT_PS5_M11C_AUDIOOUT_FATAL_STOP"]:
    assert entry in driver, entry
assert ("GODOT_PS5_M11C_AUDIOOUT_OUTPUT_OK" in driver or
        "GODOT_PS5_M11D_AUDIOOUT_OUTPUT_OK" in driver), "native PS5 AudioOut successful block marker missing"
for guard in ["Thread thread", "Mutex mutex", "BLOCK_FRAMES = 256",
              "MIX_RATE = 48000", "SPEAKER_MODE_STEREO", "SafeFlag exiting"]:
    assert guard in header, guard
assert "GODOT_PS5_M11C_AUDIOOUT_DRIVER_REGISTERED" in os_cpp
assert "AudioDriverManager::add_driver(&audio_driver)" in os_cpp
assert "#ifdef GODOT_PS5_AUDIOOUT" in os_h
assert 'os.environ.get("GODOT_PS5_AUDIOOUT") == "1"' in scons
assert 'CPPDEFINES=["GODOT_PS5_AUDIOOUT"]' in detect
assert "const int32_t sample = driver->godot_samples[i] >> 16;" in driver
assert "driver->unlock();" in driver
assert driver.index("driver->unlock();") < driver.index("sceAudioOutOutput(driver->handle,")
assert "GODOT_PS5_M11C_AUDIOOUT" not in (root/"scripts/build-engine.sh").read_text()

workflow=(root.parent.parent/".github/workflows/build-godot-ps5-m11c-native-audioout.yml").read_text()
assert "contentVersion='01.000.006'" in workflow, "stage must set v0.1.5"
assert "assert meta['contentVersion']=='01.000.006'" in workflow, "ZIP check must expect v0.1.5"
assert "GODOT_PS5_AUDIOOUT: '1'" in workflow
assert "libSceAudioOut.so" in workflow
assert "Godot-PS5-M11c-NATIVE-AUDIOOUT-v0.1.5-PS5-HARDWARE-UNTESTED" in workflow
print("GODOT_PS5_M11C_DRIVER_SOURCE_OK true AudioDriver, mixer, blocking AudioOut, safe opt-in")
