#include "../engine/platform/ps5/pck_locator.hpp"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <string>
#include <unistd.h>

int main() {
    char pattern[]="/tmp/godotps5-XXXXXX";
    const char *dir=mkdtemp(pattern);
    assert(dir);
    const std::string base(dir);
    const auto one=base+"/a.pck",two=base+"/b.PCK";
    const auto bad=base+"/c.pck",future=base+"/newer.pck";
    const unsigned char header[]={'G','D','P','C',4,0,0,0,4,0,0,0,7,0,0,0,2,0,0,0};
    auto save=[](const std::string &name,const unsigned char *data,size_t count) {
        FILE *f=fopen(name.c_str(),"wb"); assert(f);
        assert(fwrite(data,1,count,f)==count); fclose(f);
    };
    save(two,header,sizeof(header));save(one,header,sizeof(header));
    unsigned char corrupt[sizeof(header)];memcpy(corrupt,header,sizeof(header));
    corrupt[8]=3;save(bad,corrupt,sizeof(corrupt));
    corrupt[8]=4;corrupt[12]=8;save(future,corrupt,sizeof(corrupt));
    assert(godot_ps5::pack_name("a.PCK"));
    assert(!godot_ps5::pack_name("a.pck.tmp"));
    assert(!godot_ps5::safe_filename("../foo.pck"));
    assert(!godot_ps5::safe_filename("foo\\bar.pck"));
    assert(godot_ps5::valid_godot4_pack(one));
    assert(!godot_ps5::valid_godot4_pack(bad));
    assert(!godot_ps5::valid_godot4_pack(future));
    assert(godot_ps5::first_pack_in(dir)==one);
    const std::string stale=base+"/smoke.PCK";
    save(stale,header,sizeof(header));
    assert(godot_ps5::is_legacy_smoke_pack("smoke.pck"));
    assert(godot_ps5::is_legacy_smoke_pack("SMOKE.PCK"));
    assert(!godot_ps5::is_legacy_smoke_pack("smoke2.pck"));
    assert(godot_ps5::first_pack_in(dir,true)==one);
    assert(godot_ps5::choose_pack(one.c_str())==one);
    assert(godot_ps5::choose_pack(bad.c_str()).empty());
    assert(godot_ps5::choose_pack("../a.pck").empty());
    const auto link=base+"/link.pck";
    assert(symlink(one.c_str(),link.c_str())==0);
    assert(!godot_ps5::valid_godot4_pack(link));
    unlink(link.c_str());unlink(one.c_str());unlink(two.c_str());
    assert(godot_ps5::first_pack_in(dir)==stale);
    assert(godot_ps5::first_pack_in(dir,true).empty());
    unlink(stale.c_str());
    unlink(bad.c_str());unlink(future.c_str());rmdir(dir);
    puts("PASS: Godot4 PCK host/native discovery and path screening");
}
