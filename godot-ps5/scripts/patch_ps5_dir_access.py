#!/usr/bin/env python3
"""Guard dangerous upstream Unix DirAccess calls in a PS5-only overlay.

The project now has libkernel FileAccessPS5 and kernel-backed userdata mkdir,
but DirAccessUnix still constructs itself via getcwd()+chdir() and probes
folders with stat()/access(). On PS5, dispatch sandbox path checks and
directory operations through exported sceKernel functions instead. The
other platforms retain their original implementation unchanged.
"""
from pathlib import Path
import sys

MARKER = "GodotPS5 DIRACCESS 0.2.11"
INCLUDE_ANCHOR = '#include "dir_access_unix.h"'
INCLUDES = r'''
#if defined(PS5_ENABLED)
#include <fcntl.h>
#include <cstdio>
extern "C" int sceKernelOpen(const char*, int, int);
extern "C" int sceKernelClose(int);
extern "C" int sceKernelMkdir(const char*, int);

// Never use the untrusted global libc current directory on PS5.
// Only expose the app sandbox, dedicated data root and known USB mounts.
static bool ps5_dir_mount(const String &path) {
    return path == "/app0" || path.begins_with("/app0/") ||
           path == "/data/GodotPS5" || path.begins_with("/data/GodotPS5/") ||
           path == "/mnt/usb0" || path.begins_with("/mnt/usb0/") ||
           path == "/mnt/usb1" || path.begins_with("/mnt/usb1/") ||
           path == "/mnt/usb2" || path.begins_with("/mnt/usb2/") ||
           path == "/mnt/usb3" || path.begins_with("/mnt/usb3/");
}
static int ps5_dir_open(const String &path, bool require_directory) {
    if (!ps5_dir_mount(path) || path.contains("..") || path.contains("//")) return -1;
    const CharString c = path.utf8();
    return sceKernelOpen(c.get_data(),
            O_RDONLY | O_NOFOLLOW | (require_directory ? O_DIRECTORY : 0), 0);
}
static bool ps5_dir_exists_native(const String &path) {
    const int fd = ps5_dir_open(path, true);
    if (fd < 0) return false;
    sceKernelClose(fd);
    return true;
}
#endif
'''

NATIVE_METHODS = {
    "bool DirAccessUnix::file_exists(String p_file) {": r'''
    if (p_file.is_relative_path()) p_file = current_dir.path_join(p_file);
    p_file = fix_path(p_file);
    if (ps5_dir_exists_native(p_file)) return false;
    const int fd = ps5_dir_open(p_file, false);
    if (fd < 0) return false;
    sceKernelClose(fd);
    return true;
''',
    "bool DirAccessUnix::dir_exists(String p_dir) {": r'''
    if (p_dir.is_relative_path()) p_dir = current_dir.path_join(p_dir);
    return ps5_dir_exists_native(fix_path(p_dir));
''',
    "Error DirAccessUnix::make_dir(String p_dir) {": r'''
    if (p_dir.is_relative_path()) p_dir = current_dir.path_join(p_dir);
    p_dir = fix_path(p_dir);
    if (!p_dir.begins_with("/data/GodotPS5/")) return ERR_CANT_CREATE;
    if (ps5_dir_exists_native(p_dir)) return ERR_ALREADY_EXISTS;
    const CharString c = p_dir.utf8();
    const int rc = sceKernelMkdir(c.get_data(), 0755);
    if (rc < 0) return ps5_dir_exists_native(p_dir) ? ERR_ALREADY_EXISTS : ERR_CANT_CREATE;
    std::fprintf(stderr, "[GodotPS5 DIRACCESS 0.2.11] MKDIR_OK %s\n", c.get_data());
    return OK;
''',
    "Error DirAccessUnix::change_dir(String p_dir) {": r'''
    if (p_dir.is_relative_path()) p_dir = current_dir.path_join(p_dir);
    p_dir = fix_path(p_dir).simplify_path();
    if (!ps5_dir_exists_native(p_dir)) return ERR_INVALID_PARAMETER;
    current_dir = p_dir; // logical cwd, never libc chdir/getcwd
    return OK;
''',
}

def wrap_method(source: str, signature: str, ps5_impl: str) -> str:
    if source.count(signature) != 1:
        raise ValueError(f"Godot Unix source drift: {signature}")
    start = source.index(signature)
    open_brace = source.index("{", start)
    if open_brace != start + len(signature) - 1:
        raise ValueError("Unexpected method signature/opening brace")
    nesting = 1
    end = open_brace + 1
    while end < len(source) and nesting:
        if source[end] == "{": nesting += 1
        elif source[end] == "}": nesting -= 1
        end += 1
    if nesting: raise ValueError("Unbalanced original Godot method")
    body = source[open_brace + 1:end - 1]
    guarded = "\n#if defined(PS5_ENABLED)\n" + ps5_impl + "\n#else\n" + body + "\n#endif // PS5_ENABLED\n"
    return source[:open_brace + 1] + guarded + source[end - 1:]

def patch(source: str) -> str:
    if MARKER in source:
        if "ps5_dir_exists_native" not in source or "current_dir = \"/app0\";" not in source:
            raise ValueError("Partial PS5 DirAccess patch")
        return source
    if source.count(INCLUDE_ANCHOR) != 1:
        raise ValueError("Unknown Godot Unix directory include location")
    # Wrap each unsafe libc method. Preserve ALL FreeBSD/host original bodies.
    for key, replacement in NATIVE_METHODS.items():
        source = wrap_method(source, key, replacement)
    # DirAccessUnix() calls getcwd then change_dir as part of construction,
    # before derived or registered subclasses can override anything.
    ctor = "DirAccessUnix::DirAccessUnix() {"
    if source.count(ctor) != 1:
        raise ValueError("Godot DirAccessUnix constructor changed")
    start = source.index(ctor)
    stop = source.index("DirAccessUnix::remove_notification_func", start)
    part = source[start:stop]
    if part.count("\tchange_dir(current_dir);") != 1:
        raise ValueError("Unknown getcwd/change_dir constructor layout")
    part = part.replace(ctor, ctor + '\n#if defined(PS5_ENABLED)\n\tcurrent_dir = "/app0";\n#else', 1)
    part = part.replace("\tchange_dir(current_dir);", "\tchange_dir(current_dir);\n#endif // PS5_ENABLED", 1)
    source = source[:start] + part + source[stop:]
    source = source.replace(INCLUDE_ANCHOR, INCLUDE_ANCHOR + "\n" + INCLUDES, 1)
    return source

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: patch_ps5_dir_access.py /path/to/godot")
    path = Path(sys.argv[1]) / "drivers/unix/dir_access_unix.cpp"
    before = path.read_text()
    after = patch(before)
    if after != before: path.write_text(after)
    print("PS5 native DirAccess cwd/exists/mkdir/change_dir patch applied")
