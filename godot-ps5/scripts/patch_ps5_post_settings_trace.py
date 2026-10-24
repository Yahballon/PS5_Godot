#!/usr/bin/env python3
"""Trace PS5 post-PCK startup without masking runtime faults.

Patch pinned Godot 4.7.2 source after patch_ps5_setup_trace.py. Unlike
the OS setup trace this covers ProjectSettings::setup, the optional
override file, and worker-pool startup, which are the next calls after
the last observed v0.2.8 diagnostic.
"""
from pathlib import Path
import sys

MARKER = "GodotPS5 NEXT 0.2.11"
HEADER = r'''
#if defined(PS5_ENABLED)
#include <cstdio>
#define PS5_NEXT_TRACE(stage) do { \
    std::fprintf(stderr, "[GodotPS5 NEXT 0.2.11] %s\n", stage); \
    std::fflush(stderr); \
} while (0)
#else
#define PS5_NEXT_TRACE(stage) ((void)0)
#endif
'''

def once(s: str, old: str, new: str) -> str:
    count = s.count(old)
    if count != 1:
        raise ValueError(f"Unexpected Godot 4.7.2 anchor count {count}: {old!r}")
    return s.replace(old, new, 1)

def patch_main(s: str) -> str:
    if MARKER in s:
        if "BEFORE_WORKER_POOL_INIT" not in s:
            raise ValueError("Partial main.cpp instrumentation")
        return s
    entry = 'Error Main::setup(const char *execpath, int argc, char *argv[], bool p_second_phase) {'
    end = 'Error Main::setup2(bool p_show_boot_logo) {'
    start = s.index(entry)
    stop = s.index(end, start)
    part = s[start:stop]
    original = '\tif (globals->setup(project_path, main_pack, false, editor) == OK) {'
    part = once(part, original,
        '\tPS5_NEXT_TRACE("BEFORE_PROJECT_SETUP");\n' +
        original + '\n\t\tPS5_NEXT_TRACE("AFTER_PROJECT_SETUP_OK");')
    part = once(part, '\t// Initialize WorkerThreadPool.',
        '\tPS5_NEXT_TRACE("BEFORE_WORKER_POOL_BLOCK");\n\t// Initialize WorkerThreadPool.')
    original = '\t\t\tWorkerThreadPool::get_singleton()->init(worker_threads, low_priority_ratio);'
    part = once(part, original,
        '\t\t\tPS5_NEXT_TRACE("BEFORE_WORKER_POOL_INIT");\n' + original +
        '\n\t\t\tPS5_NEXT_TRACE("AFTER_WORKER_POOL_INIT");')
    original = '\t\tWorkerThreadPool::get_singleton()->init(0, 0);'
    part = once(part, original,
        '\t\tPS5_NEXT_TRACE("BEFORE_NO_THREADS_POOL_INIT");\n' + original +
        '\n\t\tPS5_NEXT_TRACE("AFTER_NO_THREADS_POOL_INIT");')
    original = '\t}\n\n#ifdef TOOLS_ENABLED\n\tif (!project_manager && !editor) {'
    part = once(part, original,
        '\t}\n\tPS5_NEXT_TRACE("AFTER_WORKER_POOL_BLOCK");\n\n#ifdef TOOLS_ENABLED\n\tif (!project_manager && !editor) {')
    for original, tag in [
        ('\tOS::get_singleton()->set_cmdline(execpath, main_args, user_args);', 'SET_CMDLINE'),
        ('\tOS::get_singleton()->ensure_user_data_dir();', 'ENSURE_USER_DATA'),
        ('\tregister_early_core_singletons();', 'EARLY_SINGLETONS'),
        ('\tinitialize_modules(MODULE_INITIALIZATION_LEVEL_CORE);', 'INITIALIZE_MODULES'),
        ('\tResourceUID::get_singleton()->load_from_cache(true); // Load UUIDs from cache.', 'LOAD_UID_CACHE'),
        ('\t\tinput_map->load_from_project_settings(); //keys for game', 'INPUT_MAP_FROM_PROJECT'),
    ]:
        indent = original[:len(original)-len(original.lstrip('\t'))]
        part = once(part, original,
            indent + 'PS5_NEXT_TRACE("BEFORE_' + tag + '");\n' +
            original + '\n' + indent + 'PS5_NEXT_TRACE("AFTER_' + tag + '");')
    return once(s[:start] + part + s[stop:], '#include "main.h"', '#include "main.h"\n' + HEADER)

def patch_project(s: str) -> str:
    if MARKER in s:
        if 'AFTER_PACK_OVERRIDE' not in s:
            raise ValueError("Partial project_settings.cpp instrumentation")
        return s
    original = '#include "project_settings.h"'
    s = once(s, original, original + '\n' + HEADER)
    entry = 'Error ProjectSettings::_setup('
    end = 'Error ProjectSettings::setup('
    start = s.index(entry)
    stop = s.index(end, start)
    entire_setup = s[start:stop]
    # Only the --main-pack branch: other Godot fallback paths contain
    # identical project.godot load calls and must remain untouched.
    cut = entire_setup.index('\tString exec_path = OS::get_singleton()->get_executable_path();')
    part, other_paths = entire_setup[:cut], entire_setup[cut:]
    part = once(part, '\tif (!p_main_pack.is_empty()) {',
        '\tif (!p_main_pack.is_empty()) {\n\t\tPS5_NEXT_TRACE("ENTER_MAIN_PACK_SETTINGS");')
    target = '\t\tbool ok = _load_resource_pack(p_main_pack, false, 0, true);'
    part = once(part,target,
        '\t\tPS5_NEXT_TRACE("BEFORE_PACK_REGISTER");\n' +target+
        '\n\t\tPS5_NEXT_TRACE("AFTER_PACK_REGISTER");')
    target = '\t\tError err = _load_settings_text_or_binary("res://project.godot", "res://project.binary");'
    part = once(part,target,
        '\t\tPS5_NEXT_TRACE("BEFORE_PROJECT_CONFIG_READ");\n' +target+
        '\n\t\tPS5_NEXT_TRACE("AFTER_PROJECT_CONFIG_READ");')
    target = '\t\t\t\t_load_settings_text(p_main_pack.get_base_dir().path_join("override.cfg"));'
    part = once(part,target,
        '\t\t\t\tPS5_NEXT_TRACE("BEFORE_PACK_OVERRIDE");\n' +target+
        '\n\t\t\t\tPS5_NEXT_TRACE("AFTER_PACK_OVERRIDE");')
    target='\t\treturn err;'
    part=once(part,target,'\t\tPS5_NEXT_TRACE("RETURN_MAIN_PACK_SETUP");\n'+target)
    s=s[:start]+part+other_paths+s[stop:]
    start=s.index(end)
    stop=s.index('bool ProjectSettings::has_setting(',start)
    section=s[start:stop]
    anchor='\tError err = _setup(p_path, p_main_pack, p_upwards, p_ignore_override);'
    section=once(section, anchor,
        '\tPS5_NEXT_TRACE("ENTER_PROJECT_SETTINGS_SETUP");\n' + anchor +
        '\n\tPS5_NEXT_TRACE("AFTER_PROJECT_SETTINGS__SETUP");')
    anchor='\tload_scene_groups_cache();'
    section=once(section, anchor,
        '\tPS5_NEXT_TRACE("BEFORE_SCENE_GROUPS_CACHE");\n'+anchor+
        '\n\tPS5_NEXT_TRACE("AFTER_SCENE_GROUPS_CACHE");')
    section=once(section, '\tproject_loaded = err == OK;\n\treturn err;',
        '\tproject_loaded = err == OK;\n\tPS5_NEXT_TRACE("PROJECT_SETTINGS_SETUP_RETURN");\n\treturn err;')
    return s[:start]+section+s[stop:]

def main() -> None:
    if len(sys.argv)!=2:
        raise SystemExit('usage: patch_ps5_post_settings_trace.py /path/to/godot')
    root=Path(sys.argv[1])
    for path,fn in (
        (root/'main/main.cpp',patch_main),
        (root/'core/config/project_settings.cpp',patch_project),
    ):
        original=path.read_text()
        changed=fn(original)
        if changed!=original: path.write_text(changed)
        print("Godot PS5 0.2.11 tracing:",path.relative_to(root))

if __name__ == '__main__':
    main()
