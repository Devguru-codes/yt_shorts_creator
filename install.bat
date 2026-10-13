@echo off
setlocal enabledelayedexpansion
title YouTube Shorts Creator - One-Click Installer

echo ==========================================================
echo    YouTube Shorts Creator - Automated Setup Script
echo ==========================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please download and install Python 3.10+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [*] Python detected successfully.
echo.

:: 2. Create Virtual Environment
if not exist "venv" (
    echo [*] Creating virtual environment (venv)...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [+] Virtual environment created.
) else (
    echo [*] Virtual environment already exists.
)

:: 3. Activate Virtual Environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

:: 4. Upgrade pip and install dependencies
echo [*] Upgrading pip...
python -m pip install --upgrade pip

echo [*] Installing required packages from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install some dependencies.
    pause
    exit /b 1
)
echo [+] All Python dependencies installed successfully!
echo.

:: 5. Check FFmpeg
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] FFmpeg was not found in your system PATH!
    echo FFmpeg is required to process audio and video clips.
    echo You can install it on Windows easily via winget:
    echo     winget install Gyan.FFmpeg
    echo Or download from: https://ffmpeg.org/download.html
    echo.
) else (
    echo [+] FFmpeg detected in system PATH.
)

:: 6. Setup .env file
if not exist ".env" (
    echo [*] Creating .env file from .env.example...
    copy .env.example .env >nul
    echo [+] Created .env file. Please open .env and add your Gemini / Groq API keys!
) else (
    echo [*] .env file already exists.
)

echo.
echo ==========================================================
echo               SETUP COMPLETED SUCCESSFULLY!
echo ==========================================================
echo.
echo To run the automated podcast shorts pipeline:
echo    1. Open .env and add your GEMINI_API_KEY and GROQ_API_KEY
echo    2. Run:
echo       venv\Scripts\activate
echo       python channel_automator.py "https://www.youtube.com/@joerogan" --max-videos 3 --num-clips 50 --auto-upload
echo.
pause
