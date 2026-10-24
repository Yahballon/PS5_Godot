#!/usr/bin/env python3
"""Regression: PS5 app must quit through the system shell, never libc exit()."""
from pathlib import Path

root=Path(__file__).resolve().parents[1]
source=(root/"native/engine_smoke_main.cpp").read_text()
assert 'extern "C" void catchReturnFromMain(int status)' in source
assert source.count('sceSystemServiceLoadExec("exit", nullptr)')==1
assert 'sceKernelUsleep(100000)' in source
assert 'std::fflush(nullptr);' in source
assert 'SHELL_EXIT_REQUEST v0.' in source, 'Missing versioned PS5 shell-exit marker'
assert 'exit(status)' not in source.split('extern "C" void catchReturnFromMain')[1]
print("PASS: PS5 shell exit hook avoids libc exit SIGSYS after main()")
