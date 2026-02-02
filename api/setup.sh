#!/bin/bash
# Setup script for TikTok API

set -e

echo "[INFO] Setting up TikTok API..."

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 could not be found. Please install Python 3."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment 'venv'..."
    python3 -m venv venv
else
    echo "[INFO] Virtual environment 'venv' already exists."
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "[INFO] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "[INFO] Installing Playwright Chromium browser..."
playwright install chromium

echo ""
echo "[INFO] Setup complete."
echo ""
echo "To start the server, run:"
echo "  source venv/bin/activate"
echo "  uvicorn app:app --reload --host 0.0.0.0 --port 5000"
