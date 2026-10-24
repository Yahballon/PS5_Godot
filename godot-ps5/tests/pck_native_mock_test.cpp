// SPDX-License-Identifier: MIT
// Host mock of the native PS5 libkernel path; exercises FreeBSD getdents layout.
#define GODOT_PS5_NATIVE_IO 1
#include "../engine/platform/ps5/pck_locator.hpp"
#include <cassert>
#include <cstring>
#include <string>
#include <vector>

namespace {
bool directory_sent = false;
const unsigned char good[20] = {
    'G','D','P','C',4,0,0,0,4,0,0,0,7,0,0,0,2,0,0,0
};
void append_dirent(std::vector<unsigned char>& bytes, const std::string& name, unsigned char type) {
    const size_t record = (8 + name.size() + 1 + 3) & ~size_t(3);
    assert(record <= 0xffff && name.size() <= 255);
    const size_t at = bytes.size();
    bytes.resize(at + record, 0);
    bytes[at + 4] = static_cast<unsigned char>(record & 255);
    bytes[at + 5] = static_cast<unsigned char>(record >> 8);
    bytes[at + 6] = type;
    bytes[at + 7] = static_cast<unsigned char>(name.size());
    std::memcpy(bytes.data() + at + 8, name.data(), name.size());
}
}
extern "C" int sceKernelOpen(const char *path, int flags, int mode) {
    (void)mode;
    if (std::strcmp(path, "/data/GodotPS5/games") == 0 && (flags & O_DIRECTORY)) {
        directory_sent = false;
        return 100;
    }
    if (std::strcmp(path, "/data/GodotPS5/games/z.pck") == 0) return 101;
    if (std::strcmp(path, "/data/GodotPS5/games/a.pck") == 0) return 102;
    if (std::strcmp(path, "/data/GodotPS5/games/old.pck") == 0) return 103;
    // Treat symbolic links and unknown absolute paths as not openable.
    return -1;
}
extern "C" int sceKernelGetdents(int fd, char *output, int limit) {
    if (fd != 100 || directory_sent) return 0;
    directory_sent = true;
    std::vector<unsigned char> data;
    append_dirent(data, "z.pck", 8);
    append_dirent(data, "a.pck", 0); // DT_UNKNOWN on PS5 is a valid candidate
    append_dirent(data, "old.pck", 8);
    append_dirent(data, "link.pck", 10); // DT_LNK must be ignored
    append_dirent(data, "folder.pck", 4); // DT_DIR must be ignored
    append_dirent(data, "../unsafe.pck", 8);
    assert(data.size() <= static_cast<size_t>(limit));
    std::memcpy(output, data.data(), data.size());
    return static_cast<int>(data.size());
}
extern "C" int sceKernelClose(int fd) {
    return fd == 100 || fd == 101 || fd == 102 || fd == 103 ? 0 : -1;
}
extern "C" long sceKernelRead(int fd, void *buffer, size_t size) {
    if (fd != 101 && fd != 102 && fd != 103) return -1;
    const size_t count = size > sizeof(good) ? sizeof(good) : size;
    unsigned char bytes[sizeof(good)];
    std::memcpy(bytes, good, sizeof(good));
    if (fd == 103) bytes[8] = 3; // Godot 3 is rejected
    std::memcpy(buffer, bytes, count);
    return static_cast<long>(count);
}
int main() {
    assert(godot_ps5::valid_godot4_pack("/data/GodotPS5/games/a.pck"));
    assert(!godot_ps5::valid_godot4_pack("/data/GodotPS5/games/old.pck"));
    assert(!godot_ps5::valid_godot4_pack("/data/GodotPS5/games/link.pck"));
    assert(godot_ps5::first_pack_in("/data/GodotPS5/games") ==
           "/data/GodotPS5/games/a.pck");
    assert(godot_ps5::choose_pack() == "/data/GodotPS5/games/a.pck");
    assert(godot_ps5::choose_pack("/data/GodotPS5/games/old.pck").empty());
    std::puts("PASS: native PS5 getdents PCK scanner mock");
}
