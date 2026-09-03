#!/usr/bin/env bash
# Build Android APK in CI (GitHub Actions / cloud Linux).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BUILD_TYPE="${BUILD_TYPE:-debug}"

apply_release_signing() {
  if [[ ! -f "$ROOT/signing/gudosnake-release.keystore" ]]; then
    echo "Release keystore not found."
    exit 1
  fi

  python3 <<'PY'
from pathlib import Path
import re

spec_path = Path("buildozer.spec")
text = spec_path.read_text(encoding="utf-8")
keystore = Path("signing/gudosnake-release.keystore").resolve().as_posix()

signing_block = f"""
android.keystore = {keystore}
android.keystore_password = {__import__('os').environ['ANDROID_KEYSTORE_PASSWORD']}
android.keyalias = {__import__('os').environ['ANDROID_KEY_ALIAS']}
android.keyalias_password = {__import__('os').environ['ANDROID_KEY_PASSWORD']}
""".strip()

text = re.sub(
    r"# Release signing \(filled temporarily by scripts/build-release\.sh\)[\s\S]*?(?=\n\[buildozer\])",
    "# Release signing (CI)\n" + signing_block + "\n\n",
    text,
    count=1,
)
spec_path.write_text(text, encoding="utf-8")
print("Applied CI release signing config")
PY
}

if [[ "$BUILD_TYPE" == "release" ]]; then
  if [[ -z "${ANDROID_KEYSTORE_BASE64:-}" ]]; then
    echo "ANDROID_KEYSTORE_BASE64 secret is required for release builds."
    exit 1
  fi
  mkdir -p signing
  echo "$ANDROID_KEYSTORE_BASE64" | base64 --decode > signing/gudosnake-release.keystore
  apply_release_signing
  touch main.py
  buildozer android p4a -- --help
  buildozer -v android release
else
  touch main.py
  buildozer android p4a -- --help
  buildozer -v android debug
fi

echo ""
echo "Built APK files:"
ls -lh bin/*.apk
