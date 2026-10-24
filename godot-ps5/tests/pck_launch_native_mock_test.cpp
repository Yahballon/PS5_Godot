// SPDX-License-Identifier: MIT
#define GODOT_PS5_NATIVE_IO 1
#include "../engine/platform/ps5/pck_launch_config.hpp"
#include <cassert>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

static std::string selected_config;
static std::string expected_external;
static bool config_present = true;
static int opens = 0;
static bool usb_fixture_present = false;
static bool usb_demo_present = false;
static bool usb_directory_emitted = false;
extern "C" int sceKernelOpen(const char *path, int, int) {
    ++opens;
    const std::string name(path);
    if (name == "/data/GodotPS5/launch.txt") return config_present ? 10 : -1;
    if (name == expected_external && !expected_external.empty()) return 11;
    if (name == "/app0/assets/godot/smoke.pck") return 12;
    if (name == "/mnt/usb0/godot") {
        usb_directory_emitted = false;
        return 14;
    }
    if (usb_fixture_present && name == "/mnt/usb0/godot/smoke.pck") return 15;
    if (usb_demo_present && name == "/mnt/usb0/godot/Demo.pck") return 16;
    if (name == "/data/GodotPS5/games" || name.find("/godot") != std::string::npos)
        return 13; // Mock empty game directories
    return -1;
}
extern "C" long sceKernelRead(int fd, void *buf, size_t len) {
    if (fd == 10) {
        const size_t count = std::min(len, selected_config.size());
        std::memcpy(buf, selected_config.data(), count);
        return long(count);
    }
    if (fd == 11 || fd == 12 || fd == 15 || fd == 16) {
        const unsigned char h[20] = {
            'G','D','P','C',2,0,0,0,4,0,0,0,7,0,0,0,0,0,0,0
        };
        const size_t count = std::min(len, sizeof(h));
        std::memcpy(buf, h, count);
        return long(count);
    }
    return -1;
}
extern "C" int sceKernelGetdents(int fd, char *out, int max_len) {
    if (fd != 14 || usb_directory_emitted || (!usb_fixture_present && !usb_demo_present)) return 0;
    usb_directory_emitted = true;
    std::vector<unsigned char> bytes;
    auto add = [&](const char *name) {
        const size_t n = std::strlen(name);
        const size_t reclen = (8 + n + 1 + 3) & ~size_t(3);
        const size_t at = bytes.size();
        bytes.resize(at + reclen, 0);
        bytes[at + 4] = static_cast<unsigned char>(reclen & 255);
        bytes[at + 5] = static_cast<unsigned char>(reclen >> 8);
        bytes[at + 6] = 8; // DT_REG
        bytes[at + 7] = static_cast<unsigned char>(n);
        std::memcpy(bytes.data() + at + 8, name, n);
    };
    if (usb_fixture_present) add("smoke.pck");
    if (usb_demo_present) add("Demo.pck");
    assert(bytes.size() <= static_cast<size_t>(max_len));
    std::memcpy(out, bytes.data(), bytes.size());
    return static_cast<int>(bytes.size());
}
extern "C" int sceKernelClose(int) { return 0; }

int main() {
    using namespace godot_ps5;
    selected_config = "/mnt/usb0/godot/External.PCK\n";
    expected_external = "/mnt/usb0/godot/External.PCK";
    auto x = select_runtime_pack();
    assert(x.source == PackSource::Config && x.path == expected_external);
    selected_config = "/mnt/usb0/godot/../INVALID.pck";
    x = select_runtime_pack();
    assert(x.source == PackSource::BundledSmoke);
    assert(x.path == "/app0/assets/godot/smoke.pck");
    config_present = false;
    x = select_runtime_pack();
    assert(x.source == PackSource::BundledSmoke);
    assert(opens > 3);
    usb_fixture_present = true;
    x = select_runtime_pack();
    assert(x.source == PackSource::BundledSmoke);
    assert(x.path == "/app0/assets/godot/smoke.pck");
    usb_demo_present = true;
    x = select_runtime_pack();
    assert(x.source == PackSource::AutoScan);
    assert(x.path == "/mnt/usb0/godot/Demo.pck");
    // A user can still explicitly select the external smoke pack.
    selected_config = "/mnt/usb0/godot/smoke.pck\n";
    config_present = true;
    x = select_runtime_pack();
    assert(x.source == PackSource::Config);
    assert(x.path == "/mnt/usb0/godot/smoke.pck");
    std::cout << "PASS: PS5 libkernel config / skip stale smoke autoscan / external demo / bundled fallback\n";
}
