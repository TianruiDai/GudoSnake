#!/usr/bin/env bash
# One-time WSL/Ubuntu setup for Gudo Snake Android builds.
set -euo pipefail

echo "==> Updating apt packages..."
sudo apt update
sudo apt install -y \
  git zip unzip openjdk-17-jdk python3-pip python3-venv \
  autoconf automake libtool pkg-config zlib1g-dev \
  libncurses5-dev libncursesw5-dev libtinfo5 cmake \
  libffi-dev libssl-dev ccache

echo "==> Installing buildozer..."
pip3 install --user --upgrade pip
pip3 install --user buildozer "Cython<0.30"

if ! grep -q '.local/bin' ~/.bashrc; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

export PATH="$HOME/.local/bin:$PATH"

echo "==> Verifying buildozer..."
buildozer --version

PROJECT="/mnt/c/Users/Matri/pytorch_env/pygame/gudosnake"
if [[ -d "$PROJECT" ]]; then
  echo ""
  echo "Setup complete. Next steps:"
  echo "  cd $PROJECT"
  echo "  python3 scripts/generate_assets.py   # optional, regenerate icons"
  echo "  buildozer -v android debug           # first build (30-60 min)"
else
  echo ""
  echo "Setup complete. Open your project folder under /mnt/c/... and run buildozer."
fi
