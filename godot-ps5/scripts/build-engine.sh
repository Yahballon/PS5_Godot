#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd)
: "$GODOT_SOURCE"
: "$PS5_PAYLOAD_SDK"
test -f "$GODOT_SOURCE/SConstruct"
test -d "$PS5_PAYLOAD_SDK/target/include/c++/v1"
python3 "$root/scripts/check_overlay.py"
mkdir -p "$GODOT_SOURCE/platform/ps5"
cp -a "$root/engine/platform/ps5/." "$GODOT_SOURCE/platform/ps5/"
python3 "$root/scripts/patch_ps5_kvm.py" "$GODOT_SOURCE"
python3 "$root/scripts/patch_ps5_setup_trace.py" "$GODOT_SOURCE"
python3 "$root/scripts/patch_ps5_post_settings_trace.py" "$GODOT_SOURCE"
python3 "$root/scripts/patch_ps5_userdata.py" "$GODOT_SOURCE"
python3 "$root/scripts/patch_ps5_dir_access.py" "$GODOT_SOURCE"
# M17: experimental native GLES3 profiling only. The original Godot source
# and known-good headless/scene-bridge builds remain unchanged.
if [[ "${GODOT_PS5_M17_PHASE_PROFILE:-0}" == "1" ]]; then
  [[ "${GODOT_PS5_NATIVE_GLES3:-0}" == "1" ]] || {
    echo 'M17 profiling requires native PS5 GLES3' >&2; exit 2;
  }
  python3 "$root/scripts/patch_ps5_m17_iteration.py" "$GODOT_SOURCE/main/main.cpp"
fi
# M24 low-overhead original Godot renderer stage timing, without M19/M23
# per-GL-API wrappers, GL fences, shader mutations, or changed frame pacing.
if [[ "${GODOT_PS5_M24_RENDER_STAGES:-0}" == "1" ]]; then
  [[ "${GODOT_PS5_NATIVE_GLES3:-0}" == "1" ]] || {
    echo 'M24 stage timings require experimental PS5 GLES3' >&2; exit 2;
  }
  python3 "$root/scripts/patch_ps5_m24_render_stages.py" \
    "$GODOT_SOURCE/servers/rendering/rendering_server_default.cpp"
fi
# M25: isolated, low-frequency timers separating canvas render, compositor
# blit, gl_end_frame and viewport bookkeeping in Godot's original GLES3.
if [[ "${GODOT_PS5_M25_VIEWPORT_STAGES:-0}" == "1" ]]; then
  [[ "${GODOT_PS5_NATIVE_GLES3:-0}" == "1" ]] || {
    echo 'M25 viewport timestamps require native GLES3' >&2; exit 2;
  }
  python3 "$root/scripts/patch_ps5_m25_viewport.py" \
    "$GODOT_SOURCE/servers/rendering/renderer_viewport.cpp"
fi
cd "$GODOT_SOURCE"
jobs=4
if test -n "$(printenv BUILD_JOBS || :)"; then jobs="$(printenv BUILD_JOBS)"; fi
# A first HEADLESS GDScript smoke test should not link Embree / Jolt /
# 3D render importers. Building all modules worked, but the final PS5 link
# failed on optional Embree symbols. The full engine can be re-enabled with
# GODOT_MODULE_SET=full after core runtime execution is proven.
module_flags=()
case "${GODOT_MODULE_SET:-smoke}" in
  smoke)
    module_flags=(modules_enabled_by_default=no
                  module_gdscript_enabled=yes
                  module_text_server_fb_enabled=yes
                  disable_3d=yes
                  disable_xr=yes
                  disable_advanced_gui=yes)
    ;;
  full)
    ;;
  *)
    echo 'GODOT_MODULE_SET must be smoke or full' >&2
    exit 2
    ;;
esac
# M9b: Default 'smoke' disables all modules except GDScript/TextServer.
# Without this explicit flag the real GodotPhysics2D factory never registers,
# and Main::initialize_physics() falls back to PhysicsServer2DDummy.
# Keep this opt-in to protect confirmed PPSA99843/99845/99847 old builds.
if [[ "${GODOT_PS5_PHYSICS2D:-0}" == "1" ]]; then
  module_flags+=(module_godot_physics_2d_enabled=yes disable_physics_2d=no)
  echo 'GODOT_PS5_M9B_PHYSICS_MODULE_ENABLED=1'
fi
# M10c: Support genuine TrueType/OpenType glyph rendering through the
# upstream FreeType module plus the existing TextServerFallback backend.
# Without this, FontFile.load_dynamic_font() can read a .ttf but has_char()
# returns false and Godot reports "engine is compiled without FreeType".
# Keep old v0.1.3 and other PS5 titles unchanged unless explicitly enabled.
if [[ "${GODOT_PS5_FREETYPE:-0}" == "1" ]]; then
  if [[ "${GODOT_MODULE_SET:-smoke}" != "smoke" ]]; then
    echo 'GODOT_PS5_FREETYPE requires the fallback-text smoke module set' >&2
    exit 2
  fi
  module_flags+=(module_freetype_enabled=yes builtin_freetype=yes
                module_text_server_fb_enabled=yes
                module_text_server_adv_enabled=no)
  echo 'GODOT_PS5_M10C_FREETYPE_MODULE_ENABLED=1'
fi
# Only CI's opt-in GLES3 archive gate can change this default.
gl_backend=no
if [[ "${GODOT_PS5_GLES3_ARCHIVES:-0}" == "1" ]]; then gl_backend=yes; fi
scons platform=ps5 target=template_debug library_type=static_library \
    arch=x86_64 lto=none vulkan=no opengl3="$gl_backend" d3d12=no metal=no \
    module_mono_enabled=no use_llvm=yes disable_path_overrides=no "${module_flags[@]}" -j"$jobs"
echo 'Engine archive build completed: NOT an installable PS5 title.'
