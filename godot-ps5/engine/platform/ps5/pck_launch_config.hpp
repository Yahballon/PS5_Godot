// SPDX-License-Identifier: MIT
// Generic Godot 4 PCK launching from PS5 homebrew folders.
// All external paths are screened before the original Godot engine sees them.
#pragma once
#include "pck_locator.hpp"
#include <string>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <fcntl.h>

namespace godot_ps5 {
enum class PackSource { Config, AutoScan, BundledSmoke, None };
struct PackSelection { std::string path; PackSource source; };

inline bool trusted_external_path(const std::string &path) {
    if (path.size() < 5 || path.size() > 900 || path[0] != '/' ||
        !pack_name(path) || path.find('\\') != std::string::npos ||
        path.find("//") != std::string::npos) return false;
    for (unsigned char c : path)
        if (c < 32 || c == 127) return false;
    // Verify WHOLE path components, not substrings (example: game..pck).
    size_t start = 1;
    while (start < path.size()) {
        const size_t end = path.find('/', start);
        const size_t n = (end == std::string::npos ? path.size() : end) - start;
        if (!n || (n == 1 && path[start] == '.') ||
            (n == 2 && path[start] == '.' && path[start+1] == '.'))
            return false;
        if (end == std::string::npos) break;
        start = end + 1;
    }
    if (!safe_filename(path.substr(path.find_last_of('/') + 1))) return false;
    for (const char *root : {
            "/data/GodotPS5/games/", "/mnt/usb0/godot/",
            "/mnt/usb1/godot/", "/mnt/usb2/godot/",
            "/mnt/usb3/godot/", "/mnt/usb0/GodotPS5/games/"}) {
        if (path.rfind(root, 0) == 0 && path.size() > std::strlen(root))
            return true;
    }
    return false;
}

inline std::string parse_launch_txt(std::string value) {
    if (value.size() > 1024) return {};
    if (value.rfind("\xEF\xBB\xBF", 0) == 0) value.erase(0, 3);
    const size_t end = value.find_first_of("\r\n");
    if (end != std::string::npos) value.resize(end);
    const size_t from = value.find_first_not_of(" \t");
    if (from == std::string::npos) return {};
    const size_t to = value.find_last_not_of(" \t");
    value = value.substr(from, to-from+1);
    if (value.empty() || value[0] == '#') return {};
    if (value.find('/') == std::string::npos && safe_filename(value)) {
        value = std::string("/data/GodotPS5/games/") + value;
    }
    return trusted_external_path(value) ? value : std::string();
}

inline std::string read_launch_txt() {
    const char *conf = "/data/GodotPS5/launch.txt";
    char bytes[1025] {};
#if defined(GODOT_PS5_NATIVE_IO)
    const int fd = sceKernelOpen(conf, O_RDONLY | O_NOFOLLOW, 0);
    if (fd < 0) return {};
    const long n = sceKernelRead(fd, bytes, sizeof(bytes));
    sceKernelClose(fd);
    return (n <= 0 || size_t(n) >= sizeof(bytes))
        ? std::string() : parse_launch_txt(std::string(bytes, size_t(n)));
#else
    FILE *f = std::fopen(conf, "rb");
    if (!f) return {};
    const size_t n = std::fread(bytes, 1, sizeof(bytes), f);
    std::fclose(f);
    return (n == 0 || n == sizeof(bytes))
        ? std::string() : parse_launch_txt(std::string(bytes, n));
#endif
}

inline PackSelection select_runtime_pack() {
    const std::string requested = read_launch_txt();
    if (trusted_external_path(requested) && valid_godot4_pack(requested))
        return {requested, PackSource::Config};
    for (const char *root : {
            "/data/GodotPS5/games", "/mnt/usb0/godot",
            "/mnt/usb1/godot", "/mnt/usb2/godot",
            "/mnt/usb3/godot", "/mnt/usb0/GodotPS5/games"}) {
        const std::string found = first_pack_in(root, true);
        if (!found.empty() && trusted_external_path(found))
            return {found, PackSource::AutoScan};
    }
    constexpr char bundled[] = "/app0/assets/godot/smoke.pck";
    if (valid_godot4_pack(bundled))
        return {bundled, PackSource::BundledSmoke};
    return {{}, PackSource::None};
}

inline const char *pack_source_name(PackSource s) {
    switch(s) {
        case PackSource::Config: return "CONFIG";
        case PackSource::AutoScan: return "AUTOSCAN";
        case PackSource::BundledSmoke: return "BUNDLED_SMOKE";
        default: return "NONE";
    }
}
} // namespace godot_ps5
