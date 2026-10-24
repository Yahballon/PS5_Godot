// SPDX-License-Identifier: MIT
#pragma once
// Native PS5 EGL callbacks from a *separate experimental title*.
// ABI intentionally has no Godot, EGL, GPL, or SDK types. This allows
// replacing the implementation without rewriting Godot's DisplayServer.
//
// IMPORTANT: this API is NOT an installed title; only the EGL-backed native
// test sets these hooks before godot_ps5_run_pack().
struct GodotPS5GraphicsHooks {
    bool (*open)(int width, int height);
    bool (*swap)();
    void (*close)();
    void *(*get_gl_proc)(const char *name);
};

extern "C" void godot_ps5_set_graphics_hooks(const GodotPS5GraphicsHooks *hooks);
