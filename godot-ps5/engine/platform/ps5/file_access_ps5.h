// SPDX-License-Identifier: MIT
#pragma once
#include "drivers/unix/file_access_unix.h"

// Read-only kernel-backed file access for PS5 sandbox mounts. Godot's upstream
// FileAccessUnix depends on libc fopen/fseeko which are not dependable on PS5.
// Writes and non-native host paths remain delegated to FileAccessUnix.
class FileAccessPS5 : public FileAccessUnix {
    GDSOFTCLASS(FileAccessPS5, FileAccessUnix);
    int native_fd = -1;
    String native_path;
    String original_path;
    mutable Error native_error = OK;
    mutable bool native_eof = false;
    bool kernel_backed() const { return native_fd >= 0; }
    static bool native_mount(const String &path);
    static int open_native(const String &path);

public:
    Error open_internal(const String &p_path, int p_mode_flags) override;
    bool is_open() const override;
    String get_path() const override;
    String get_path_absolute() const override;
    void seek(uint64_t p_position) override;
    void seek_end(int64_t p_position = 0) override;
    uint64_t get_position() const override;
    uint64_t get_length() const override;
    bool eof_reached() const override;
    uint64_t get_buffer(uint8_t *p_dst, uint64_t p_length) const override;
    Error get_error() const override;
    void close() override;
    bool file_exists(const String &p_path) override;
    int64_t _get_size(const String &p_file) override;
    ~FileAccessPS5() override { close(); }
};
