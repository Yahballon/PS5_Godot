#!/usr/bin/env python3
"""Fail-closed smoke tests for Godot PS5 real setup instrumentation."""
import importlib.util
from pathlib import Path
root=Path(__file__).resolve().parents[1]
target=root/"scripts/patch_ps5_setup_trace.py"
spec=importlib.util.spec_from_file_location("ps5_trace",target)
trace=importlib.util.module_from_spec(spec)
spec.loader.exec_module(trace)

entry='Error Main::setup(const char *execpath, int argc, char *argv[], bool p_second_phase) {'
next_entry='Error Main::setup2(bool p_show_boot_logo) {'
fixture='#include "main.h"\n' + entry + '\n' + '\n'.join(
    marker for marker,_,_ in trace.MAIN_STEPS
) + '\n}\n' + next_entry + '\n}\n'
modified=trace.patch_main(fixture)
assert modified==trace.patch_main(modified)
assert modified.count("ENTER_MAIN_SETUP")==1
for call,before,after in trace.MAIN_STEPS:
    assert modified.count(before)==1 and modified.count(after)==1
    assert modified.index(before)<modified.index(call)<modified.index(after)
try:
    trace.patch_main(fixture.replace('Thread::make_main_thread();','not_here();'))
except ValueError:
    pass
else:
    raise AssertionError("Unexpected Main anchor accepted")

unix='#include "os_unix.h"\nvoid OS_Unix::initialize_core() {\n' + '\n'.join(
    marker for marker,_,_ in trace.UNIX_STEPS
) + '\n}\nvoid OS_Unix::finalize_core() {}\n'
edited=trace.patch_unix(unix)
assert edited==trace.patch_unix(edited)
assert 'BEFORE_POSIX_THREAD_INIT' in edited
assert 'AFTER_SETUP_CLOCK' in edited
assert '#if defined(PS5_ENABLED)' in edited
print("PASS: Godot Main::setup and OS_Unix trace markers / idempotence / fail-closed")
