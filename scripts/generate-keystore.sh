#!/usr/bin/env bash
# Generate a release keystore for signing APK/AAB.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KEYSTORE="$ROOT/signing/gudosnake-release.keystore"
PROPS="$ROOT/signing/keystore.properties"

mkdir -p "$ROOT/signing"

if [[ -f "$KEYSTORE" ]]; then
  echo "Keystore already exists: $KEYSTORE"
  echo "Delete it first if you want to create a new one."
  exit 1
fi

read -r -p "Keystore password: " -s STORE_PASS
echo
read -r -p "Key password (Enter to reuse keystore password): " -s KEY_PASS
echo
if [[ -z "$KEY_PASS" ]]; then
  KEY_PASS="$STORE_PASS"
fi

keytool -genkeypair \
  -v \
  -keystore "$KEYSTORE" \
  -alias gudosnake \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -storepass "$STORE_PASS" \
  -keypass "$KEY_PASS" \
  -dname "CN=Gudo Snake, OU=Mobile, O=GudoSnake, L=Local, ST=Local, C=CN"

cat > "$PROPS" <<EOF
KEYSTORE_FILE=signing/gudosnake-release.keystore
KEYSTORE_PASSWORD=${STORE_PASS}
KEY_ALIAS=gudosnake
KEY_PASSWORD=${KEY_PASS}
EOF

chmod 600 "$PROPS" 2>/dev/null || true

echo ""
echo "Created:"
echo "  $KEYSTORE"
echo "  $PROPS"
echo ""
echo "Keep these files safe. Do not commit them to git."
