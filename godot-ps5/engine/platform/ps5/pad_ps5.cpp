// SPDX-License-Identifier: MIT
// Native DualSense to original Godot 4 Input bridge (experimental).
#include "pad_ps5.h"
#include "core/input/input.h"
#include <cstdio>
#include <cstring>

extern "C" {
int sceUserServiceInitialize(const void *);
int sceUserServiceGetInitialUser(int *);
int sceUserServiceTerminate();
int scePadInit();
int scePadOpen(int user, int type, int index, const void *);
int scePadRead(int handle, ps5_pad::RawReport *, int);
int scePadClose(int handle);
}

namespace ps5_pad {
void Bridge::initialize() {
    // Godot constructs its Input singleton before calling initialize_joypads.
    if (!Input::get_singleton()) return;
    const int user_init = sceUserServiceInitialize(nullptr);
    user_service_owned = user_init == 0;
    if (user_init != 0 && static_cast<uint32_t>(user_init) != 0x80960003u)
        std::fprintf(stderr, "[GodotPS5 PAD] USER_INIT status=0x%08x\n", unsigned(user_init));
    int rc = sceUserServiceGetInitialUser(&initial_user);
    if (rc != 0) {
        std::fprintf(stderr, "[GodotPS5 PAD] NO_USER status=0x%08x\n", unsigned(rc));
        initial_user = -1;
        return;
    }
    const int pad_init = scePadInit();
    std::fprintf(stderr, "[GodotPS5 PAD] SDK_INIT status=0x%08x user=%d\n",
                 unsigned(pad_init), initial_user);
    std::fflush(stderr);
    retry_ticks = 0;
}

void Bridge::poll() {
    Input *const input = Input::get_singleton();
    if (!input) return;
    if (handle < 0) {
        if (initial_user < 0) return;
        if (retry_ticks-- > 0) return;
        retry_ticks = 120; // Retry once in roughly two seconds at 60 fps.
        handle = scePadOpen(initial_user, 0, 0, nullptr);
        if (handle < 0) return;
        std::fprintf(stderr, "[GodotPS5 PAD] PAD_OPEN handle=%d\n", handle);
        std::fflush(stderr);
        connected = false;
        last_buttons = 0;
        std::memset(last_axes, 0, sizeof(last_axes));
    }

    RawReport samples[32]{};
    const int count = scePadRead(handle, samples, 32);
    if (count < 0) {
        if (connected) {
            input->joy_connection_changed(0, false, "DualSense");
            connected = false;
        }
        scePadClose(handle);
        handle = -1;
        retry_ticks = 120;
        std::fprintf(stderr, "[GodotPS5 PAD] PAD_READ_FAILED status=0x%08x\n", unsigned(count));
        return;
    }
    if (count > 32) return;
    for (int i = 0; i < count; ++i) {
        const RawReport &raw = samples[i];
        if (raw.connected == 0 || (raw.buttons & 0x80000000u)) {
            if (connected) {
                input->joy_connection_changed(0, false, "DualSense");
                connected = false;
                last_buttons = 0;
                std::fprintf(stderr, "[GodotPS5 PAD] DISCONNECTED_OR_INTERCEPTED\n");
            }
            continue;
        }
        if (!connected) {
            Dictionary info;
            info["mapping_handled"] = true;
            input->joy_connection_changed(0, true, "DualSense PS5", "ps5-dualsense", info);
            connected = true;
            last_buttons = 0;
            std::memset(last_axes, 0, sizeof(last_axes));
            std::fprintf(stderr, "[GodotPS5 PAD] CONNECTED dev=0\n");
        }
        for (const Mapping &map : kButtons) {
            const uint32_t changed = last_buttons ^ raw.buttons;
            if (changed & map.native_bit) {
                const bool down = (raw.buttons & map.native_bit) != 0;
                input->joy_button(0, static_cast<JoyButton>(map.godot_button), down);
                if (map.godot_button == 0) {
                    std::fprintf(stderr, "[GodotPS5 PAD] CROSS_%s\n", down ? "DOWN" : "UP");
                    std::fflush(stderr);
                }
            }
        }
        last_buttons = raw.buttons;
        const float axes[6] = {
            axis(raw.lx), axis(raw.ly), axis(raw.rx), axis(raw.ry),
            trigger(raw.l2), trigger(raw.r2)
        };
        for (int a = 0; a < 6; ++a) {
            if (axes[a] != last_axes[a]) {
                last_axes[a] = axes[a];
                input->joy_axis(0, static_cast<JoyAxis>(a), axes[a]);
            }
        }
    }
}

void Bridge::shutdown() {
    if (connected && Input::get_singleton()) {
        Input::get_singleton()->joy_connection_changed(0, false, "DualSense");
    }
    connected = false;
    if (handle >= 0) {
        scePadClose(handle);
        handle = -1;
    }
    if (user_service_owned) sceUserServiceTerminate();
    user_service_owned = false;
}
} // namespace ps5_pad
