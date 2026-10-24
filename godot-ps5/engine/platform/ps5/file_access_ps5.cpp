// SPDX-License-Identifier: MIT
#include "file_access_ps5.h"
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <fcntl.h>
#include <unistd.h>

extern "C" int sceKernelOpen(const char *, int, int);
extern "C" long sceKernelRead(int, void *, size_t);
extern "C" long long sceKernelLseek(int, long long, int);
extern "C" int sceKernelClose(int);

bool FileAccessPS5::native_mount(const String &path) {
    return path.begins_with("/app0/") ||
           path.begins_with("/mnt/usb0/") ||
           path.begins_with("/mnt/usb1/") ||
           path.begins_with("/mnt/usb2/") ||
           path.begins_with("/mnt/usb3/") ||
           path.begins_with("/data/") ||
           path.begins_with("/download0/");
}

int FileAccessPS5::open_native(const String &path) {
    if (!native_mount(path)) return -1;
    const CharString utf8 = path.utf8();
    return sceKernelOpen(utf8.get_data(), O_RDONLY | O_NOFOLLOW, 0);
}

Error FileAccessPS5::open_internal(const String &p_path, int p_mode_flags) {
    close();
    original_path = p_path;
    native_path = fix_path(p_path);
    native_eof = false;
    native_error = OK;
    if (p_mode_flags == READ && native_mount(native_path)) {
        native_fd = open_native(native_path);
        if (native_fd < 0) {
            native_error = ERR_FILE_NOT_FOUND;
            std::fprintf(stderr, "[GodotPS5 IO] OPEN_FAILED %s\n", native_path.utf8().get_data());
            return native_error;
        }
        // M15: repeated PCK opens were synchronously flushed to the
        // unbuffered console log, even during gameplay. Bound successful
        // path diagnostics; preserve every failed open and native IO behavior.
        static std::atomic<unsigned> successful_open_logs{0};
        if (successful_open_logs.fetch_add(1, std::memory_order_relaxed) < 8)
            std::fprintf(stderr, "[GodotPS5 IO] OPEN_OK %s\n", native_path.utf8().get_data());
        return OK;
    }
    return FileAccessUnix::open_internal(p_path, p_mode_flags);
}

bool FileAccessPS5::is_open() const {
    return kernel_backed() || FileAccessUnix::is_open();
}

String FileAccessPS5::get_path() const {
    return kernel_backed() ? original_path : FileAccessUnix::get_path();
}

String FileAccessPS5::get_path_absolute() const {
    return kernel_backed() ? native_path : FileAccessUnix::get_path_absolute();
}

void FileAccessPS5::seek(uint64_t position) {
    if (!kernel_backed()) { FileAccessUnix::seek(position); return; }
    if (position > INT64_MAX || sceKernelLseek(native_fd, static_cast<int64_t>(position), SEEK_SET) < 0) {
        native_error = ERR_FILE_CANT_READ;
    } else {
        native_eof = false;
        native_error = OK;
    }
}

void FileAccessPS5::seek_end(int64_t offset) {
    if (!kernel_backed()) { FileAccessUnix::seek_end(offset); return; }
    if (sceKernelLseek(native_fd, offset, SEEK_END) < 0) native_error = ERR_FILE_CANT_READ;
    else { native_eof = false; native_error = OK; }
}

uint64_t FileAccessPS5::get_position() const {
    if (!kernel_backed()) return FileAccessUnix::get_position();
    const long long p = sceKernelLseek(native_fd, 0, SEEK_CUR);
    if (p < 0) { native_error = ERR_FILE_CANT_READ; return 0; }
    return static_cast<uint64_t>(p);
}

uint64_t FileAccessPS5::get_length() const {
    if (!kernel_backed()) return FileAccessUnix::get_length();
    const long long p = sceKernelLseek(native_fd, 0, SEEK_CUR);
    if (p < 0) { native_error = ERR_FILE_CANT_READ; return 0; }
    const long long length = sceKernelLseek(native_fd, 0, SEEK_END);
    const long long restored = sceKernelLseek(native_fd, p, SEEK_SET);
    if (length < 0 || restored < 0) { native_error = ERR_FILE_CANT_READ; return 0; }
    return static_cast<uint64_t>(length);
}

bool FileAccessPS5::eof_reached() const {
    return kernel_backed() ? native_eof : FileAccessUnix::eof_reached();
}

uint64_t FileAccessPS5::get_buffer(uint8_t *dst, uint64_t length) const {
    if (!kernel_backed()) return FileAccessUnix::get_buffer(dst, length);
    if (!dst && length) { native_error = ERR_INVALID_PARAMETER; return 0; }
    uint64_t done = 0;
    while (done < length) {
        constexpr uint64_t chunk = 1024 * 1024;
        const size_t count = static_cast<size_t>((length - done) < chunk ? length - done : chunk);
        const long n = sceKernelRead(native_fd, dst + done, count);
        if (n <= 0 || static_cast<uint64_t>(n) > count) {
            if (n == 0) { native_eof = true; native_error = ERR_FILE_EOF; }
            else native_error = ERR_FILE_CANT_READ;
            break;
        }
        done += static_cast<uint64_t>(n);
    }
    return done;
}

Error FileAccessPS5::get_error() const {
    return kernel_backed() ? native_error : FileAccessUnix::get_error();
}

void FileAccessPS5::close() {
    if (native_fd >= 0) { sceKernelClose(native_fd); native_fd = -1; }
    FileAccessUnix::close();
    native_eof = false;
    native_error = OK;
}

bool FileAccessPS5::file_exists(const String &p_path) {
    const String path = fix_path(p_path);
    if (!native_mount(path)) return FileAccessUnix::file_exists(p_path);
    const int fd = open_native(path);
    if (fd < 0) return false;
    sceKernelClose(fd);
    return true;
}

int64_t FileAccessPS5::_get_size(const String &p_file) {
    const String path = fix_path(p_file);
    if (!native_mount(path)) return FileAccessUnix::_get_size(p_file);
    const int fd = open_native(path);
    if (fd < 0) return -1;
    const long long size = sceKernelLseek(fd, 0, SEEK_END);
    sceKernelClose(fd);
    return size;
}
