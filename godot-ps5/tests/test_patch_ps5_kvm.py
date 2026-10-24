#!/usr/bin/env python3
"""Test the PS5 libkvm source guard; no false return values or fake stubs."""
from pathlib import Path
import importlib.util
import tempfile

target = Path(__file__).resolve().parents[1] / "scripts/patch_ps5_kvm.py"
spec = importlib.util.spec_from_file_location("patch_ps5_kvm", target)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

fixture = (
    '#if defined(__FreeBSD__)\n#include <kvm.h>\n#endif\n'
    'Dictionary OS_Unix::get_memory_info() const {\n'
    '\tuint64_t stotal = 0;\n\tuint64_t sused = 0;\n'
    '\tchar errmsg[_POSIX2_LINE_MAX] = {};\n'
    '\tkvm_t *kd = kvm_openfiles(nullptr, "/dev/null", nullptr, 0, errmsg);\n'
    '\tif (kd == nullptr) {\n'
    '\t\tERR_PRINT("error");\n'
    '\t} else {\n'
    '\t\tint count = kvm_getswapinfo(kd, nullptr, 0, 0);\n'
    '\t\t(void)count;\n'
    '\t\tkvm_close(kd);\n\t}\n'
    '\tmeminfo["available"] = 0;\n\treturn meminfo;\n}\n'
)
patched = module.patch(fixture)
assert '#if defined(__FreeBSD__) && !defined(PS5_ENABLED)' in patched
assert '#if !defined(PS5_ENABLED)\n\tchar errmsg' in patched
assert patched.count('#endif // !PS5_ENABLED') == 1
assert module.patch(patched) == patched
assert 'uint64_t stotal = 0;' in patched and 'uint64_t sused = 0;' in patched
try:
    module.patch("unrelated upstream source")
except ValueError:
    pass
else:
    raise AssertionError("unrecognized upstream source accepted")
print("PASS: PS5 libkvm guard, upstream FreeBSD unaffected, idempotence, fail-closed")
