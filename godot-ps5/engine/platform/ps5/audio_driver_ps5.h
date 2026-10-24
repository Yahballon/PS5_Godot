// SPDX-License-Identifier: MIT
// M11c experimental native Godot -> PS5 libSceAudioOut bridge.
// Opt-in; never used by the working PPSA99847 v0.1.4 baseline.
#pragma once

#include "core/os/mutex.h"
#include "core/os/thread.h"
#include "core/templates/safe_refcount.h"
#include "core/templates/vector.h"
#include "servers/audio/audio_server.h"

class AudioDriverPS5 final : public AudioDriver {
    static constexpr int MIX_RATE = 48000;
    static constexpr int BLOCK_FRAMES = 256;
    static constexpr int CHANNELS = 2;
    static void thread_main(void *userdata);
    Thread thread;
    Mutex mutex;
    SafeFlag running;
    SafeFlag exiting;
    Vector<int32_t> godot_samples;
    Vector<int16_t> output_samples;
    int handle = -1;
    uint64_t delivered = 0;
    uint64_t failures = 0;

public:
    const char *get_name() const override { return "PS5 AudioOut"; }
    Error init() override;
    void start() override;
    int get_mix_rate() const override { return MIX_RATE; }
    SpeakerMode get_speaker_mode() const override { return SPEAKER_MODE_STEREO; }
    float get_latency() override { return float(BLOCK_FRAMES * 2) / float(MIX_RATE); }
    void lock() override { mutex.lock(); }
    void unlock() override { mutex.unlock(); }
    void finish() override;
    ~AudioDriverPS5() override { finish(); }
};
