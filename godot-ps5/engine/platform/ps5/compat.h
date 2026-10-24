// SPDX-License-Identifier: MIT
#pragma once
// Godot's Unix core expects getentropy, while the jailbreak SDK's unistd
// headers may not declare it. Keep the declaration C/C++ compatible.
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
int getentropy(void *buffer, size_t count);
#ifdef __cplusplus
}
#endif
