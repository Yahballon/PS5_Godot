// SPDX-License-Identifier: GPL-3.0-or-later
// PS5 OpenGL/EGL graphics shader + geometry acceptance probe.
// Separate GPL test; NOT a Godot DisplayServer or a shipped Godot renderer.
#include "platform/ps5/display_egl.hpp"
#include "platform/ps5/pad.hpp"
#include "platform/ps5/system.hpp"
#include "core/input.hpp"
#include <EGL/egl.h>
#include <GL/glcorearb.h>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cmath>
#include <sys/stat.h>

namespace {
constexpr char kLog[] = "/data/GodotPS5/graphics-probe.log";
constexpr char kPrefix[] = "[GodotPS5 GPU shader] ";

void record(const char *event, int value = -1) {
    if (FILE *out = std::fopen(kLog, "ab")) {
        if (value >= 0) std::fprintf(out, "%s%s=%d\n", kPrefix, event, value);
        else std::fprintf(out, "%s%s\n", kPrefix, event);
        std::fflush(out);
        std::fclose(out);
    }
}
void log_string(const char *tag, const GLubyte *value) {
    if (FILE *out = std::fopen(kLog, "ab")) {
        std::fprintf(out, "%s%s=%s\n", kPrefix, tag,
            value ? reinterpret_cast<const char *>(value) : "(null)");
        std::fclose(out);
    }
}
void log_shader_failure(GLuint obj, bool link) {
    GLint length = 0;
    if (link) glGetProgramiv(obj, GL_INFO_LOG_LENGTH, &length);
    else glGetShaderiv(obj, GL_INFO_LOG_LENGTH, &length);
    if (length < 1) return;
    // Bound log size to prevent overflow or oversized console diagnostics.
    char log[2048] = {};
    GLsizei written = 0;
    if (link) glGetProgramInfoLog(obj, sizeof(log) - 1, &written, log);
    else glGetShaderInfoLog(obj, sizeof(log) - 1, &written, log);
    (void)length;
    if (FILE *out = std::fopen(kLog, "ab")) {
        std::fprintf(out, "%s%s: %s\n", kPrefix, link ? "LINK_LOG" : "SHADER_LOG", log);
        std::fclose(out);
    }
}
const char *kVertexShader = R"(#version 460 core
layout(location = 0) in vec2 position;
layout(location = 1) in vec3 color;
uniform float rotation;
out vec3 vertColor;
void main() {
    float c = cos(rotation);
    float s = sin(rotation);
    vec2 pos = vec2(c * position.x - s * position.y,
                    s * position.x + c * position.y);
    gl_Position = vec4(pos, 0.0, 1.0);
    vertColor = color;
}
)";
const char *kFragmentShader = R"(#version 460 core
in vec3 vertColor;
layout(location = 0) out vec4 fragColor;
void main() {
    fragColor = vec4(vertColor, 1.0);
}
)";
// Layout: (x, y, r, g, b); three different corner colors prove interpolation.
constexpr GLfloat kVertices[] = {
    -0.66f, -0.52f, 1.0f, 0.83f, 0.11f,
     0.66f, -0.52f, 0.08f, 1.0f, 0.34f,
     0.00f,  0.70f, 0.34f, 0.38f, 1.0f
};
struct Geometry {
    GLuint program = 0;
    GLuint vao = 0;
    GLuint vbo = 0;
    GLint rotation = -1;
    bool ready = false;

    static GLuint compile(GLenum type, const char *source) {
        GLuint shader = glCreateShader(type);
        if (!shader) { record("SHADER_CREATE_FAILED"); return 0; }
        glShaderSource(shader, 1, &source, nullptr);
        glCompileShader(shader);
        GLint ok = GL_FALSE;
        glGetShaderiv(shader, GL_COMPILE_STATUS, &ok);
        if (ok != GL_TRUE) {
            record(type == GL_VERTEX_SHADER ? "VERTEX_COMPILE_FAILED" : "FRAGMENT_COMPILE_FAILED");
            log_shader_failure(shader, false);
            glDeleteShader(shader);
            return 0;
        }
        record(type == GL_VERTEX_SHADER ? "VERTEX_COMPILE_OK" : "FRAGMENT_COMPILE_OK");
        return shader;
    }

    bool init() {
        const GLuint vs = compile(GL_VERTEX_SHADER, kVertexShader);
        if (!vs) return false;
        const GLuint fs = compile(GL_FRAGMENT_SHADER, kFragmentShader);
        if (!fs) { glDeleteShader(vs); return false; }
        program = glCreateProgram();
        if (!program) { record("PROGRAM_CREATE_FAILED"); glDeleteShader(fs); glDeleteShader(vs); return false; }
        glAttachShader(program, vs);
        glAttachShader(program, fs);
        glLinkProgram(program);
        glDeleteShader(vs);
        glDeleteShader(fs);
        GLint linked = GL_FALSE;
        glGetProgramiv(program, GL_LINK_STATUS, &linked);
        if (linked != GL_TRUE) {
            record("PROGRAM_LINK_FAILED");
            log_shader_failure(program, true);
            release();
            return false;
        }
        record("PROGRAM_LINK_OK");
        rotation = glGetUniformLocation(program, "rotation");
        if (rotation < 0) { record("ROTATION_UNIFORM_FAILED"); release(); return false; }
        glGenVertexArrays(1, &vao);
        glBindVertexArray(vao);
        glGenBuffers(1, &vbo);
        glBindBuffer(GL_ARRAY_BUFFER, vbo);
        glBufferData(GL_ARRAY_BUFFER, sizeof(kVertices), kVertices, GL_STATIC_DRAW);
        glEnableVertexAttribArray(0);
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), reinterpret_cast<void *>(0));
        glEnableVertexAttribArray(1);
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), reinterpret_cast<void *>(2 * sizeof(GLfloat)));
        glBindVertexArray(0);
        glBindBuffer(GL_ARRAY_BUFFER, 0);
        const GLenum error = glGetError();
        if (!vao || !vbo || error != GL_NO_ERROR) {
            record("GL_RESOURCE_ERROR", static_cast<int>(error));
            release();
            return false;
        }
        ready = true;
        record("GL_GEOMETRY_READY");
        return true;
    }

    void draw(int frame) {
        glUseProgram(program);
        glUniform1f(rotation, static_cast<float>(frame) * 0.015f);
        glBindVertexArray(vao);
        glDrawArrays(GL_TRIANGLES, 0, 3);
        glBindVertexArray(0);
        glUseProgram(0);
    }

    void release() {
        if (vbo) { glDeleteBuffers(1, &vbo); vbo = 0; }
        if (vao) { glDeleteVertexArrays(1, &vao); vao = 0; }
        if (program) { glDeleteProgram(program); program = 0; }
        ready = false;
    }
};

// Second, independent shader program: deliberately exercises the Godot 2D
// compatibility prerequisites (RGBA8 texture upload, UV interpolation,
// alpha blending, and animated textured quads) on real PS5 AGC hardware.
// This is NOT Godot's RenderingServer/DisplayServer.
struct Texture2DProbe {
    GLuint program = 0;
    GLuint vao = 0;
    GLuint vbo = 0;
    GLuint texture = 0;
    GLint wobble_uniform = -1;
    GLint sampler_uniform = -1;
    bool ready = false;

    static constexpr const char *vertex_source = R"(#version 460 core
layout(location = 0) in vec2 position;
layout(location = 1) in vec2 uv;
out vec2 pixel_uv;
uniform float wobble;
void main() {
    vec2 displacement = vec2(0.17 * sin(wobble), 0.08 * cos(wobble * 0.7));
    gl_Position = vec4(position + displacement, 0.0, 1.0);
    pixel_uv = uv;
}
)";
    static constexpr const char *fragment_source = R"(#version 460 core
in vec2 pixel_uv;
layout(location = 0) out vec4 fragColor;
uniform sampler2D sprite_tex;
void main() {
    fragColor = texture(sprite_tex, pixel_uv);
}
)";

    bool init() {
        const GLuint vs = Geometry::compile(GL_VERTEX_SHADER, vertex_source);
        if (!vs) { record("SPRITE_VERTEX_COMPILE_FAILED"); return false; }
        const GLuint fs = Geometry::compile(GL_FRAGMENT_SHADER, fragment_source);
        if (!fs) { record("SPRITE_FRAGMENT_COMPILE_FAILED"); glDeleteShader(vs); return false; }
        program = glCreateProgram();
        if (!program) { record("SPRITE_PROGRAM_CREATE_FAILED"); glDeleteShader(fs); glDeleteShader(vs); return false; }
        glAttachShader(program, vs);
        glAttachShader(program, fs);
        glLinkProgram(program);
        glDeleteShader(vs);
        glDeleteShader(fs);
        GLint ok = GL_FALSE;
        glGetProgramiv(program, GL_LINK_STATUS, &ok);
        if (ok != GL_TRUE) {
            record("SPRITE_PROGRAM_LINK_FAILED");
            log_shader_failure(program, true);
            release();
            return false;
        }
        record("SPRITE_PROGRAM_LINK_OK");
        wobble_uniform = glGetUniformLocation(program, "wobble");
        sampler_uniform = glGetUniformLocation(program, "sprite_tex");
        if (wobble_uniform < 0 || sampler_uniform < 0) {
            record("SPRITE_UNIFORM_FAILED"); release(); return false;
        }

        // 64x64 fully deterministic RGBA8 test image. Color, UV mirroring,
        // checker edges and transparency are visible without external files.
        constexpr int side = 64;
        std::array<std::uint8_t, side * side * 4> pixels{};
        for (int y = 0; y < side; ++y) {
            for (int x = 0; x < side; ++x) {
                const bool magenta = ((x / 8) + (y / 8)) % 2 == 0;
                const int at = (y * side + x) * 4;
                pixels[at] = magenta ? 255 : 5;
                pixels[at + 1] = magenta ? 22 : 235;
                pixels[at + 2] = magenta ? 170 : 255;
                pixels[at + 3] = 185; // 72.5% opacity => alpha blend witness
            }
        }
        glGenTextures(1, &texture);
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D, texture);
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, side, side, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
        glBindTexture(GL_TEXTURE_2D, 0);
        record("SPRITE_TEXTURE_UPLOAD");

        constexpr GLfloat quad[] = {
            // x, y, u, v
            -0.95f, -0.80f, 0.0f, 0.0f,
            -0.27f, -0.80f, 1.0f, 0.0f,
            -0.95f, -0.12f, 0.0f, 1.0f,
            -0.27f, -0.12f, 1.0f, 1.0f
        };
        glGenVertexArrays(1, &vao);
        glBindVertexArray(vao);
        glGenBuffers(1, &vbo);
        glBindBuffer(GL_ARRAY_BUFFER, vbo);
        glBufferData(GL_ARRAY_BUFFER, sizeof(quad), quad, GL_STATIC_DRAW);
        glEnableVertexAttribArray(0);
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(GLfloat),
                              reinterpret_cast<const void *>(0));
        glEnableVertexAttribArray(1);
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(GLfloat),
                              reinterpret_cast<const void *>(2 * sizeof(GLfloat)));
        glBindVertexArray(0);
        glBindBuffer(GL_ARRAY_BUFFER, 0);
        const GLenum error = glGetError();
        if (!vao || !vbo || !texture || error != GL_NO_ERROR) {
            record("SPRITE_INIT_GL_ERROR", static_cast<int>(error));
            release();
            return false;
        }
        ready = true;
        record("SPRITE_2D_READY");
        return true;
    }

    void draw(int frame) {
        glDisable(GL_DEPTH_TEST);
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        glUseProgram(program);
        glUniform1f(wobble_uniform, static_cast<float>(frame) * 0.032f);
        glUniform1i(sampler_uniform, 0);
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D, texture);
        glBindVertexArray(vao);
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
        glBindVertexArray(0);
        glBindTexture(GL_TEXTURE_2D, 0);
        glUseProgram(0);
        glDisable(GL_BLEND);
    }
    void release() {
        if (vbo) { glDeleteBuffers(1, &vbo); vbo = 0; }
        if (vao) { glDeleteVertexArrays(1, &vao); vao = 0; }
        if (texture) { glDeleteTextures(1, &texture); texture = 0; }
        if (program) { glDeleteProgram(program); program = 0; }
        ready = false;
    }
};
} // namespace

int main() {
    mkdir("/data/GodotPS5", 0755);
    record("BOOT_SHADER_PROBE");
    hui::ps5::Display display;
    if (!display.open(1920, 1080)) {
        record("EGL_OPEN_FAILED", static_cast<int>(display.last_error()));
        hui::sys::quit();
    }
    record("EGL_OPEN_OK");
    record("SURFACE_WIDTH", display.width());
    record("SURFACE_HEIGHT", display.height());
    log_string("GL_VERSION", glGetString(GL_VERSION));
    log_string("GL_RENDERER", glGetString(GL_RENDERER));
    log_string("GLSL_VERSION", glGetString(GL_SHADING_LANGUAGE_VERSION));

    Geometry geometry;
    if (!geometry.init()) record("GEOMETRY_FAILED_BACKGROUND_FALLBACK");
    Texture2DProbe sprite;
    if (!sprite.init()) record("SPRITE_FAILED_BACKGROUND_FALLBACK");
    hui::ps5::Pad pad;
    record(pad.open() ? "PAD_OPEN_OK" : "PAD_UNAVAILABLE");
    std::uint32_t previous = 0;
    int selected = 0;
    bool splash_hidden = false;
    bool draw_reported = false;
    bool sprite_draw_reported = false;
    int presented = 0;

    constexpr std::array<std::array<float, 3>, 3> colors = {{
        {{0.04f, 0.20f, 0.92f}}, // Blue
        {{0.04f, 0.78f, 0.24f}}, // Green
        {{0.92f, 0.12f, 0.18f}}  // Red
    }};
    for (int frame = 0; frame < 1800; ++frame) {
        std::array<hui::PadSample, 64> samples{};
        std::uint32_t pressed = 0;
        for (size_t i = 0, n = pad.read(samples); i < n; ++i) {
            pressed |= samples[i].buttons & ~previous;
            previous = samples[i].buttons;
        }
        if (pressed & hui::pad_bits::kCircle) { record("CIRCLE_EXIT"); break; }
        if (pressed & hui::pad_bits::kCross) {
            selected = (selected + 1) % 3;
            record("CROSS_COLOR", selected);
        }
        const auto &color = colors[(selected + frame / 120) % 3];
        glViewport(0, 0, display.width(), display.height());
        glClearColor(color[0], color[1], color[2], 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        if (geometry.ready) {
            geometry.draw(frame);
            if (!draw_reported) {
                const GLenum error = glGetError();
                record("GL_FIRST_DRAW_ERROR", static_cast<int>(error));
                if (error == GL_NO_ERROR) record("GL_TRIANGLE_SUBMITTED");
                draw_reported = true;
            }
        }
        if (sprite.ready) {
            sprite.draw(frame);
            if (!sprite_draw_reported) {
                const GLenum error = glGetError();
                record("SPRITE_FIRST_DRAW_ERROR", static_cast<int>(error));
                if (error == GL_NO_ERROR) record("SPRITE_2D_DRAW_SUBMITTED");
                sprite_draw_reported = true;
            }
        }
        if (!display.swap()) {
            record("EGL_SWAP_FAILED", static_cast<int>(display.last_error()));
            break;
        }
        ++presented;
        if (!splash_hidden) {
            hui::sys::hide_splash_screen();
            splash_hidden = true;
            record("FIRST_FRAME_PRESENTED");
        }
        if (presented == 60 || presented == 120 || presented == 600)
            record("PRESENTED_FRAME_COUNT", presented);
        hui::sys::sleep_us(1000);
    }
    record("TOTAL_PRESENTED", presented);
    pad.close();
    sprite.release(); // GL objects must be destroyed before EGL context.
    geometry.release(); // MUST be before EGL context teardown.
    display.close();
    record("CLEAN_SHUTDOWN");
    hui::sys::quit();
}
