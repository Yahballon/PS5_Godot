#!/usr/bin/env python3
"""Checks native PS5 userdata mkdir path and fail-closed source patch."""
from pathlib import Path
import importlib.util

root=Path(__file__).resolve().parents[1]
src=root/"scripts/patch_ps5_userdata.py"
spec=importlib.util.spec_from_file_location("ps5_userdata",src)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
fixture='#include "os.h"\n'+m.ORIGINAL+'\nvoid OS::test_sentinel() {}\n'
fixed=m.patch(fixture)
assert m.patch(fixed)==fixed, "source patch must be idempotent"
assert fixed.count("void OS::ensure_user_data_dir() {")==1
assert '#if defined(PS5_ENABLED)' in fixed
assert "#else\n\tString dd = get_user_data_dir();" in fixed
assert 'sceKernelMkdir(current, 0755)' in fixed
assert 'sceKernelOpen(current, O_RDONLY | O_DIRECTORY, 0)' in fixed
assert 'std::fflush(stderr);' in fixed
assert 'DIR_FAILED' in fixed and 'DIR_OK' in fixed and 'UNSAFE_PATH' in fixed
assert 'get_user_data_dir()' in fixed
assert 'Ref<DirAccess> da' in fixed, "non-PS5 implementation preserved"
assert 'get_user_data_dir()' in fixed
assert '0.2.11' in fixed
try:
    m.patch(fixture.replace("make_dir_recursive(dd)", "make_dir(dd)"))
except ValueError:
    pass
else:
    raise AssertionError("Unexpected upstream Godot source accepted")
print("PASS: Godot PS5 kernel mkdir / open data-root guard / other-platform fallback")
