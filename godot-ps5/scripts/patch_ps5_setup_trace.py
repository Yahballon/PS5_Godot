#!/usr/bin/env python3
"""Trace Godot Main::setup and OS_Unix::initialize_core on PS5 hardware.

Upstream Godot 4.7.2 is patched in a CI-only checkout. We instrument
known source anchors, fail closed on drift and retain all normal behavior.
"""
from pathlib import Path
import sys

MARKER = "GodotPS5 SETUP 0.2.11"
MACRO = r'''
#if defined(PS5_ENABLED)
#include <cstdio>
#define PS5_SETUP_TRACE(step) do { \
    std::fprintf(stderr, "[GodotPS5 SETUP 0.2.11] %s\n", step); \
    std::fflush(stderr); \
} while (0)
#else
#define PS5_SETUP_TRACE(step) ((void)0)
#endif
'''

MAIN_STEPS = [
    ('\tThread::make_main_thread();',
     'BEFORE_THREAD_MAKE_MAIN', 'AFTER_THREAD_MAKE_MAIN'),
    ('\tset_current_thread_safe_for_nodes(true);',
     'BEFORE_THREAD_NODE_SAFE', 'AFTER_THREAD_NODE_SAFE'),
    ('\tOS::get_singleton()->initialize();',
     'BEFORE_OS_INITIALIZE', 'AFTER_OS_INITIALIZE'),
    ('\tString old_cwd = OS::get_singleton()->get_cwd();',
     'BEFORE_GET_CWD', 'AFTER_GET_CWD'),
    ('\tString new_cwd = OS::get_singleton()->get_executable_path().get_base_dir();',
     'BEFORE_GET_EXECUTABLE_PATH', 'AFTER_GET_EXECUTABLE_PATH'),
    ('\tOS::get_singleton()->benchmark_begin_measure("Startup", "Main::Setup");',
     'BEFORE_BENCHMARK_BEGIN', 'AFTER_BENCHMARK_BEGIN'),
    ('\tengine = memnew(Engine);',
     'BEFORE_ENGINE_CREATE', 'AFTER_ENGINE_CREATE'),
    ('\tregister_core_types();',
     'BEFORE_REGISTER_CORE_TYPES', 'AFTER_REGISTER_CORE_TYPES'),
    ('\tregister_core_driver_types();',
     'BEFORE_REGISTER_CORE_DRIVERS', 'AFTER_REGISTER_CORE_DRIVERS'),
    ('\tinput_map = memnew(InputMap);',
     'BEFORE_INPUT_MAP', 'AFTER_INPUT_MAP'),
    ('\tglobals = memnew(ProjectSettings);',
     'BEFORE_PROJECT_SETTINGS', 'AFTER_PROJECT_SETTINGS'),
    ('\tregister_core_settings(); //here globals are present',
     'BEFORE_CORE_SETTINGS', 'AFTER_CORE_SETTINGS'),
]

UNIX_STEPS = [
    ('\tinit_thread_posix();', 'BEFORE_POSIX_THREAD_INIT', 'AFTER_POSIX_THREAD_INIT'),
    ('\tFileAccess::make_default<FileAccessUnix>(FileAccess::ACCESS_RESOURCES);',
     'BEFORE_FILE_ACCESS', 'AFTER_FILE_ACCESS'),
    ('\tDirAccess::make_default<DirAccessUnix>(DirAccess::ACCESS_FILESYSTEM);',
     'BEFORE_DIR_ACCESS', 'AFTER_DIR_ACCESS'),
    ('\tNetSocketUnix::make_default();', 'BEFORE_SOCKET_DEFAULT', 'AFTER_SOCKET_DEFAULT'),
    ('\tIPUnix::make_default();', 'BEFORE_IP_DEFAULT', 'AFTER_IP_DEFAULT'),
    ('\tprocess_map = memnew((HashMap<ProcessID, ProcessInfo>));',
     'BEFORE_PROCESS_MAP', 'AFTER_PROCESS_MAP'),
    ('\t_setup_clock();', 'BEFORE_SETUP_CLOCK', 'AFTER_SETUP_CLOCK'),
]

def patch_segment(segment: str, steps: list[tuple[str, str, str]]) -> str:
    for original, before, after in steps:
        if segment.count(original) != 1:
            raise ValueError(f"Upstream Godot anchor changed: {original!r} ({segment.count(original)})")
        segment = segment.replace(
            original, '\tPS5_SETUP_TRACE("' + before + '");\n' +
            original + '\n\tPS5_SETUP_TRACE("' + after + '");', 1)
    return segment

def patch_main(s: str) -> str:
    if MARKER in s:
        if s.count("BEFORE_OS_INITIALIZE") != 1:
            raise ValueError("Partially patched Main::setup")
        return s
    entry = 'Error Main::setup(const char *execpath, int argc, char *argv[], bool p_second_phase) {'
    next_entry = 'Error Main::setup2(bool p_show_boot_logo) {'
    begin = s.index(entry)
    end = s.index(next_entry, begin)
    segment = s[begin:end]
    segment = patch_segment(segment, MAIN_STEPS)
    segment = segment.replace(entry, entry + '\n\tPS5_SETUP_TRACE("ENTER_MAIN_SETUP");', 1)
    if s.count('#include "main.h"') != 1:
        raise ValueError("Upstream Main include changed")
    s = s[:begin] + segment + s[end:]
    return s.replace('#include "main.h"', '#include "main.h"\n' + MACRO, 1)

def patch_unix(s: str) -> str:
    if MARKER in s:
        if s.count("BEFORE_POSIX_THREAD_INIT") != 1:
            raise ValueError("Partially patched OS_Unix::initialize_core")
        return s
    entry = 'void OS_Unix::initialize_core() {'
    end_entry = 'void OS_Unix::finalize_core() {'
    begin = s.index(entry)
    end = s.index(end_entry, begin)
    segment = s[begin:end]
    segment = patch_segment(segment, UNIX_STEPS)
    segment = segment.replace(entry, entry + '\n\tPS5_SETUP_TRACE("ENTER_OS_UNIX_INITIALIZE_CORE");', 1)
    # Avoid a second helper/macro: this is a distinct compilation unit.
    if s.count('#include "os_unix.h"') != 1:
        raise ValueError("Upstream OS_Unix include changed")
    s = s[:begin] + segment + s[end:]
    return s.replace('#include "os_unix.h"', '#include "os_unix.h"\n' + MACRO, 1)

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: patch_ps5_setup_trace.py /path/to/godot")
    root = Path(sys.argv[1])
    for path, patcher in (
        (root / "main/main.cpp", patch_main),
        (root / "drivers/unix/os_unix.cpp", patch_unix),
    ):
        before = path.read_text()
        after = patcher(before)
        if after != before:
            path.write_text(after)
        print("PS5 setup instrumentation:", path.relative_to(root))

if __name__ == "__main__":
    main()
