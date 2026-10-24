// SPDX-License-Identifier: MIT
// First native Godot DisplayServerPS5 registration/ABI validation stage.
// This is NOT an EGL-enabled Godot renderer. GLES3 is deliberately disabled.
#include "display_server_ps5.h"

#include "core/error/error_macros.h"
#include "core/os/memory.h"
#include "servers/rendering/dummy/rasterizer_dummy.h"
#ifdef GODOT_PS5_NATIVE_GLES3
#include "drivers/gles3/rasterizer_gles3.h"
#include "graphics_hooks_ps5.h"
#include <platform_egl.h>
#include <cstdio>
static GodotPS5GraphicsHooks ps5_graphics = {};
bool DisplayServerPS5::context_ready = false;
extern "C" void godot_ps5_set_graphics_hooks(const GodotPS5GraphicsHooks *hooks) {
    ps5_graphics = hooks ? *hooks : GodotPS5GraphicsHooks{};
}
#endif

Vector<String> DisplayServerPS5::get_rendering_drivers_func() {
    Vector<String> drivers;
#ifdef GODOT_PS5_NATIVE_GLES3
    drivers.push_back("opengl3");
#else
    drivers.push_back("dummy");
#endif
    return drivers;
}

DisplayServer *DisplayServerPS5::create_func(
        const String &p_rendering_driver,
        DisplayServerEnums::WindowMode p_mode,
        DisplayServerEnums::VSyncMode p_vsync_mode,
        uint32_t p_flags,
        const Vector2i *p_position,
        const Vector2i &p_resolution,
        int p_screen,
        DisplayServerEnums::Context p_context,
        int64_t p_parent_window,
        Error &r_error) {
#ifdef GODOT_PS5_NATIVE_GLES3
    if (p_rendering_driver != "opengl3") {
        r_error = ERR_UNAVAILABLE;
        ERR_PRINT("PS5 GLES3: only opengl3 is supported by this display backend.");
        return nullptr;
    }
    if (!ps5_graphics.open || !ps5_graphics.swap ||
            !ps5_graphics.close || !ps5_graphics.get_gl_proc) {
        r_error = ERR_UNAVAILABLE;
        ERR_PRINT("[GodotPS5 GLES3] EGL_HOOKS_MISSING");
        return nullptr;
    }
    if (!ps5_graphics.open(1920, 1080)) {
        r_error = ERR_CANT_CREATE;
        ERR_PRINT("[GodotPS5 GLES3] EGL_OPEN_FAILED");
        return nullptr;
    }
    // Godot's GLES3 rasterizer uses GLAD. Loading the EGL proc resolver
    // from the live PS5 EGL implementation is required *before* Godot
    // constructs RasterizerGLES3. No competing GL context is created here.
    glad_eglGetProcAddress = reinterpret_cast<PFNEGLGETPROCADDRESSPROC>(
            ps5_graphics.get_gl_proc);
    context_ready = true;
    RasterizerGLES3::make_current(true); // Mesa PS5 AGC: OpenGL 4.6 Core
    std::fprintf(stderr, "[GodotPS5 GLES3] DISPLAY_SERVER_PS5_EGL_READY\n");
    r_error = OK;
    return memnew(DisplayServerPS5);
#else
    // Existing headless ABI gate: never pretend that GLES3 works.
    if (!p_rendering_driver.is_empty() && p_rendering_driver != "dummy") {
        r_error = ERR_UNAVAILABLE;
        ERR_PRINT("PS5 DisplayServer: EGL/GLES3 not wired; refusing non-dummy renderer.");
        return nullptr;
    }
    r_error = OK;
    RasterizerDummy::make_current();
    print_line("[GodotPS5] DISPLAY_SERVER_PS5_DUMMY_REGISTERED_NO_VIDEO");
    return memnew(DisplayServerPS5);
#endif
}

Vector<DisplayServerEnums::WindowID> DisplayServerPS5::get_window_list() const {
    Vector<DisplayServerEnums::WindowID> windows;
    windows.push_back(DisplayServerEnums::MAIN_WINDOW_ID);
    return windows;
}

void DisplayServerPS5::register_ps5_driver() {
    DisplayServer::register_create_function("ps5", create_func, get_rendering_drivers_func);
}

#ifdef GODOT_PS5_NATIVE_GLES3
void DisplayServerPS5::swap_buffers() {
    if (!context_ready || !ps5_graphics.swap) {
        return;
    }
    if (!ps5_graphics.swap()) {
        ERR_PRINT("[GodotPS5 GLES3] EGL_SWAP_FAILED");
        context_ready = false;
    }
}
DisplayServerPS5::~DisplayServerPS5() {
    // Godot's Main::cleanup() releases its RenderingServer before the
    // DisplayServer. The GL context must remain alive until then.
    if (ps5_graphics.close) ps5_graphics.close();
    context_ready = false;
    std::fprintf(stderr, "[GodotPS5 GLES3] EGL_CONTEXT_CLOSED\n");
}
#endif
