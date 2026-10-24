// SPDX-License-Identifier: MIT
#include "../engine/platform/ps5/pck_launch_config.hpp"
#include <cassert>
#include <iostream>
#include <string>
int main() {
    using namespace godot_ps5;
    assert(parse_launch_txt("Game.pck\n") == "/data/GodotPS5/games/Game.pck");
    assert(parse_launch_txt("  Game.pck  \r\n") == "/data/GodotPS5/games/Game.pck");
    assert(parse_launch_txt("\xEF\xBB\xBF/mnt/usb0/godot/My Game.PCK\r\n") ==
           "/mnt/usb0/godot/My Game.PCK");
    assert(parse_launch_txt("# no launch config") == "");
    assert(parse_launch_txt("   \t  ") == "");
    for (const char *s : {
            "../evil.pck", "/tmp/evil.pck", "/app0/evil.pck",
            "/data/GodotPS5/games/../evil.pck",
            "/data/GodotPS5/games/./evil.pck",
            "/data/GodotPS5/games//evil.pck",
            "/data/GodotPS5/private/evil.pck",
            "/mnt/usb0/godot2/evil.pck",
            "/mnt/usb0/godot/g.pck\\backslash.pck",
            "/mnt/usb0/godot/g.mp4",
            "/mnt/usb0/godot/.hidden.pck"
            }) {
        assert(parse_launch_txt(s).empty());
    }
    assert(parse_launch_txt(std::string(1025,'a')).empty());
    assert(trusted_external_path("/mnt/usb3/godot/My Game.PCK"));
    assert(trusted_external_path("/data/GodotPS5/games/my-game..pck"));
    assert(!trusted_external_path("/mnt/usb2/godot/../spoof.pck"));
    assert(!trusted_external_path("/mnt/usb1/godot/evil\\b.pck"));
    assert(std::string(pack_source_name(PackSource::AutoScan)) == "AUTOSCAN");
    std::cout << "PASS: safe Godot PS5 external pack config parsing\n";
}
