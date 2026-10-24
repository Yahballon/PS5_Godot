#!/usr/bin/env python3
"""Fail-closed 0.2.9 Godot upstream tracing smoke tests."""
import importlib.util
from pathlib import Path

src=Path(__file__).resolve().parents[1]/'scripts/patch_ps5_post_settings_trace.py'
spec=importlib.util.spec_from_file_location('ps5_post_trace',src)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

project='''#include "project_settings.h"
Error ProjectSettings::_setup(const String &p_path, const String &p_main_pack, bool p_upwards, bool p_ignore_override) {
\tif (!p_main_pack.is_empty()) {
\t\tbool ok = _load_resource_pack(p_main_pack, false, 0, true);
\t\tError err = _load_settings_text_or_binary("res://project.godot", "res://project.binary");
\t\t\t\t_load_settings_text(p_main_pack.get_base_dir().path_join("override.cfg"));
\t\treturn err;
\t}
\tString exec_path = OS::get_singleton()->get_executable_path();
\tError err = _load_settings_text_or_binary("res://project.godot", "res://project.binary");
\treturn err;
}
Error ProjectSettings::setup(const String &p_path, const String &p_main_pack, bool p_upwards, bool p_ignore_override) {
\tError err = _setup(p_path, p_main_pack, p_upwards, p_ignore_override);
\tload_scene_groups_cache();
\tproject_loaded = err == OK;
\treturn err;
}
bool ProjectSettings::has_setting(const String &p_var) const {}
'''
patched=m.patch_project(project)
assert m.patch_project(patched)==patched
assert patched.count('BEFORE_PROJECT_CONFIG_READ')==1
assert patched.count('AFTER_PACK_OVERRIDE')==1
assert patched.count('AFTER_SCENE_GROUPS_CACHE')==1
assert patched.count('RETURN_MAIN_PACK_SETUP')==1
assert patched.count('Error err = _load_settings_text_or_binary("res://project.godot", "res://project.binary");')==2
try:
    m.patch_project(project.replace('override.cfg','wrong.cfg'))
except ValueError:
    pass
else:
    raise AssertionError('Missing upstream main pack override did not fail closed')

main='''#include "main.h"
Error Main::setup(const char *execpath, int argc, char *argv[], bool p_second_phase) {
\tif (globals->setup(project_path, main_pack, false, editor) == OK) {
\t}
\t// Initialize WorkerThreadPool.
\t\t\tWorkerThreadPool::get_singleton()->init(worker_threads, low_priority_ratio);
\t\tWorkerThreadPool::get_singleton()->init(0, 0);
\t}

#ifdef TOOLS_ENABLED
\tif (!project_manager && !editor) {
\tOS::get_singleton()->set_cmdline(execpath, main_args, user_args);
\tOS::get_singleton()->ensure_user_data_dir();
\tregister_early_core_singletons();
\tinitialize_modules(MODULE_INITIALIZATION_LEVEL_CORE);
\tResourceUID::get_singleton()->load_from_cache(true); // Load UUIDs from cache.
\t\tinput_map->load_from_project_settings(); //keys for game
}
Error Main::setup2(bool p_show_boot_logo) {}
'''
patched=m.patch_main(main)
assert patched==m.patch_main(patched)
for step in ('BEFORE_PROJECT_SETUP','AFTER_PROJECT_SETUP_OK','BEFORE_WORKER_POOL_INIT',
             'AFTER_WORKER_POOL_INIT','AFTER_WORKER_POOL_BLOCK','BEFORE_EARLY_SINGLETONS'):
    assert patched.count(step)==1, step
print('PASS: post-PCK Godot tracer stays scoped, idempotent and fail-closed')
