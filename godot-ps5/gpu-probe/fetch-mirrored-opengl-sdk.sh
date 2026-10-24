#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Pinned, independent archival mirror of the now-unavailable upstream
# ps5-opengl SDK v1.0.2 release. The mirror's claim of originality is
# UNVERIFIED, so both archive digest and inner file manifests are checked.
set -euo pipefail
version=1.0.2
sha256=30d8e51dd062739b629346102be5932728ba714bc50b1bdcdf08306c8843d9a4
url="https://github.com/KernelForgeLabs/ps5-opengl-sdk-mirror/releases/download/sdk-v${version}/ps5-opengl-sdk-${version}.tar.gz"
root="${1:-/tmp/ps5-gpu-opengl}"
mkdir -p "$root"
archive="$root/ps5-opengl-sdk-${version}.tar.gz"
if [[ ! -f "$archive" ]] || ! printf '%s  %s\n' "$sha256" "$archive" | sha256sum --check --strict --quiet; then
  echo "Fetching checksum-pinned UNOFFICIAL PS5 OpenGL SDK mirror (v${version})" >&2
  curl -fL --retry 3 --retry-delay 2 -o "$archive.partial" "$url"
  mv -- "$archive.partial" "$archive"
fi
printf '%s  %s\n' "$sha256" "$archive" | sha256sum --check --strict --quiet
# A matching *outer* digest must precede extraction. Inner checks below
# catch broken/missing files and ensure the expected SDK layout.
prefix="$root/ps5-opengl-sdk-${version}/sdk"
if [[ ! -f "$prefix/manifest.sha256" ]]; then
  mkdir -p "$root"
  # Extract the SDK subtree only; no executable scripts from the archive are run.
  tar -xzf "$archive" -C "$root" --no-same-owner --no-same-permissions \
    "ps5-opengl-sdk-${version}/sdk"
fi
for required in manifest.sha256 include/EGL/egl.h include/GL/glcorearb.h \
   include/ps5_opengl_display.h lib/libPS5OpenGL.a \
   lib/libSceAgc.so lib/libSceAgcDriver.so; do
  test -f "$prefix/$required" || { echo "SDK missing $required" >&2; exit 1; }
done
(cd "$prefix" && sha256sum --check --strict --quiet manifest.sha256)
echo "Verified 1.0.2 unofficial SDK archive SHA-256 and extracted SDK manifest" >&2
printf '%s\n' "$prefix"
