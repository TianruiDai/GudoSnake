#!/usr/bin/env bash
# Build a signed release APK using signing/keystore.properties
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PROPS="$ROOT/signing/keystore.properties"
SPEC="$ROOT/buildozer.spec"
SPEC_BACKUP="$ROOT/buildozer.spec.bak"

cleanup() {
  if [[ -f "$SPEC_BACKUP" ]]; then
    mv -f "$SPEC_BACKUP" "$SPEC"
  fi
}
trap cleanup EXIT

if [[ ! -f "$PROPS" ]]; then
  echo "Missing $PROPS"
  echo "Run: bash scripts/generate-keystore.sh"
  echo "Or copy signing/keystore.properties.example to signing/keystore.properties"
  exit 1
fi

# shellcheck disable=SC1090
source "$PROPS"

KEYSTORE_PATH="$ROOT/$KEYSTORE_FILE"
if [[ ! -f "$KEYSTORE_PATH" ]]; then
  echo "Keystore not found: $KEYSTORE_PATH"
  exit 1
fi

cp "$SPEC" "$SPEC_BACKUP"

python3 <<PY
from pathlib import Path
import re

spec_path = Path("$SPEC")
text = spec_path.read_text(encoding="utf-8")

signing_block = f'''
android.keystore = {Path("$KEYSTORE_PATH").as_posix()}
android.keystore_password = $KEYSTORE_PASSWORD
android.keyalias = $KEY_ALIAS
android.keyalias_password = $KEY_PASSWORD
'''.strip()

text = re.sub(
    r"# Release signing \\(filled temporarily by scripts/build-release\\.sh\\)[\\s\\S]*?(?=\\n\\[buildozer\\])",
    "# Release signing (filled temporarily by scripts/build-release.sh)\\n" + signing_block + "\\n\\n",
    text,
    count=1,
)

spec_path.write_text(text, encoding="utf-8")
print("Applied signing config for release build")
PY

buildozer -v android release

echo ""
echo "Release APK:"
ls -lh "$ROOT/bin/"*release*.apk 2>/dev/null || ls -lh "$ROOT/bin/"*.apk
