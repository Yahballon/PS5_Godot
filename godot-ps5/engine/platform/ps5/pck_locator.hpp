// SPDX-License-Identifier: MIT
// PS5 PCK discovery using public libkernel, avoiding libc opendir/stat in
// the sandbox. Files are only screened, not interpreted as trusted game data.
#pragma once
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include <fcntl.h>

#if defined(GODOT_PS5_NATIVE_IO)
extern "C" int sceKernelOpen(const char *, int, int);
extern "C" int sceKernelGetdents(int, char *, int);
extern "C" int sceKernelClose(int);
extern "C" long sceKernelRead(int, void *, size_t);
#else
#include <dirent.h>
#include <sys/stat.h>
#endif

namespace godot_ps5 {
inline bool pack_name(std::string n) {
    if (n.size() < 5 || n.size() > 255) return false;
    n = n.substr(n.size()-4);
    for (char &c : n) if (c >= 'A' && c <= 'Z') c = char(c + ('a' - 'A'));
    return n == ".pck";
}
inline bool safe_filename(const std::string &n) {
    if (!pack_name(n) || n[0] == '.') return false;
    for (unsigned char c : n)
        if (c < 32 || c == 127 || c == '/' || c == '\\') return false;
    return true;
}
inline unsigned read_u32(const unsigned char *p) {
    return unsigned(p[0]) | unsigned(p[1]) << 8 |
           unsigned(p[2]) << 16 | unsigned(p[3]) << 24;
}
inline bool pack_header_compatible(const unsigned char *p, size_t n) {
    return n >= 20 && std::memcmp(p, "GDPC", 4) == 0 &&
           read_u32(p+4) >= 2 && read_u32(p+4) <= 4 &&
           read_u32(p+8) == 4 && read_u32(p+12) <= 7;
}
inline bool valid_godot4_pack(const std::string &path) {
    if (path.empty() || path.size() >= 1024 || path[0] != '/') return false;
    unsigned char header[20] {};
#if defined(GODOT_PS5_NATIVE_IO)
    const int fd = sceKernelOpen(path.c_str(), O_RDONLY | O_NOFOLLOW, 0);
    if (fd < 0) return false;
    size_t done = 0;
    while (done < sizeof(header)) {
        const long n = sceKernelRead(fd, header+done, sizeof(header)-done);
        if (n <= 0 || size_t(n) > sizeof(header)-done) break;
        done += size_t(n);
    }
    sceKernelClose(fd);
    return pack_header_compatible(header, done);
#else
    struct stat st {};
    if (lstat(path.c_str(), &st) || !S_ISREG(st.st_mode) || st.st_size < 20) return false;
    FILE *f = std::fopen(path.c_str(), "rb");
    if (!f) return false;
    const size_t n = std::fread(header, 1, sizeof(header), f);
    std::fclose(f);
    return pack_header_compatible(header, n);
#endif
}
// Do not let a stale external smoke.pck silently override the bundled
// controller acceptance fixture. Explicit launch.txt may still select it.
inline bool is_legacy_smoke_pack(const std::string &name) {
    constexpr char expected[] = "smoke.pck";
    if (name.size() != sizeof(expected) - 1) return false;
    for (size_t i = 0; i < sizeof(expected) - 1; ++i) {
        char c = name[i];
        if (c >= 'A' && c <= 'Z') c = char(c + ('a' - 'A'));
        if (c != expected[i]) return false;
    }
    return true;
}
inline std::string first_pack_in(const char *root, bool skip_legacy_smoke = false) {
    std::vector<std::string> found;
    constexpr size_t max_entries = 2048, max_pcks = 256;
#if defined(GODOT_PS5_NATIVE_IO)
    const int fd = sceKernelOpen(root, O_RDONLY | O_DIRECTORY | O_NOFOLLOW, 0);
    if (fd < 0) return {};
    alignas(0x4000) unsigned char buffer[0x10000] {};
    size_t scanned = 0;
    bool malformed = false;
    while (scanned < max_entries && found.size() < max_pcks) {
        const int n = sceKernelGetdents(fd, reinterpret_cast<char *>(buffer), sizeof(buffer));
        if (n <= 0 || size_t(n) > sizeof(buffer)) break;
        size_t at = 0;
        while (at < size_t(n) && scanned < max_entries) {
            ++scanned;
            if (at+8 > size_t(n)) { malformed = true; break; }
            const unsigned char *p = buffer+at;
            const size_t reclen = size_t(p[4]) | (size_t(p[5]) << 8);
            const size_t namelen = p[7];
            if (reclen < 12 || reclen % 4 || at+reclen > size_t(n) ||
                !namelen || 8+namelen >= reclen) { malformed = true; break; }
            const unsigned char type = p[6];
            const std::string name(reinterpret_cast<const char *>(p+8), namelen);
            at += reclen;
            if (type != 0 && type != 8) continue; // DT_UNKNOWN or DT_REG
            if (!safe_filename(name) || (skip_legacy_smoke && is_legacy_smoke_pack(name))) continue;
            const auto path = std::string(root)+"/"+name;
            if (valid_godot4_pack(path)) found.push_back(path);
            if (found.size() >= max_pcks) break;
        }
        if (malformed) break;
    }
    sceKernelClose(fd);
#else
    DIR *dir = opendir(root);
    if (!dir) return {};
    size_t scanned = 0;
    while (dirent *entry = readdir(dir)) {
        if (++scanned > max_entries) break;
        const std::string name(entry->d_name);
        if (!safe_filename(name) || (skip_legacy_smoke && is_legacy_smoke_pack(name))) continue;
        const auto path = std::string(root)+"/"+name;
        if (valid_godot4_pack(path)) found.push_back(path);
        if (found.size() >= max_pcks) break;
    }
    closedir(dir);
#endif
    std::sort(found.begin(), found.end());
    return found.empty() ? std::string() : found.front();
}
inline std::string choose_pack(const char *requested = nullptr) {
    if (requested && *requested)
        return valid_godot4_pack(requested) ? std::string(requested) : std::string();
    for (const char *root : {"/data/GodotPS5/games", "/mnt/usb0/godot",
                              "/mnt/usb1/godot", "/mnt/usb0/GodotPS5/games"}) {
        const std::string found = first_pack_in(root);
        if (!found.empty()) return found;
    }
    return {};
}
} // namespace godot_ps5
