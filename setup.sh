#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "   YouTube Shorts Creator - Automated Setup Script (Linux/macOS)"
echo "=========================================================="
echo ""

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found."
    echo "Please install Python 3.10+ using your package manager (e.g. brew install python3 or sudo apt install python3 python3-venv)"
    exit 1
fi

echo "[*] Python3 detected: $(python3 --version)"

# 2. Virtual Environment
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment (venv)..."
    python3 -m venv venv
    echo "[+] Virtual environment created."
else
    echo "[*] Virtual environment already exists."
fi

# 3. Activate venv
echo "[*] Activating virtual environment..."
source venv/bin/activate

# 4. Install dependencies
echo "[*] Upgrading pip..."
pip install --upgrade pip

echo "[*] Installing dependencies from requirements.txt..."
pip install -r requirements.txt
echo "[+] Dependencies installed successfully!"

# 5. Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "[WARNING] ffmpeg could not be found."
    echo "Please install ffmpeg (e.g., brew install ffmpeg or sudo apt install ffmpeg)"
else
    echo "[+] ffmpeg detected."
fi

# 6. Setup .env
if [ ! -f ".env" ]; then
    echo "[*] Creating .env from .env.example..."
    cp .env.example .env
    echo "[+] .env created. Please edit .env with your API keys."
else
    echo "[*] .env already exists."
fi

echo ""
echo "=========================================================="
echo "              SETUP COMPLETED SUCCESSFULLY!"
echo "=========================================================="
echo "To run the pipeline:"
echo "   source venv/bin/activate"
echo "   python channel_automator.py \"https://www.youtube.com/@joerogan\" --max-videos 3 --num-clips 50 --auto-upload"
echo ""
