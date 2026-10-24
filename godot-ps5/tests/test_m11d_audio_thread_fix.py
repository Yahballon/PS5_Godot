#!/usr/bin/env python3
"""M11d hardware-derived regression: Godot Thread::start returns Thread::ID."""
from pathlib import Path
base=Path(__file__).resolve().parents[1]
driver=(base/"engine/platform/ps5/audio_driver_ps5.cpp").read_text()
workflow=(base.parent.parent/".github/workflows/build-godot-ps5-m11d-audio-thread.yml").read_text()
assert "thread.start(&AudioDriverPS5::thread_main, this);" in driver
assert "if (!thread.is_started())" in driver
assert "thread.start(&AudioDriverPS5::thread_main, this) != OK" not in driver
assert "thread.start(&AudioDriverPS5::thread_main, this) == OK" not in driver
assert 'GODOT_PS5_M11D_AUDIOOUT_THREAD_STARTED' in driver
assert 'GODOT_PS5_M11D_AUDIOOUT_OUTPUT_OK' in driver
assert 'GODOT_PS5_M11D_AUDIOOUT_OUTPUT_ERROR' in driver
assert '%llu' not in driver, "Godot vformat does not support %llu; hides native return codes"
assert "driver->unlock();" in driver and driver.index("driver->unlock();") < driver.index("sceAudioOutOutput(driver->handle,")
assert "thread.wait_to_finish();" in driver
assert "sceAudioOutClose(handle);" in driver
assert "contentVersion='01.000.007'" in workflow
assert "assert meta['contentVersion']=='01.000.007'" in workflow
assert 'GODOT_PS5_AUDIOOUT: \'1\'' in workflow
assert 'Godot-PS5-M11d-NATIVE-AUDIOOUT-v0.1.6-PS5-HARDWARE-UNTESTED' in workflow
print("GODOT_PS5_M11D_THREAD_ID_AUDIOOUT_REGRESSION_PASS")
