// Native-free tests for DualSense protocol mapping and ABI.
#include "../engine/platform/ps5/pad_ps5.h"
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
using namespace ps5_pad;
int main() {
    static_assert(sizeof(RawReport) == 120);
    assert(kButtons[0].native_bit == 0x4000u && kButtons[0].godot_button == 0); // Cross
    bool found_up=false, found_touch=false, found_options=false;
    uint32_t used=0;
    for (const auto &x : kButtons) {
        assert(x.native_bit!=0 && (used & x.native_bit)==0);
        used|=x.native_bit;
        assert(x.godot_button>=0 && x.godot_button<128);
        if(x.native_bit==0x10u && x.godot_button==11)found_up=true;
        if(x.native_bit==0x100000u && x.godot_button==20)found_touch=true;
        if(x.native_bit==0x8u && x.godot_button==6)found_options=true;
    }
    assert(found_up && found_touch && found_options);
    assert(axis(128)==0.0f);
    assert(axis(127)==0.0f);
    assert(axis(0)==-1.0f);
    assert(axis(255)==1.0f);
    assert(std::fabs(axis(230)-0.8039f)<0.02f);
    assert(trigger(0)==0.0f && trigger(255)==1.0f);
    assert(trigger(127)>0.49f && trigger(127)<0.51f);
    std::cout << "PASS: DualSense PS5 button/axis map and 120-byte pad ABI\n";
}
