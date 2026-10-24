// SPDX-License-Identifier: MIT
// Godot PS5 v0.1.0 – native PS5 hardware diagnostic, NOT A GODOT GAME PLAYER.
#define GODOT_PS5_NATIVE_IO 1
#include "pck_locator.hpp"
#include "gfx/renderer.hpp"
#include "platform/ps5/display_egl.hpp"
#include "platform/ps5/pad.hpp"
#include "platform/ps5/system.hpp"
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <string>
#include <sys/stat.h>
#include <vector>

namespace {
using namespace hui::gfx;
constexpr const char *kRoot = "/data/GodotPS5";
constexpr const char *kLog = "/data/GodotPS5/probe.log";
const Color mint = Color::rgb(0x79edc4);
const Color white = Color::rgb(0xeef5fc);
const Color subdued = Color::rgb(0x9bb3c5);
const Color amber = Color::rgb(0xffd37c);
struct Found { std::string name; std::string path; };
std::string status = "STARTING";
std::vector<Found> found;

void log_line(const std::string &message) {
    mkdir(kRoot, 0755);
    if (FILE *f = fopen(kLog, "ab")) {
        fprintf(f, "[GodotPS5 Probe 0.1.0] %s\n", message.c_str());
        fclose(f);
    }
}
std::string read_font() {
    const char* paths[]={"/app0/assets/fonts/inter-semibold.huifont",
                          "/data/homebrew/PPSA99842/assets/fonts/inter-semibold.huifont"};
    for (const char *path : paths) {
        FILE *f = fopen(path, "rb");
        if (!f) continue;
        if (fseek(f, 0, SEEK_END)) { fclose(f); continue; }
        const long length=ftell(f);
        if (length < 1 || length > 16000000) { fclose(f); continue; }
        rewind(f);
        std::string content(static_cast<size_t>(length), '\0');
        const size_t n=fread(content.data(), 1, content.size(), f);
        fclose(f);
        if (n == content.size()) return content;
    }
    return {};
}
std::string basename(const std::string &path) {
    const size_t slash=path.rfind('/');
    return slash==std::string::npos?path:path.substr(slash+1);
}
std::string short_path(std::string path, size_t limit=73) {
    if(path.size() > limit) path=path.substr(0,limit-3)+"...";
    return path;
}
void scan_pcks() {
    found.clear();
    const char *roots[] = {"/data/GodotPS5/games", "/mnt/usb0/godot",
                           "/mnt/usb1/godot", "/mnt/usb0/GodotPS5/games"};
    for (const char *root : roots) {
        std::string p=godot_ps5::first_pack_in(root);
        if (!p.empty()) {
            found.push_back({basename(p),p});
            log_line("FOUND_PCK "+p);
        } else {
            log_line(std::string("NO_VALID_PCK ")+root);
        }
    }
    status = found.empty() ? "No compatible Godot 4 PCK found" :
            std::to_string(found.size())+" directories with compatible PCKs";
    log_line(status);
}
void text_line(DrawList &ui, Font &font, unsigned atlas,
               const std::string &s, float x, float y, float size,
               Color color=white, Align align=Align::left) {
    ui.text(font, atlas, s, x, y, size, color, align);
}
void panel(DrawList &ui, float x,float y,float w,float h,bool active=false) {
    ui.bordered_rect({x,y,w,h},18,Color::rgb(active?0x16493f:0x12263a),
                     active?3:1,Color::rgb(active?0x7af5cc:0x2e5064));
}
} // namespace

int main() {
    log_line("BOOT native PS5 PCK hardware diagnostic");
    log_line("GODOT_ENGINE_LINKED=NO");
    log_line("SCAN_BACKEND=PS5_LIBKERNEL_GETDENTS");
    scan_pcks();

    hui::ps5::Display display;
    if (!display.open()) { log_line("DISPLAY_OPEN_FAILED"); hui::sys::park(); }
    Renderer renderer;
    if (!renderer.init()) { log_line("RENDERER_INIT_FAILED"); hui::sys::park(); }
    Font font;
    if (!font.load(read_font())) { log_line("FONT_LOAD_FAILED"); hui::sys::park(); }
    const unsigned atlas=renderer.batch().create_font_texture(font);
    hui::ps5::Pad pad;
    pad.open();
    size_t selected=0;
    uint32_t previous=0;

    for (;;) {
        std::array<hui::PadSample,64> samples {};
        uint32_t pressed=0,held=0;
        const size_t n=pad.read(samples);
        bool connected=false;
        for(size_t i=0;i<n;i++) {
            if (!samples[i].connected) continue;
            connected=true;
            uint32_t buttons=samples[i].buttons;
            if(samples[i].left_y < 65) buttons |= hui::pad_bits::kUp;
            if(samples[i].left_y > 190) buttons |= hui::pad_bits::kDown;
            pressed |= buttons & ~previous;
            previous=buttons;
            held=buttons;
        }
        if (!connected) previous=0;
        (void)held;
        if((pressed & hui::pad_bits::kUp) && selected>0) --selected;
        if((pressed & hui::pad_bits::kDown) && selected+1<found.size()) ++selected;
        if(pressed & hui::pad_bits::kSquare) {
            log_line("RESCAN");
            scan_pcks();
            selected=0;
        }
        if((pressed & hui::pad_bits::kCross) && !found.empty()) {
            const auto &p=found[selected].path;
            const bool valid=godot_ps5::valid_godot4_pack(p);
            status=valid ? "PCK HEADER READ OK - engine not linked" : "PCK header read failed";
            log_line(std::string(valid?"PCK_READ_OK ":"PCK_READ_FAILED ")+p);
        }
        if(pressed & hui::pad_bits::kCircle) {
            log_line("EXIT");
            pad.close();
            renderer.release();
            display.close();
            hui::sys::quit();
        }

        DrawList ui;
        ui.gradient_rect({0,0,1920,1080},0,Color::rgb(0x061021),Color::rgb(0x0c2831));
        ui.line(70,185,1850,185,2,Color::rgb(0x31657b));
        text_line(ui,font,atlas,"GODOT PS5",84,118,72,white);
        text_line(ui,font,atlas,"HOMEBREW ENGINE / HARDWARE PROBE",90,159,23,mint);
        text_line(ui,font,atlas,"v0.1.0  |  by YAHBALLON",1830,117,22,subdued,Align::right);
        panel(ui,78,235,1083,665);
        panel(ui,1190,235,650,665);
        text_line(ui,font,atlas,"GODOT 4 PACKS",115,306,35,white);
        ui.line(115,329,1114,329,2,Color::rgb(0x2c5064));
        if(found.empty()) {
            text_line(ui,font,atlas,"No Godot 4 PCK found",133,415,31,amber);
            text_line(ui,font,atlas,"Try these folders:",133,486,25,subdued);
            text_line(ui,font,atlas,"/data/GodotPS5/games/",133,542,26,mint);
            text_line(ui,font,atlas,"/mnt/usb0/godot/",133,590,26,mint);
            text_line(ui,font,atlas,"Then press SQUARE to rescan",133,658,23,subdued);
        } else {
            for(size_t i=0;i<found.size() && i<7;i++) {
                const float y=355.0f+float(i)*75;
                panel(ui,122,y,1007,65,i==selected);
                text_line(ui,font,atlas,i==selected?">":"+",153,y+42,26,mint);
                text_line(ui,font,atlas,short_path(found[i].name,50),196,y+42,27,white);
                text_line(ui,font,atlas,short_path(found[i].path,47),1087,y+43,18,subdued,Align::right);
            }
        }
        text_line(ui,font,atlas,"PORT STATUS",1223,308,34,mint);
        text_line(ui,font,atlas,"Display: initialized",1225,385,23,white);
        text_line(ui,font,atlas,"Input: DualSense polling",1225,435,23,white);
        text_line(ui,font,atlas,"Storage: PS5 kernel getdents",1225,485,21,white);
        text_line(ui,font,atlas,"PCK: Godot 4 header detection",1225,535,21,white);
        text_line(ui,font,atlas,"Engine execution: NOT LINKED",1225,604,24,amber);
        text_line(ui,font,atlas,"No Godot game can run in v0.1.0",1225,647,20,amber);
        text_line(ui,font,atlas,"RESULT",1225,736,25,mint);
        text_line(ui,font,atlas,short_path(status,42),1225,779,21,white);
        text_line(ui,font,atlas,"Log: /data/GodotPS5/probe.log",1225,844,17,subdued);
        text_line(ui,font,atlas,"D-PAD: SELECT     X: VERIFY PCK     SQUARE: RESCAN     CIRCLE: EXIT",
                  960,1009,22,white,Align::center);
        renderer.begin();
        renderer.draw(ui);
        renderer.present(0,display.width(),display.height());
        display.swap();
        hui::sys::hide_splash_screen();
        hui::sys::sleep_us(16000);
    }
}
