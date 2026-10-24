#!/usr/bin/env python3
"""Summarize the LAST PS5 M13 frame session from append-only Godot stdout.

Use with /data/GodotPS5/gles3-stdout.log after playing M12d on the
experimental Godot PS5 v0.1.7. No GUI/network/heavy dependencies.
The script never changes any user data.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from statistics import mean

NUMBERS = re.compile(r"([a-z_0-9]+)=([0-9.]+)")
ANCHOR = "GODOT_PS5_M13_NATIVE_FRAME_PROFILER_READY"
SPIKE = "GODOT_PS5_M13_FRAME_SPIKE"
SUMMARY = "GODOT_PS5_M13_FRAME_5S"
GODOT = "GODOT_PS5_M12D_FRAME_HITCH"

def extract_last_run(lines: list[str]) -> list[str]:
    starts = [i for i, line in enumerate(lines) if ANCHOR in line]
    return lines[starts[-1]:] if starts else []

def numbers(s: str) -> dict[str, float]:
    return {key: float(value) for key, value in NUMBERS.findall(s)}

def analyze(lines: list[str]) -> dict:
    current = extract_last_run(lines)
    spikes = [numbers(line) for line in current if SPIKE in line]
    stats = [numbers(line) for line in current if SUMMARY in line]
    shaders = [line for line in current if "[ps5-gallium] compile-shader" in line]
    godot_hitches = [line for line in current if GODOT in line]
    if not stats and not spikes:
        return {"status": "NO_M13_DATA", "native_profiler_booted": bool(current),
                "hint": "Run experimental native v0.1.7 with M12d PCK and collect fresh gles3-stdout.log"}
    total_frames = sum(int(x.get("frames", 0)) for x in stats)
    average_cpu = sum(x.get("avg_cpu_ms", 0) * x.get("frames", 0) for x in stats) / max(1, total_frames)
    average_swap = sum(x.get("avg_swap_ms", 0) * x.get("frames", 0) for x in stats) / max(1, total_frames)
    summary = {
        "status": "M13_LAST_SESSION_ONLY",
        "native_profiler_booted": True,
        "five_second_windows": len(stats),
        "total_frames_in_complete_windows": total_frames,
        "window_hitches_80ms": sum(int(s.get("spikes_80ms", 0)) for s in stats),
        "individual_spike_records": len(spikes),
        "godot_hitches_logged": len(godot_hitches),
        "gallium_compile_shaders_after_profiler_ready": len(shaders),
        "weighted_mean_cpu_before_swap_ms": round(average_cpu, 2),
        "weighted_mean_egl_swap_ms": round(average_swap, 2),
        "max_cpu_before_swap_ms": round(max([x.get("max_cpu_ms", 0) for x in stats] + [x.get("cpu_before_swap_ms", 0) for x in spikes] + [0]), 2),
        "max_egl_swap_ms": round(max([x.get("max_swap_ms", 0) for x in stats] + [x.get("egl_swap_ms", 0) for x in spikes] + [0]), 2),
        "max_total_frame_ms": round(max([x.get("max_frame_ms", 0) for x in stats] + [x.get("total_ms", 0) for x in spikes] + [0]), 2),
        "spike_examples": spikes[:12],
    }
    if summary["max_egl_swap_ms"] > summary["max_cpu_before_swap_ms"] * 2:
        summary["preliminary"] = "EGL_SWAP_DOMINATES_MAX: inspect PS5 Gallium/vsync/compositor; may include scheduling"
    elif summary["max_cpu_before_swap_ms"] > summary["max_egl_swap_ms"] * 2:
        summary["preliminary"] = "CPU_BEFORE_SWAP_DOMINATES_MAX: inspect Godot physics/render submission/I/O; may include scheduling"
    else:
        summary["preliminary"] = "MIXED_OR_INCONCLUSIVE: inspect individual spike records and shader timestamps"
    return summary

def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("stdout_log",type=Path)
    parser.add_argument("--json",action="store_true")
    args=parser.parse_args()
    result=analyze(args.stdout_log.read_text(errors="replace").splitlines())
    if args.json:
        print(json.dumps(result,indent=2,sort_keys=True))
    else:
        for key,value in result.items():
            if key!="spike_examples":print(f"{key}: {value}")
        if result.get("spike_examples"):
            print("first_spike_examples:",json.dumps(result["spike_examples"][:5]))
if __name__=="__main__":
    main()
