// SPDX-License-Identifier: MIT
// Link this static-engine entry point from a genuine PS5-DevBridge launcher.
#include "os_ps5.h"
#include "pck_locator.hpp"
#include "core/profiling/profiling.h"
#include "main/main.h"
#include <cstdio>
#include <cstdlib>
#include <string>
#ifdef GODOT_PS5_NATIVE_GLES3
#include <fcntl.h>
extern "C" int sceKernelOpen(const char *, int, int);
extern "C" long sceKernelRead(int, void *, size_t);
extern "C" int sceKernelClose(int);
// Optional controlled A/B only. Normal users retain native AudioOut.
// Exact file content "dummy" switches to Godot's built-in Dummy driver.
static bool m18_dummy_audio_requested() {
    const int fd=sceKernelOpen("/data/GodotPS5/m18_audio_mode.txt",O_RDONLY|O_NOFOLLOW,0);
    if(fd<0)return false;
    char buf[17]{};
    const long n=sceKernelRead(fd,buf,sizeof(buf));
    sceKernelClose(fd);
    if(n<=0 || n>=static_cast<long>(sizeof(buf)))return false;
    std::string value(buf,static_cast<size_t>(n));
    while(!value.empty() && (value.back()=='\n'||value.back()=='\\r'))value.pop_back();
    return value=="dummy";
}
#endif

extern "C" int godot_ps5_run_pack(const char *requested) {
    const std::string pack = godot_ps5::choose_pack(requested);
    if (pack.empty()) {
        std::fprintf(stderr, "[GodotPS5] No valid standalone Godot 4 pack found.\n");
        return EXIT_FAILURE;
    }
    std::fprintf(stderr, "[GodotPS5] Headless Godot startup: %s\n", pack.c_str());

    std::fprintf(stderr, "[GodotPS5 PHASE 0.2.11] BEFORE_PROFILER_INIT\n");
    std::fflush(stderr);
    godot_init_profiler();
    std::fprintf(stderr, "[GodotPS5 PHASE 0.2.11] AFTER_PROFILER_INIT\n");
    std::fflush(stderr);
    int result = EXIT_FAILURE;
    {
        std::fprintf(stderr, "[GodotPS5 PHASE 0.2.11] BEFORE_OS_PS5_CONSTRUCTOR\n");
        std::fflush(stderr);
        OS_PS5 os;
        std::fprintf(stderr, "[GodotPS5 PHASE 0.2.11] AFTER_OS_PS5_CONSTRUCTOR\n");
        std::fflush(stderr);
        char main_pack[] = "--main-pack";
#ifdef GODOT_PS5_NATIVE_GLES3
        // IMPORTANT: Don't pass --headless; it would bypass DisplayServerPS5.
        // The engine must construct the *real* GLES3 renderer from this
        // display driver's EGL context, not our old native preview path.
        char display_opt[] = "--display-driver";
        char display_name[] = "ps5";
        char driver_opt[] = "--rendering-driver";
        char driver_name[] = "opengl3";
        char method_opt[] = "--rendering-method";
        char method_name[] = "gl_compatibility";
        char audio_opt[] = "--audio-driver";
        char audio_driver_dummy[] = "Dummy";
        char *args[10] = {display_opt, display_name, driver_opt, driver_name,
                         method_opt, method_name, main_pack,
                         const_cast<char *>(pack.c_str())};
        constexpr int count = 8;
        int m18_count=count;
        const bool dummy_audio=m18_dummy_audio_requested();
        if(dummy_audio) {
            args[m18_count++]=audio_opt;
            args[m18_count++]=audio_driver_dummy;
        }
        std::printf("GODOT_PS5_M18_AUDIO_AB_MODE mode=%s\n",
            dummy_audio?"dummy":"native_audioout");
#else
        char headless[] = "--headless";
        char *args[] = {headless, main_pack, const_cast<char *>(pack.c_str())};
        constexpr int count = 3;
#endif

        std::fprintf(stderr, "[GodotPS5 PHASE 0.2.11] BEFORE_MAIN_SETUP\n");
        std::fflush(stderr);
        #ifdef GODOT_PS5_NATIVE_GLES3
        const Error err = Main::setup("godot.ps5", m18_count, args);
#else
        const Error err = Main::setup("godot.ps5", count, args);
#endif
        std::fprintf(stderr, "[GodotPS5 PHASE 0.2.11] AFTER_MAIN_SETUP status=%d\n", int(err));
        std::fflush(stderr);
        if (err == OK) {

            std::fprintf(stderr, "[GodotPS5 PHASE 0.2.11] BEFORE_MAIN_START\n");
            std::fflush(stderr);
            const int start_status = Main::start();
            std::fprintf(stderr, "[GodotPS5 PHASE 0.2.11] AFTER_MAIN_START status=%d\n", start_status);
            std::fflush(stderr);
            if (start_status == EXIT_SUCCESS) {
                std::fprintf(stderr, "[GodotPS5 PHASE 0.2.11] BEFORE_OS_RUN\n");
                std::fflush(stderr);
                os.run();
                result = os.get_exit_code();
            }
            Main::cleanup();
        } else {
            std::fprintf(stderr, "[GodotPS5] Engine setup error: %d\n", int(err));
        }
    }
    std::fprintf(stderr, "[GodotPS5 PHASE 0.2.11] BEFORE_PROFILER_CLEANUP\n");
    std::fflush(stderr);
    godot_cleanup_profiler();
    return result;
}
