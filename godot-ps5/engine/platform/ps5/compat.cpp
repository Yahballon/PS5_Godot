// SPDX-License-Identifier: MIT
// Secure PS5/BSD entropy shim for the Godot 4 Unix runtime.
// No deterministic randomness fallback. Native kernel testing is still needed.
#include "compat.h"

#include <cerrno>
#include <sys/types.h>
#include <sys/sysctl.h>

extern "C" int getentropy(void *buffer, size_t count) {
    if (count > 256 || (count != 0 && buffer == nullptr)) {
        errno = EIO;
        return -1;
    }
    if (count == 0) return 0;
    int mib[2] = { CTL_KERN, KERN_ARND };
    size_t got = count;
    if (sysctl(mib, 2, buffer, &got, nullptr, 0) != 0 || got != count) {
        errno = EIO;
        return -1;
    }
    return 0;
}
