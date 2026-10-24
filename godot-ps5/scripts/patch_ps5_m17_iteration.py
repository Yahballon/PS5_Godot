#!/usr/bin/env python3
"""M17: phase-localize Godot 4.7.2 Main::iteration stalls on the experimental PS5 GLES3 build.

This is deliberately a pure upstream overlay, applied only inside the isolated CI
checkout. Validate all exact anchors to fail closed if Godot upstream changes.
Do not change engine order, Godot frame-time logic, sync, draw or physics.
"""
from pathlib import Path
import sys

MARKER = "GODOT_PS5_M17_PHASE_5S"
GUARD = "#if defined(PS5_ENABLED) && defined(GODOT_PS5_NATIVE_GLES3)"
SOURCE = Path("main/main.cpp")

def once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"Godot 4.7.2 M17 source anchor count {count}, expected 1: {old[:120]!r}")
    return text.replace(old, new, 1)

def guard(body: str) -> str:
    return f"{GUARD}\n{body}\n#endif\n"

def patch_main(source: str) -> str:
    if MARKER in source:
        if "GODOT_PS5_M17_PHASE_SPIKE" not in source:
            raise ValueError("Partial M17 instrumented source")
        return source

    entry = "bool Main::iteration() {"
    stop = "void Main::force_redraw() {"
    start = source.index(entry)
    end = source.index(stop, start)
    before, body, after = source[:start], source[start:end], source[end:]
    prefix = GUARD + "\n#include <cstdio>\n#include <cstdint>\n#endif\n"
    before = once(before, '#include "main.h"\n', '#include "main.h"\n' + prefix)

    body = once(body,
        "\tGodotProfileZone(\"Main::iteration\");",
        guard("\tconst uint64_t m17_start=OS::get_singleton()->get_ticks_usec();")
        + "\tGodotProfileZone(\"Main::iteration\");")

    body = once(body,
        "\tEngine::get_singleton()->_in_physics = false;\n\t}\n\n\tif (Input::get_singleton()->is_agile_input_event_flushing()) {",
        "\tEngine::get_singleton()->_in_physics = false;\n\t}\n"
        + guard("\tconst uint64_t m17_after_physics=OS::get_singleton()->get_ticks_usec();")
        + "\n\tif (Input::get_singleton()->is_agile_input_event_flushing()) {")

    body = once(body,
        "\tRenderingServer::get_singleton()->sync(); //sync if still drawing from previous frames.",
        guard("\tconst uint64_t m17_before_sync=OS::get_singleton()->get_ticks_usec();")
        + "\tRenderingServer::get_singleton()->sync(); //sync if still drawing from previous frames.\n"
        + guard("\tconst uint64_t m17_after_sync=OS::get_singleton()->get_ticks_usec();").rstrip("\n"))

    body = once(body,
        "\tprocess_ticks = OS::get_singleton()->get_ticks_usec() - process_begin;",
        guard("\tconst uint64_t m17_after_draw=OS::get_singleton()->get_ticks_usec();")
        + "\tprocess_ticks = OS::get_singleton()->get_ticks_usec() - process_begin;")

    body = once(body,
        "\tOS::get_singleton()->add_frame_delay(DisplayServer::get_singleton()->window_can_draw(), wake_for_events);",
        guard("\tconst uint64_t m17_before_delay=OS::get_singleton()->get_ticks_usec();")
        + "\tOS::get_singleton()->add_frame_delay(DisplayServer::get_singleton()->window_can_draw(), wake_for_events);\n"
        + guard("\tconst uint64_t m17_after_delay=OS::get_singleton()->get_ticks_usec();").rstrip("\n"))

    report = r'''
#if defined(PS5_ENABLED) && defined(GODOT_PS5_NATIVE_GLES3)
    // All phase durations measured on the same main thread using Godot's
    // monotonic clock. No GL fence, readback or forced CPU/GPU synchronization.
    static uint64_t m17_window_begin=0;
    static uint64_t m17_sum_us[6]={};
    static uint64_t m17_peak_us[6]={};
    static unsigned m17_frames=0,m17_spikes=0,m17_spike_logs=0;
    const uint64_t m17_samples[6]={
        m17_after_physics-m17_start,
        m17_before_sync-m17_after_physics,
        m17_after_sync-m17_before_sync,
        m17_after_draw-m17_after_sync,
        m17_before_delay-m17_after_draw,
        m17_after_delay-m17_before_delay
    };
    if(!m17_window_begin) {
        m17_window_begin=m17_after_delay;
        std::printf("GODOT_PS5_M17_PHASE_PROFILER_READY sections=physics,scene,sync,draw,tail,delay\n");
    }
    uint64_t m17_total_us=0;
    for(unsigned i=0;i<6;++i) {
        m17_sum_us[i]+=m17_samples[i];
        if(m17_samples[i]>m17_peak_us[i])m17_peak_us[i]=m17_samples[i];
        m17_total_us+=m17_samples[i];
    }
    ++m17_frames;
    if(m17_total_us>=80000) {
        ++m17_spikes;
        if(m17_spike_logs<4) {
            ++m17_spike_logs;
            std::printf("GODOT_PS5_M17_PHASE_SPIKE physics_ms=%.2f scene_ms=%.2f sync_ms=%.2f draw_ms=%.2f tail_ms=%.2f delay_ms=%.2f total_ms=%.2f\n",
                m17_samples[0]/1000.0,m17_samples[1]/1000.0,
                m17_samples[2]/1000.0,m17_samples[3]/1000.0,
                m17_samples[4]/1000.0,m17_samples[5]/1000.0,
                m17_total_us/1000.0);
        }
    }
    if(m17_after_delay>=m17_window_begin && m17_after_delay-m17_window_begin>=5000000) {
        std::printf("GODOT_PS5_M17_PHASE_5S frames=%u spikes_80ms=%u max_physics_ms=%.2f max_scene_ms=%.2f max_sync_ms=%.2f max_draw_ms=%.2f max_tail_ms=%.2f max_delay_ms=%.2f avg_physics_ms=%.2f avg_scene_ms=%.2f avg_sync_ms=%.2f avg_draw_ms=%.2f\n",
            m17_frames,m17_spikes,m17_peak_us[0]/1000.0,m17_peak_us[1]/1000.0,
            m17_peak_us[2]/1000.0,m17_peak_us[3]/1000.0,
            m17_peak_us[4]/1000.0,m17_peak_us[5]/1000.0,
            double(m17_sum_us[0])/double(m17_frames)/1000.0,
            double(m17_sum_us[1])/double(m17_frames)/1000.0,
            double(m17_sum_us[2])/double(m17_frames)/1000.0,
            double(m17_sum_us[3])/double(m17_frames)/1000.0);
        m17_window_begin=m17_after_delay;
        m17_frames=m17_spikes=m17_spike_logs=0;
        for(unsigned i=0;i<6;++i)m17_sum_us[i]=m17_peak_us[i]=0;
    }
#endif
'''
    # Do not instrument the fixed-FPS editor early-return branch. User PS5
    # player uses default fixed_fps==-1, so this is the normal game return.
    body = once(body, "\treturn exit;\n}", report + "\treturn exit;\n}")
    return before+body+after

def main() -> None:
    source = Path(sys.argv[1]) if len(sys.argv)>1 else SOURCE
    original = source.read_text()
    result = patch_main(original)
    if result != original:
        source.write_text(result)
        print("GODOT_PS5_M17_UPSTREAM_MAIN_PHASE_PATCHED")
    else:
        print("GODOT_PS5_M17_UPSTREAM_MAIN_ALREADY_PATCHED")

if __name__ == "__main__":
    main()
