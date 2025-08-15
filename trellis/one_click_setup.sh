#!/bin/bash

# 1-click setup for TRELLIS
# This script will clone TRELLIS, copy setup files, and run environment setup automatically.

set -e

# Variables
TRELLIS_REPO="https://github.com/microsoft/TRELLIS.git"
TRELLIS_DIR="TRELLIS"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Clone TRELLIS with submodules
if [ ! -d "$TRELLIS_DIR" ]; then
    echo "Cloning TRELLIS repository..."
    git clone --recurse-submodules "$TRELLIS_REPO"
else
    echo "TRELLIS directory already exists. Skipping clone."
fi

cd "$TRELLIS_DIR"

# Copy setup_env.sh and main.py to TRELLIS directory
wget https://raw.githubusercontent.com/thong-pvn/scripts/main/trellis/main.py
wget https://raw.githubusercontent.com/thong-pvn/scripts/main/trellis/setup_env.sh

# Make setup_env.sh executable
chmod +x setup_env.sh

# Run setup_env.sh
echo "Running setup_env.sh..."
./setup_env.sh

echo "\n[INFO] TRELLIS environment setup complete!"
