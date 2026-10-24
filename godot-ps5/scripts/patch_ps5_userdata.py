#!/usr/bin/env python3
"""Godot 4.7.2 PS5-only kernel-backed user-data creation.

The previous hardware build v0.2.9 stops at BEFORE_ENSURE_USER_DATA.
Upstream OS::ensure_user_data_dir uses DirAccessUnix stat/mkdir/chdir
through incomplete PS5 libc. Keep other platforms unchanged; on PS5,
use the real sceKernelMkdir + sceKernelOpen directory APIs.
"""
from pathlib import Path
import sys

ORIGINAL = """void OS::ensure_user_data_dir() {
	String dd = get_user_data_dir();
	if (DirAccess::exists(dd)) {
		return;
	}

	Ref<DirAccess> da = DirAccess::create(DirAccess::ACCESS_FILESYSTEM);
	Error err = da->make_dir_recursive(dd);
	ERR_FAIL_COND_MSG(err != OK, vformat("Error attempting to create data dir: %s.", dd));
}"""

NATIVE = r"""void OS::ensure_user_data_dir() {
#if defined(PS5_ENABLED)
	// The app owns /data/GodotPS5. Do not use upstream DirAccessUnix here:
	// its libc stat()/mkdir() path crashes on this PS5 homebrew runtime.
	const String dd = get_user_data_dir();
	const CharString utf8 = dd.utf8();
	const char *requested = utf8.get_data();
	constexpr char root[] = "/data/GodotPS5";
	constexpr size_t root_len = sizeof(root) - 1;
	const size_t count = std::strlen(requested);
	if (count < root_len || count >= 768 || std::memcmp(requested, root, root_len) != 0 ||
			(requested[root_len] != '\0' && requested[root_len] != '/') ||
			std::strstr(requested, "/../") || std::strstr(requested, "/./") ||
			(count >= 3 && std::strcmp(requested + count - 3, "/..") == 0)) {
		std::fprintf(stderr, "[GodotPS5 USERDATA 0.2.11] UNSAFE_PATH %s\n", requested);
		std::fflush(stderr);
		return;
	}

	char current[768];
	std::memcpy(current, requested, count + 1);
	// Create/verify every component under the dedicated app data root.
	// An existing directory yields an expected mkdir error; successful
	// open(O_DIRECTORY) is our authoritative verification.
	for (size_t end = root_len; end <= count; ++end) {
		if (current[end] != '/' && current[end] != '\0') {
			continue;
		}
		const char saved = current[end];
		current[end] = '\0';
		const int make_result = sceKernelMkdir(current, 0755);
		const int fd = sceKernelOpen(current, O_RDONLY | O_DIRECTORY, 0);
		if (fd < 0) {
			std::fprintf(stderr, "[GodotPS5 USERDATA 0.2.11] DIR_FAILED %s mkdir=%d\n", current, make_result);
			std::fflush(stderr);
			return;
		}
		sceKernelClose(fd);
		std::fprintf(stderr, "[GodotPS5 USERDATA 0.2.11] DIR_OK %s\n", current);
		std::fflush(stderr);
		current[end] = saved;
	}
#else
	String dd = get_user_data_dir();
	if (DirAccess::exists(dd)) {
		return;
	}

	Ref<DirAccess> da = DirAccess::create(DirAccess::ACCESS_FILESYSTEM);
	Error err = da->make_dir_recursive(dd);
	ERR_FAIL_COND_MSG(err != OK, vformat("Error attempting to create data dir: %s.", dd));
#endif
}"""

INCLUDE_ANCHOR = '#include "os.h"'
INCLUDES = r'''#if defined(PS5_ENABLED)
#include <cstdio>
#include <cstring>
#include <fcntl.h>
extern "C" int sceKernelMkdir(const char *, int);
extern "C" int sceKernelOpen(const char *, int, int);
extern "C" int sceKernelClose(int);
#endif
'''

def patch(contents: str) -> str:
    if "[GodotPS5 USERDATA 0.2.11]" in contents:
        if "sceKernelMkdir(current, 0755)" not in contents:
            raise ValueError("Partial PS5 userdata source patch")
        return contents
    if contents.count(ORIGINAL) != 1:
        raise ValueError("Pinned Godot OS::ensure_user_data_dir source layout changed")
    if contents.count(INCLUDE_ANCHOR) != 1:
        raise ValueError("Pinned Godot OS header layout changed")
    # Replace method before earlier includes alter file offsets.
    result = contents.replace(ORIGINAL, NATIVE, 1)
    return result.replace(INCLUDE_ANCHOR, INCLUDE_ANCHOR + '\n' + INCLUDES, 1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: patch_ps5_userdata.py /path/to/godot")
    file = Path(sys.argv[1]) / "core/os/os.cpp"
    before = file.read_text()
    after = patch(before)
    if after != before:
        file.write_text(after)
    print("PS5 kernel-backed Godot userdata path patch applied")
