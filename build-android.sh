#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

mkdir -p docker/buildozer docker/gradle

echo "Building Docker image (first run may take a few minutes)..."
docker build --tag gudosnake/buildozer "$ROOT"

echo "Building Android APK (first run downloads SDK/NDK and may take 30-60 min)..."
docker run --rm \
  -u "$(id -u):$(id -g)" \
  -v "$ROOT/docker/buildozer:/home/user/.buildozer" \
  -v "$ROOT/docker/gradle:/home/user/.gradle" \
  -v "$ROOT:/home/user/hostcwd" \
  gudosnake/buildozer -v android debug

echo ""
echo "Done. APK output:"
ls -lh "$ROOT/bin/"*.apk 2>/dev/null || true
