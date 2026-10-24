// SPDX-License-Identifier: MIT
#pragma once
// PS5 Mesa AGC exposes desktop OpenGL 4.6 Core Profile.
// Use upstream GLAD desktop GL, NOT the GLES2 loader: its optional
// gladLoaderLoadGLES2 symbol was undefined during native PS5 linking.
// The GLES3 renderer still runs its GL-over-GLES compatibility path.
#ifndef GL_API_ENABLED
#define GL_API_ENABLED
#endif
#include <thirdparty/glad/glad/gl.h>
