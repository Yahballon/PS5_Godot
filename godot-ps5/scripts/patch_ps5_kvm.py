#!/usr/bin/env python3
"""Patch Godot 4.7.2's FreeBSD-only libkvm memory query for PS5.

The PS5 homebrew SDK has FreeBSD headers but not the userland libkvm
functions used to query swap. Preserve the upstream memory sysctl path,
and report available memory without a swap figure rather than linking
dummy kvm APIs. On other FreeBSD targets, upstream code is unchanged.
"""
from pathlib import Path
import sys

HEADER = "#if defined(__FreeBSD__)\n#include <kvm.h>\n#endif"
KVM_START = "\tchar errmsg[_POSIX2_LINE_MAX] = {};\n\tkvm_t *kd = kvm_openfiles("
KVM_END = "\t\tkvm_close(kd);\n\t}\n"

def patch(contents: str) -> str:
    # Must target precisely upstream Godot 4.7.2, not any similar code.
    if "#if !defined(PS5_ENABLED)\n\tchar errmsg" in contents:
        if "#if defined(__FreeBSD__) && !defined(PS5_ENABLED)\n#include <kvm.h>" in contents:
            return contents  # idempotent
        raise ValueError("partially patched Godot source")
    if contents.count(HEADER) != 1 or contents.count(KVM_START) != 1 or contents.count(KVM_END) != 1:
        raise ValueError("Godot 4.7.2 libkvm source layout differs; refusing patch")
    begin = contents.index(KVM_START)
    end = contents.index(KVM_END, begin) + len(KVM_END)
    func = contents.rfind("Dictionary OS_Unix::get_memory_info() const", 0, begin)
    next_func = contents.find("return meminfo;", end)
    if func == -1 or next_func == -1 or end > next_func:
        raise ValueError("libkvm block not in expected get_memory_info() function")
    # Apply the positional edit BEFORE changing the earlier #include text.
    # Otherwise offsets shift and truncate the wrong bytes.
    contents = contents[:begin] + "#if !defined(PS5_ENABLED)\n" + contents[begin:end] + "#endif // !PS5_ENABLED: no libkvm in PS5 homebrew\n" + contents[end:]
    return contents.replace(
        HEADER, "#if defined(__FreeBSD__) && !defined(PS5_ENABLED)\n#include <kvm.h>\n#endif", 1
    )

def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: patch_ps5_kvm.py /path/to/godot")
    file = Path(sys.argv[1]) / "drivers/unix/os_unix.cpp"
    before = file.read_text()
    after = patch(before)
    file.write_text(after) if after != before else None
    print("PS5 libkvm query disabled in Godot OS_Unix; sysctl memory path retained")

if __name__ == "__main__":
    main()
