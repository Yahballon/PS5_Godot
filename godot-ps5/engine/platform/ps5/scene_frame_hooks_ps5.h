// SPDX-License-Identifier: MIT
#pragma once
// Stable ABI for the experimental native PS5 Godot scene-state preview.
// This does NOT render anything: the actual scene is updated by GDScript.
// Shared by platform/ps5/os_ps5.cpp and native/scene_bridge_main.cpp.
// Keeping one signature prevents native/engine callback drift.
#include <stdint.h>
using GodotPS5SceneFrameCallback = void (*)(float sprite_x, float rotation,
        int cross_count, uint32_t main_loop_us, uint32_t pad_poll_us);
extern "C" void godot_ps5_set_scene_frame_callback(GodotPS5SceneFrameCallback cb);
