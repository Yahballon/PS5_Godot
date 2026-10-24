// SPDX-License-Identifier: MIT
#include <cstdio>
#include <sys/stat.h>
#define GODOT_PS5_NATIVE_IO 1
#include "pck_launch_config.hpp"
extern "C" int godot_ps5_run_pack(const char *);
static void log_message(const char *message) {
    if (FILE *f = fopen("/data/GodotPS5/engine-smoke.log","ab")) {
        fprintf(f, "[GodotPS5 engine] %s\n", message);
        fclose(f);
    }
}
// PS5 CRT's catchReturnFromMain is intentionally a weak hook. Its default
// returns and then calls libc exit(status), causing SIGSYS on real PS5 titles.
// Request that the PS5 shell close this homebrew instead, then wait for it.
extern "C" int sceSystemServiceLoadExec(const char *path, const char *const *argv);
extern "C" int sceKernelUsleep(unsigned int microseconds);
extern "C" void catchReturnFromMain(int status) {
    char message[96]{};
    std::snprintf(message, sizeof(message), "SHELL_EXIT_REQUEST v0.3.2 status=%d", status);
    log_message(message);
    std::fflush(nullptr);
    (void)sceSystemServiceLoadExec("exit", nullptr);
    for (;;) {
        (void)sceKernelUsleep(100000);
    }
}
int main() {
    mkdir("/data/GodotPS5",0755);
    log_message("MAIN_ENTER_BEFORE_REDIRECT v0.3.2");
    FILE *out=freopen("/data/GodotPS5/engine-stdout.log","ab",stdout);
    FILE *err=freopen("/data/GodotPS5/engine-stderr.log","ab",stderr);
    if(out) setvbuf(stdout,nullptr,_IONBF,0);
    if(err) setvbuf(stderr,nullptr,_IONBF,0);
    log_message("NATIVE_GODOT_ENTRY_START v0.3.2 ENGINE_PHASE_TRACE");
    // External Godot 4 project packs take priority over the bundled smoke
    // fixture. The PS5 kernel screens config and USB paths before launching.
    const godot_ps5::PackSelection selected = godot_ps5::select_runtime_pack();
    char chosen[1100]{};
    std::snprintf(chosen,sizeof(chosen),"PACK_SOURCE=%s PACK=%s",
                  godot_ps5::pack_source_name(selected.source),selected.path.c_str());
    log_message(chosen);
    if (selected.path.empty()) {
        log_message("NO_VALID_GODOT4_PACK");
        return 2;
    }
    log_message("ENGINE_BASE=GODOT_4_7_2_HEADLESS");
    const int result=godot_ps5_run_pack(selected.path.c_str());
    char msg[96]{};
    snprintf(msg,sizeof(msg),"NATIVE_GODOT_RETURN=%d",result);
    log_message(msg);
    return result;
}
