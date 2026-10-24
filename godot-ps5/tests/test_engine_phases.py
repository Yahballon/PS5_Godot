#!/usr/bin/env python3
"""Ensure PS5 crash phase markers surround actual Godot entrypoint calls."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
text = (root / "engine/platform/ps5/godot_ps5.cpp").read_text()
phase_pairs = [
    ("BEFORE_PROFILER_INIT", "AFTER_PROFILER_INIT", "godot_init_profiler();"),
    ("BEFORE_OS_PS5_CONSTRUCTOR", "AFTER_OS_PS5_CONSTRUCTOR", "OS_PS5 os;"),
    ("BEFORE_MAIN_SETUP", "AFTER_MAIN_SETUP", 'Main::setup("godot.ps5", count, args)'),
    ("BEFORE_MAIN_START", "AFTER_MAIN_START", "Main::start();"),
]
for pre, post, call in phase_pairs:
    assert text.count(pre) == 1, pre
    assert text.count(post) == 1, post
    assert text.count(call) == 1, call
    assert text.index(pre) < text.index(call) < text.index(post), (pre, post)
assert text.count("std::fflush(stderr);") >= len(phase_pairs) * 2
assert '0.2.11' in text
print("PASS: real PS5 Godot engine phase markers surround runtime initialization")
