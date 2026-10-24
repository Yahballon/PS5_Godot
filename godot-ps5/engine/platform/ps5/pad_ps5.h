// SPDX-License-Identifier: MIT
#pragma once
#include <cstdint>
#include <cstddef>

// Independent PS5 controller protocol adapter. Pure mapping lives here so
// host CI can verify behavior without PS5 SDK headers or runtime imports.
namespace ps5_pad {
struct Sample {
    uint32_t buttons = 0;
    uint8_t lx = 128, ly = 128, rx = 128, ry = 128;
    uint8_t l2 = 0, r2 = 0;
    bool connected = false;
};
struct Mapping {
    uint32_t native_bit;
    int godot_button;
};
constexpr Mapping kButtons[] = {
    {0x00004000u, 0},  // Cross = Godot A
    {0x00002000u, 1},  // Circle = B
    {0x00008000u, 2},  // Square = X
    {0x00001000u, 3},  // Triangle = Y
    {0x00000008u, 6},  // Options = START
    {0x00000002u, 7},  // L3
    {0x00000004u, 8},  // R3
    {0x00000400u, 9},  // L1
    {0x00000800u, 10}, // R1
    {0x00000010u, 11}, // Up
    {0x00000040u, 12}, // Down
    {0x00000080u, 13}, // Left
    {0x00000020u, 14}, // Right
    {0x00100000u, 20}, // Touchpad click
};
inline float axis(uint8_t value, bool flip = false) {
    const float v = (static_cast<float>(value) - 127.5f) / 127.5f;
    const float out = flip ? -v : v;
    return (out > -0.12f && out < 0.12f) ? 0.0f :
        (out < -1.0f ? -1.0f : out > 1.0f ? 1.0f : out);
}
inline float trigger(uint8_t value) { return static_cast<float>(value) / 255.0f; }
struct RawReport {
    uint32_t buttons;
    uint8_t lx, ly, rx, ry, l2, r2;
    uint8_t reserved[66];
    int32_t connected;
    uint64_t timestamp_us;
    uint8_t extension[16];
    uint8_t connected_count;
    uint8_t tail[15];
};
static_assert(sizeof(RawReport) == 120, "scePadRead raw sample ABI changed");
static_assert(offsetof(RawReport, connected) == 0x4c, "PS5 pad status alignment mismatch");
static_assert(offsetof(RawReport, timestamp_us) == 0x50, "PS5 pad timestamp ABI mismatch");

class Bridge {
    int handle = -1;
    int initial_user = -1;
    int retry_ticks = 0;
    bool user_service_owned = false;
    bool connected = false;
    uint32_t last_buttons = 0;
    float last_axes[6] = {0};
public:
    void initialize();
    void poll();
    void shutdown();
};
} // namespace ps5_pad
