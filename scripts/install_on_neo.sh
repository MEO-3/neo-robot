#!/bin/bash
set -e

echo "=== NEO Robot Installer ==="
echo "Installing dependencies for neo-robot..."

# Update package list
sudo apt-get update

# Install pip if not present
sudo apt-get install -y python3-pip

# Install remaining Python dependencies via pip
echo "[2/3] Installing Jedi and pyflakes via pip..."
pip3 install --break-system-packages -r ./neo-robot/requirements.txt

# Install neo-robot itself
echo "[3/3] Installing neo-robot..."
cd ./neo-robot
pip3 install --break-system-packages --no-deps .

# Add pip user bin to PATH if not already present
BIN_DIR="$HOME/.local/bin"
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "Adding $BIN_DIR to PATH..."
    echo 'export PATH="$PATH:$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    export PATH="$PATH:$BIN_DIR"
fi

echo ""
echo "Installation complete. Run 'neo-robot' to start."
