// SPDX-License-Identifier: GPL-3.0-or-later
// PPSA99845 — same-process GDScript-state → OpenGL presentation bridge.
// This is a diagnostic intermediary, NOT Godot's GLES3 or CanvasItem renderer.
// Godot's real SceneTree owns animation and DualSense input; native GL
// displays a procedural preview using its actual per-frame scene transforms.
#include "platform/ps5/display_egl.hpp"
#include "platform/ps5/system.hpp"
#include <GL/glcorearb.h>
#include <array>
#include <cstdio>
#include <cmath>
#include <sys/stat.h>
#include <cstdint>
#include <time.h>
#include "scene_frame_hooks_ps5.h"

extern "C" int godot_ps5_run_pack(const char *pack);

namespace {
constexpr char kLog[]="/data/GodotPS5/scene-bridge.log";
uint64_t monotonic_us() {
    struct timespec ts = {};
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) return 0;
    return uint64_t(ts.tv_sec) * 1000000ULL + uint64_t(ts.tv_nsec) / 1000ULL;
}
void log(const char *name,int value=-1) {
    if(FILE*f=std::fopen(kLog,"ab")){
        if(value>=0)std::fprintf(f,"[GodotPS5 BRIDGE 0.1.2] %s=%d\n",name,value);
        else std::fprintf(f,"[GodotPS5 BRIDGE 0.1.2] %s\n",name);
        std::fflush(f); std::fclose(f);
    }
}
GLuint compile(GLenum type,const char*source){
    GLuint shader=glCreateShader(type);
    if(!shader)return 0;
    glShaderSource(shader,1,&source,nullptr);
    glCompileShader(shader);
    GLint status=GL_FALSE;
    glGetShaderiv(shader,GL_COMPILE_STATUS,&status);
    if(status!=GL_TRUE){
        char buffer[1024]={};GLsizei size=0;
        glGetShaderInfoLog(shader,sizeof(buffer)-1,&size,buffer);
        if(FILE*f=std::fopen(kLog,"ab")){
            std::fprintf(f,"[GodotPS5 BRIDGE 0.1.2] SHADER_ERROR=%s\n",buffer);
            std::fclose(f);
        }
        glDeleteShader(shader);return 0;
    }
    return shader;
}
constexpr char kVertex[]=R"(#version 460 core
layout(location=0) in vec2 pos;
layout(location=1) in vec2 uv;
uniform vec2 spritePos;
uniform float angle;
out vec2 uvFrag;
void main() {
    float s=sin(angle), c=cos(angle);
    vec2 rotated=vec2(c*pos.x-s*pos.y,s*pos.x+c*pos.y);
    gl_Position=vec4(rotated+spritePos,0,1);
    uvFrag=uv;
}
)";
constexpr char kFragment[]=R"(#version 460 core
in vec2 uvFrag;
uniform sampler2D spriteTexture;
layout(location=0) out vec4 color;
void main() {color=texture(spriteTexture,uvFrag);}
)";
struct GLScene {
    hui::ps5::Display display;
    GLuint program=0,vao=0,vbo=0,texture=0;
    GLint position=-1,rotation=-1,sampler=-1;
    int frames=0, last_presses=-1;
    uint32_t max_pad_us=0, max_main_us=0, max_draw_us=0, max_swap_us=0;
    uint32_t pad_hitches=0, main_hitches=0, draw_hitches=0, swap_hitches=0;
    void profile_snapshot() {
        // One single append for each infrequent sample, not a file open
        // and flush on every Cross press. The latter can stall frame pacing.
        if (FILE *f=std::fopen(kLog,"ab")) {
            std::fprintf(f,
                "[GodotPS5 BRIDGE 0.1.2] PERF_SAMPLE_FRAMES=%d CROSS_COUNT=%d "
                "PAD_MAX_US=%u MAIN_MAX_US=%u DRAW_MAX_US=%u SWAP_MAX_US=%u "
                "PAD_HITCHES=%u MAIN_HITCHES=%u DRAW_HITCHES=%u SWAP_HITCHES=%u\n",
                frames,last_presses,max_pad_us,max_main_us,max_draw_us,max_swap_us,
                pad_hitches,main_hitches,draw_hitches,swap_hitches);
            std::fclose(f);
        }
    }
    bool ready=false;
    bool open(){
        if(!display.open(1920,1080)){log("EGL_OPEN_FAILED",display.last_error());return false;}
        log("EGL_OPEN_OK");
        GLuint vs=compile(GL_VERTEX_SHADER,kVertex),fs=compile(GL_FRAGMENT_SHADER,kFragment);
        if(!vs||!fs){log("GL_SHADER_FAILURE");if(vs)glDeleteShader(vs);if(fs)glDeleteShader(fs);return false;}
        program=glCreateProgram();
        glAttachShader(program,vs);glAttachShader(program,fs);glLinkProgram(program);
        glDeleteShader(vs);glDeleteShader(fs);
        GLint ok=0;glGetProgramiv(program,GL_LINK_STATUS,&ok);
        if(!ok){log("GL_PROGRAM_LINK_FAILED");return false;}
        position=glGetUniformLocation(program,"spritePos");
        rotation=glGetUniformLocation(program,"angle");
        sampler=glGetUniformLocation(program,"spriteTexture");
        if(position<0||rotation<0||sampler<0){log("GL_UNIFORM_FAILURE");return false;}
        constexpr int side=64;
        std::array<unsigned char,side*side*4> pixels{};
        for(int y=0;y<side;++y)for(int x=0;x<side;++x){
            const int off=(y*side+x)*4;
            const bool on=((x/8+y/8)&1)==0;
            pixels[off]=on?255:10;
            pixels[off+1]=on?35:235;
            pixels[off+2]=on?160:255;
            pixels[off+3]=180;
        }
        glGenTextures(1,&texture);
        glBindTexture(GL_TEXTURE_2D,texture);
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA8,side,side,0,GL_RGBA,GL_UNSIGNED_BYTE,pixels.data());
        glBindTexture(GL_TEXTURE_2D,0);
        constexpr GLfloat quad[]={
            -0.28f,-0.50f,0,0,
             0.28f,-0.50f,1,0,
            -0.28f, 0.50f,0,1,
             0.28f, 0.50f,1,1
        };
        glGenVertexArrays(1,&vao);
        glBindVertexArray(vao);
        glGenBuffers(1,&vbo);
        glBindBuffer(GL_ARRAY_BUFFER,vbo);
        glBufferData(GL_ARRAY_BUFFER,sizeof(quad),quad,GL_STATIC_DRAW);
        glEnableVertexAttribArray(0);
        glVertexAttribPointer(0,2,GL_FLOAT,GL_FALSE,4*sizeof(GLfloat),(const void*)0);
        glEnableVertexAttribArray(1);
        glVertexAttribPointer(1,2,GL_FLOAT,GL_FALSE,4*sizeof(GLfloat),(const void*)(2*sizeof(GLfloat)));
        glBindVertexArray(0);
        if(glGetError()!=GL_NO_ERROR){log("GL_SETUP_ERROR");return false;}
        ready=true;log("SCENE_BRIDGE_GL_READY");
        return true;
    }
    // Present a visible fallback *before* Godot loads the PCK.
    // This separates GPU failure from startup/_ready hangs and
    // prevents a black screen during synchronous GDScript initialization.
    bool boot_frame() {
        if (!ready) return false;
        glViewport(0, 0, display.width(), display.height());
        glClearColor(0.05f, 0.18f, 0.40f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);
        const GLenum err=glGetError();
        log("BOOT_FRAME_GL_ERROR",static_cast<int>(err));
        if (err!=GL_NO_ERROR || !display.swap()) {
            log("BOOT_FRAME_SWAP_FAILED");
            return false;
        }
        hui::sys::hide_splash_screen();
        log("BOOT_FRAME_PRESENTED");
        return true;
    }
    void frame(float sprite_x,float angle,int presses,
               uint32_t main_loop_us,uint32_t pad_poll_us){
        if(!ready)return;
        // Track Cross in memory. No synchronous filesystem write on button
        // input; on the previous build that I/O coincided with user hitches.
        last_presses=presses;
        if(main_loop_us>max_main_us)max_main_us=main_loop_us;
        if(pad_poll_us>max_pad_us)max_pad_us=pad_poll_us;
        if(main_loop_us>33000)++main_hitches;
        if(pad_poll_us>33000)++pad_hitches;
        const uint64_t draw_begin_us=monotonic_us();
        // Count is read directly from a live Godot GDScript scene property;
        // NO independent native pad polling or second animation clock.
        const bool red=(presses&1)!=0;
        glViewport(0,0,display.width(),display.height());
        glClearColor(red?0.18f:0.06f,red?0.07f:0.10f,red?0.08f:0.18f,1);
        glClear(GL_COLOR_BUFFER_BIT);
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
        glUseProgram(program);
        glUniform2f(position,(sprite_x-960.0f)/960.0f,0.0f);
        glUniform1f(rotation,angle);
        glUniform1i(sampler,0);
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D,texture);
        glBindVertexArray(vao);
        glDrawArrays(GL_TRIANGLE_STRIP,0,4);
        glBindVertexArray(0);
        glBindTexture(GL_TEXTURE_2D,0);
        glUseProgram(0);
        glDisable(GL_BLEND);
        if(frames==0){
            log("GODOT_GDSCRIPT_SCENE_FRAME_DRAWN");
            log("FIRST_DRAW_GL_ERROR",(int)glGetError());
        }
        const uint64_t draw_end_us=monotonic_us();
        if (draw_begin_us && draw_end_us>=draw_begin_us) {
            const uint64_t elapsed=draw_end_us-draw_begin_us;
            const uint32_t us=static_cast<uint32_t>(elapsed>10000000?10000000:elapsed);
            if(us>max_draw_us)max_draw_us=us;
            if(us>33000)++draw_hitches;
        }
        const uint64_t swap_begin_us=monotonic_us();
        if(!display.swap()){log("EGL_SWAP_FAILED",display.last_error());ready=false;return;}
        const uint64_t swap_end_us=monotonic_us();
        if(swap_begin_us&&swap_end_us>=swap_begin_us){
            const uint64_t elapsed=swap_end_us-swap_begin_us;
            const uint32_t us=static_cast<uint32_t>(elapsed>10000000?10000000:elapsed);
            if(us>max_swap_us)max_swap_us=us;
            if(us>33000)++swap_hitches;
        }
        ++frames;
        if(frames==1){log("FIRST_FRAME_PRESENTED");hui::sys::hide_splash_screen();}
        if(frames==60||frames==600)log("PRESENTED_FRAME_COUNT",frames);
        if(frames==240||frames==600)profile_snapshot();
    }
    void close(){
        profile_snapshot();
        log("GDSCRIPT_CROSS_COUNT",last_presses);
        log("TOTAL_PRESENTED",frames);
        if(vbo)glDeleteBuffers(1,&vbo);
        if(vao)glDeleteVertexArrays(1,&vao);
        if(texture)glDeleteTextures(1,&texture);
        if(program)glDeleteProgram(program);
        display.close();
        log("GPU_SHUTDOWN");
    }
};
GLScene* active=nullptr;
void scene_callback(float x,float rotation,int count,
                    uint32_t main_loop_us,uint32_t pad_poll_us){
    if(active)active->frame(x,rotation,count,main_loop_us,pad_poll_us);
}
} // namespace
int main(){
    mkdir("/data/GodotPS5",0755);
    log("BOOT_SCENE_BRIDGE");
    FILE *out=freopen("/data/GodotPS5/bridge-stdout.log","ab",stdout);
    FILE *err=freopen("/data/GodotPS5/bridge-stderr.log","ab",stderr);
    if(out)setvbuf(stdout,nullptr,_IONBF,0);
    if(err)setvbuf(stderr,nullptr,_IONBF,0);
    GLScene scene;
    if(!scene.open()){log("GPU_INIT_FAILED");scene.close();hui::sys::quit();}
    if (!scene.boot_frame()) { log("GPU_BOOT_FRAME_FAILED"); scene.close(); hui::sys::quit(); }
    active=&scene;
    godot_ps5_set_scene_frame_callback(scene_callback);
    log("GODOT_ENGINE_ENTER");
    const int result=godot_ps5_run_pack("/app0/assets/godot/visual-smoke.pck");
    log("GODOT_ENGINE_RETURN",result);
    godot_ps5_set_scene_frame_callback(nullptr);
    active=nullptr;
    scene.close();
    log("NORMAL_SHUTDOWN");
    hui::sys::quit();
}
