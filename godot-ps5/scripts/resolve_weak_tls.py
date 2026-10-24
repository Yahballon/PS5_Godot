#!/usr/bin/env python3
"""Resolve narrowly allowlisted undefined weak ELF hooks before PS5 conversion.

On regular ELF, a weak undefined TLS-init function resolves to null; callers
check its address before calling. DevBridge's PS5 converter cannot import such
non-SDK symbols and rejects the PIE. Patch the *temporary* DevBridge linker
invocation so LLD binds those exact OPTIONAL hooks to the ELF null value.
Never replace strong symbols, TLS storage or ordinary runtime code.
"""
import argparse
from pathlib import Path
import re
import subprocess

CXX_TLS_INIT = re.compile(r"^_ZTH[A-Za-z0-9_]+$")
# libc++abi declares this optional C-library entry as WEAK and contains
# a real pthread-key fallback when the underlying libc does not export it.
# See LLVM libcxxabi/src/cxa_thread_atexit.cpp.
CXXABI_OPTIONAL_WEAK = {"__cxa_thread_atexit_impl"}
def allowed_weak(name: str) -> bool:
    return bool(CXX_TLS_INIT.fullmatch(name) or name in CXXABI_OPTIONAL_WEAK)
INJECTION_POINT = 'link_inputs+=("--end-group")'
SYM_ROW = re.compile(
    r"^\s*\d+:\s+[0-9a-fA-F]+\s+\d+\s+\S+\s+"
    r"(?P<binding>\S+)\s+\S+\s+(?P<section>\S+)\s+"
    r"(?P<name>\S+)"
)

def parse_weak_tls(readelf_output: str) -> list[str]:
    results = set()
    for line in readelf_output.splitlines():
        match = SYM_ROW.match(line)
        if not match:
            continue
        name = match.group("name").split("@", 1)[0]
        if allowed_weak(name) and match.group("section") == "UND":
            if match.group("binding") != "WEAK":
                raise ValueError("Strong undefined optional symbol: " + name)
            results.add(name)
    return sorted(results)

def insert_optional_linker_zero(build_sh: Path, names: list[str]) -> int:
    if not names:
        raise ValueError("No supported undefined weak hooks in linked PIE")
    source = build_sh.read_text()
    if source.count(INJECTION_POINT) != 1:
        raise ValueError("Missing precise PS5 link group marker")
    args = []
    for name in names:
        if not allowed_weak(name):
            raise ValueError("Unsafe or non-optional-weak symbol: " + name)
        if '--defsym=' + name + '=0' not in source:
            args.append('link_inputs+=("--defsym=' + name + '=0")')
    if not args:
        raise ValueError("No new supported weak hooks to resolve")
    source = source.replace(INJECTION_POINT,
                            "\n".join(args) + "\n" + INJECTION_POINT, 1)
    build_sh.write_text(source)
    print("ELF optional weak hooks bound to null:", ", ".join(names))
    return len(args)

def resolve_from_elf(elf: Path, build_sh: Path, readelf: str) -> int:
    if not elf.is_file():
        raise ValueError("Initial PS5 PIE ELF was not produced")
    output = subprocess.check_output(
        [readelf, "--dyn-syms", "--wide", str(elf)], text=True
    )
    return insert_optional_linker_zero(build_sh, parse_weak_tls(output))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--build-sh", type=Path, required=True)
    parser.add_argument("--readelf", default="llvm-readelf-18")
    arguments = parser.parse_args()
    resolve_from_elf(arguments.elf, arguments.build_sh, arguments.readelf)
