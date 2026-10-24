#!/usr/bin/env python3
"""Verify Godot PS5 native DirAccess guard against host/libc cwd crashes."""
import importlib.util
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("dirpatch",root/"scripts/patch_ps5_dir_access.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
fixture='#include "dir_access_unix.h"\n'
for signature in m.NATIVE_METHODS:
    fixture += signature+'\n\tint x=0;\n\tif (x) { x++; }\n\treturn {};\n}\n'
fixture+='DirAccessUnix::DirAccessUnix() {\n\tchar test[2048];\n\tgetcwd(test,2048);\n\tchange_dir(current_dir);\n}\nDirAccessUnix::RemoveNotificationFunc DirAccessUnix::remove_notification_func = nullptr;\n'
patched=m.patch(fixture)
assert m.patch(patched)==patched
assert patched.count('current_dir = "/app0"')==1
assert 'ps5_dir_exists_native' in patched
assert 'sceKernelMkdir' in patched
assert 'O_DIRECTORY' in patched and 'O_NOFOLLOW' in patched
assert 'return ERR_CANT_CREATE' in patched
assert 'current_dir = p_dir' in patched
assert patched.count('#else')>=5
assert 'GodotPS5 DIRACCESS 0.2.11' in patched
for signature in m.NATIVE_METHODS:
    assert patched.count(signature)==1
    assert 'return {};' in patched
try:
    m.patch(fixture.replace("change_dir(current_dir);","missing();"))
except ValueError:
    pass
else:
    raise AssertionError("Missing upstream constructor anchor accepted")
print("PASS: PS5 Unix DirAccess native ctor/cwd/file/dir/mkdir guards and host fallback")
