#!/usr/bin/env python3
"""Offline tests for safely resolving *weak undefined* C++ TLS init hooks."""
from pathlib import Path
import importlib.util
import tempfile

src=Path(__file__).resolve().parents[1]/"scripts/resolve_weak_tls.py"
spec=importlib.util.spec_from_file_location("tls",src)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
fixture="""
Symbol table '.dynsym' contains 5 entries:
   Num:    Value          Size Type    Bind   Vis      Ndx Name
    0: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT  UND
    1: 0000000000000000     0 FUNC    WEAK   DEFAULT  UND _ZTHN12MessageQueue16thread_singletonE
    2: 0000000000000000     0 FUNC    WEAK   DEFAULT  UND _ZTHN14ResourceLoader12load_nestingE
    3: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND sceKernelOpen
    4: 0000000000000000     0 FUNC    WEAK   DEFAULT  UND unrelated_weak_symbol
    5: 0000000000000000     0 FUNC    WEAK   DEFAULT  UND __cxa_thread_atexit_impl
"""
names=mod.parse_weak_tls(fixture)
assert names==sorted([
    "_ZTHN12MessageQueue16thread_singletonE",
    "_ZTHN14ResourceLoader12load_nestingE",
    "__cxa_thread_atexit_impl"
])
try:
    mod.parse_weak_tls(
        "  4: 0000000000000000   0 FUNC GLOBAL DEFAULT UND _ZTHDangerous")
except ValueError:
    pass
else:
    raise AssertionError("Strong undefined TLS hooks must not be hidden")
with tempfile.TemporaryDirectory() as d:
    build=Path(d)/"build.sh"
    build.write_text('link_inputs+=("--start-group")\nlink_inputs+=("--end-group")\n')
    assert mod.insert_optional_linker_zero(build,names)==3
    value=build.read_text()
    assert value.count("--defsym=_ZTHN12MessageQueue16thread_singletonE=0")==1
    assert value.count("--defsym=_ZTHN14ResourceLoader12load_nestingE=0")==1
    assert value.count("--defsym=__cxa_thread_atexit_impl=0")==1
    assert "--end-group" in value
    assert "sceKernelOpen" not in value
    try:
        mod.insert_optional_linker_zero(build,["_ZTHN12MessageQueue16thread_singletonE"])
    except ValueError:
        pass
    else:
        raise AssertionError("Duplicate TLS linker zero was silently accepted")
    try:
        mod.insert_optional_linker_zero(build,["; rm -rf /"])
    except ValueError:
        pass
    else:
        raise AssertionError("Unsafe linker symbol accepted")
print("PASS: PS5 C++ ELF weak TLS import rules and minimal safe linker changes")
