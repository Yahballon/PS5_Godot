// SPDX-License-Identifier: MIT
// Upstream Godot 4.7.2 PCM mixer -> PS5 homebrew AudioOut.
// Native audio output API has no DRM/media decode dependency.
// Requires libSceAudioOut.so import stub from public ps5-payload-sdk.
// Header signatures follow the tested PS5 SDK audio probe; no binary blobs.
#include "audio_driver_ps5.h"
#include "core/os/os.h"
#include "core/string/print_string.h"
#include <cstdint>
#include <cstring>

// PS5 user-service AudioOut ABI: user_id, type, index, frames, sample_rate, format.
// See ps5_sdk_audio_open_default() in Rufidj/PS5_DEV_HOMEBREW.
extern "C" {
int sceAudioOutInit(void);
int sceAudioOutOpen(int user_id, int type, int index, unsigned int buffer_frames,
                    unsigned int sample_rate, unsigned int sample_format);
int sceAudioOutOutput(int handle, const void *interleaved_pcm);
int sceAudioOutClose(int handle);
}

Error AudioDriverPS5::init() {
    if (handle >= 0) {
        return OK;
    }
    constexpr int USER_MAIN = 0xff;
    constexpr int PORT_MAIN = 0;
    constexpr int PORT_INDEX = 0;
    constexpr int FORMAT_S16_STEREO = 1;

    const int init_result = sceAudioOutInit();
    print_line(vformat("GODOT_PS5_M11C_AUDIOOUT_INIT rc=%d", init_result));
    if (init_result < 0) {
        return ERR_CANT_OPEN;
    }
    handle = sceAudioOutOpen(USER_MAIN, PORT_MAIN, PORT_INDEX, BLOCK_FRAMES,
                             MIX_RATE, FORMAT_S16_STEREO);
    print_line(vformat("GODOT_PS5_M11C_AUDIOOUT_OPEN handle=%d", handle));
    if (handle < 0) {
        handle = -1;
        return ERR_CANT_OPEN;
    }
    godot_samples.resize(BLOCK_FRAMES * CHANNELS);
    output_samples.resize(BLOCK_FRAMES * CHANNELS);
    delivered = 0;
    failures = 0;
    exiting.clear();
    running.clear();
    // Godot 4.7.2 Thread::start returns Thread::ID (nonzero on success),
    // NOT Godot Error/OK (zero). v0.1.5 misclassified a working worker
    // as ERR_CANT_CREATE and closed AudioOut under the still-running thread.
    thread.start(&AudioDriverPS5::thread_main, this);
    if (!thread.is_started()) {
        print_line("GODOT_PS5_M11D_AUDIOOUT_THREAD_START_FAIL");
        sceAudioOutClose(handle);
        handle = -1;
        return ERR_CANT_CREATE;
    }
    print_line("GODOT_PS5_M11D_AUDIOOUT_THREAD_STARTED");
    print_line("GODOT_PS5_M11C_AUDIOOUT_READY rate=48000 channels=2 frames=256");
    return OK;
}

void AudioDriverPS5::start() {
    if (handle >= 0) {
        running.set();
        print_line("GODOT_PS5_M11C_AUDIOOUT_START");
    }
}

void AudioDriverPS5::thread_main(void *userdata) {
    auto *driver = static_cast<AudioDriverPS5 *>(userdata);
    // Output() is a blocking ~5.3 ms PS5 kernel operation. Never call it
    // while holding Godot's mixer mutex: otherwise scene updates can hang.
    while (!driver->exiting.is_set()) {
        driver->lock();
        if (driver->running.is_set()) {
            driver->audio_server_process(BLOCK_FRAMES, driver->godot_samples.ptrw());
            for (int i = 0; i < BLOCK_FRAMES * CHANNELS; i++) {
                // Godot mixer uses signed 32-bit fixed-point; S16=top 16 bits.
                const int32_t sample = driver->godot_samples[i] >> 16;
                driver->output_samples.write[i] = static_cast<int16_t>(sample);
            }
        } else {
            std::memset(driver->output_samples.ptrw(), 0,
                        BLOCK_FRAMES * CHANNELS * sizeof(int16_t));
        }
        driver->unlock();

        const int rc = sceAudioOutOutput(driver->handle, driver->output_samples.ptr());
        if (rc < 0) {
            driver->failures++;
            if (driver->failures <= 6 || driver->failures % 512 == 0) {
                print_line(vformat("GODOT_PS5_M11D_AUDIOOUT_OUTPUT_ERROR rc=%d failures=%d",
                                   rc, static_cast<int64_t>(driver->failures)));
            }
            // Prevent fast loop if output did not block. Do not fake success.
            OS::get_singleton()->delay_usec(2000);
            if (driver->failures >= 256) {
                print_line("GODOT_PS5_M11C_AUDIOOUT_FATAL_STOP");
                driver->exiting.set();
            }
        } else {
            driver->delivered++;
            if (driver->delivered == 1 || driver->delivered % 2048 == 0) {
                print_line(vformat("GODOT_PS5_M11D_AUDIOOUT_OUTPUT_OK blocks=%d",
                                   static_cast<int64_t>(driver->delivered)));
            }
        }
    }
}

void AudioDriverPS5::finish() {
    exiting.set();
    if (thread.is_started()) {
        thread.wait_to_finish();
    }
    running.clear();
    if (handle >= 0) {
        const int rc = sceAudioOutClose(handle);
        print_line(vformat("GODOT_PS5_M11D_AUDIOOUT_CLOSE rc=%d blocks=%d errors=%d",
                           rc, static_cast<int64_t>(delivered),
                           static_cast<int64_t>(failures)));
        handle = -1;
    }
}
