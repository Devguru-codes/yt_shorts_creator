# 🎙️ YouTube Shorts Creator & Auto-Scheduler
> **Fully Autonomous Channel-to-Shorts Pipeline with AI Highlight Detection, Face-Tracking Vertical Crop, and YouTube Studio Scheduling.**

An end-to-end automated pipeline designed for long-form content, interviews, and massive 2- to 3-hour podcasts (such as *The Joe Rogan Experience*). It scrapes recent episodes, transcribes speech with Faster Whisper, detects viral moments using multi-model AI (Gemini + Groq failover), crops footage vertically to 9:16 with face tracking, generates click-worthy titles/metadata, and automatically uploads & schedules the shorts via YouTube Studio into prime-time audience windows.

---

## ⚡ What This Pipeline Does

```
 1. Scrape Channel
    (yt-dlp extracts recent videos & checks processed_history.json)
         │
         ▼
 2. Transcribe Audio
    (Local Faster Whisper with Voice Activity Detection - VAD)
         │
         ▼
 3. Extract 50+ Viral Highlights
    (Gemini 2.5 Flash with automatic high-speed Groq failover)
         │
         ▼
 4. Smart Vertical 9:16 Video Rendering
    (OpenCV facial tracking & centered motion-smoothed crop)
         │
         ▼
 5. Auto Disk Space Cleanup
    (Immediately purges raw 2-hour source files to prevent disk overflow)
         │
         ▼
 6. YouTube Studio Uploader & Scheduler
    (Selenium + Firefox profile schedules shorts across peak engagement windows)
```

1. **Autonomous Channel Scraping**: Feeds in a channel URL (e.g. `https://www.youtube.com/@joerogan`), extracts video links, and checks `processed_history.json` so no video is ever processed twice.
2. **Local Faster Whisper Transcription**: Transcribes hours of audio locally with high-accuracy VAD filtering, writing cached timestamped `.srt` files.
3. **Multi-Model AI Highlight Extraction**:
   - Analyzes long-form transcripts in parallel chunks.
   - Ranks moments based on emotional hooks, shocking statements, humor, and curiosity gaps.
   - **Multi-Model Redundancy**: If Google Gemini hits free-tier rate limits (`429 Too Many Requests`), the system automatically switches to **Groq** (`openai/gpt-oss-120b` or `qwen/qwen3.8-27b`) so the pipeline never crashes mid-podcast.
4. **Intelligent 9:16 Vertical Cropping**:
   - Uses OpenCV face-tracking to follow speakers and keep them centered in vertical frame.
   - Generates dual versions: smart face-tracked crop and cinematic blurred letterbox.
5. **Disk Overflow Prevention**: Long podcasts take 3–8 GB each. The automator automatically deletes the raw source video immediately after slicing the clips, keeping your disk clean.
6. **Automated YouTube Studio Scheduling**:
   - Uses your logged-in Firefox profile to bypass Google bot detection.
   - Alternates video schedules between peak global viewer windows:
     - **Window A (10:30 PM IST / 1:00 PM EST)**: Captures US lunch breaks and European evening audiences.
     - **Window B (4:30 AM IST / 7:00 PM EST)**: Captures US prime-time evening audiences.
   - Automatically cleans up uploaded shorts from the `output/` folder once confirmed.

---

## 🛠️ Prerequisites

* **Python 3.10+**
* **FFmpeg** installed and accessible in your system `PATH`.
  * *Windows*: `winget install Gyan.FFmpeg`
  * *macOS*: `brew install ffmpeg`
  * *Ubuntu/Debian*: `sudo apt install ffmpeg`
* **Mozilla Firefox** (for automated YouTube Studio uploading).
* **API Keys**:
  * Free **Google Gemini API Key**: [Google AI Studio](https://aistudio.google.com/)
  * Free **Groq API Key** (for failover redundancy): [Groq Console](https://console.groq.com/)

---

## 🚀 Quick Start & Installation

### Option 1: One-Click Installer (Windows)
Double-click `install.bat` or run:
```cmd
install.bat
```
This script automatically creates a virtual environment, installs all required packages from `requirements.txt`, checks FFmpeg, and prepares your `.env` file.

### Option 2: One-Click Installer (macOS / Linux)
```bash
chmod +x setup.sh
./setup.sh
```

### Option 3: Manual Installation
```bash
# 1. Create and activate a virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 2. Upgrade pip and install all dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Configure your API keys
cp .env.example .env
```

---

## ⚙️ Configuration (`.env`)

Open `.env` in any text editor and fill in your keys:

```ini
# Primary LLM Provider
LLM_PROVIDER=gemini

# Google Gemini API Keys (You can provide a primary and a backup)
GEMINI_API_KEY="your_primary_gemini_key_here"
BACKUP_GEMINI_API_KEY="your_backup_gemini_key_here"
GEMINI_MODEL="gemini-2.5-flash"

# Groq High-Speed Failover Keys (Takes over if Gemini rate-limits)
GROQ_API_KEY="your_groq_api_key_here"
GROQ_API_KEY_1="your_groq_api_key_here"
GROQ_MODEL="openai/gpt-oss-120b"

# Local Faster Whisper Settings
# Keep set to "cpu" on Windows machines to avoid CUDA DLL missing errors
LOCAL_WHISPER_DEVICE="cpu"
LOCAL_WHISPER_MODEL="medium"

# Local Output Directory
LOCAL_OUTPUT_DIR="output"
```

---

## 📖 How to Run

### 1. Full Autonomous Channel Pipeline (Recommended)
This runs the full end-to-end loop: scrapes the latest videos from a channel, extracts up to 50 viral highlights per video, saves disk space, and automatically uploads & schedules the shorts via YouTube Studio.

```bash
# Windows
.\venv\Scripts\Activate.ps1
python channel_automator.py "https://www.youtube.com/@joerogan" --max-videos 3 --num-clips 50 --auto-upload

# Linux / macOS
source venv/bin/activate
python channel_automator.py "https://www.youtube.com/@joerogan" --max-videos 3 --num-clips 50 --auto-upload
```

**CLI Flags:**
* `channel_url`: The YouTube channel URL or playlist URL.
* `--max-videos`: Number of recent videos to scan and process (e.g. `3`).
* `--num-clips`: How many viral shorts to generate per episode (e.g. `50`).
* `--auto-upload`: Automatically triggers the scheduling mass-uploader once generation completes.

---

### 2. Generate Shorts for a Single Video
If you want to extract viral shorts from a single YouTube URL without uploading:

```bash
python main.py "https://www.youtube.com/watch?v=EXAMPLE_ID" --num-clips 50 --mode local
```

The generated 9:16 shorts and metadata `.json` files will be saved in the `output/` folder.

---

### 3. Standalone Mass Uploader & Scheduler
If you already have rendered shorts in your `output/` folder and want to upload and schedule them to YouTube Studio:

```bash
python mass_upload.py output
```

**How YouTube Authentication Works:**
* The uploader automatically detects your existing Firefox browser profile.
* As long as you are already logged into YouTube Studio in Firefox on your machine, it attaches to your session without asking for passwords or triggering 2-factor authentication blocks.
* It uses persistent scheduling state (`schedule_state.json`) to spread uploads evenly across future dates at 10:30 PM IST and 4:30 AM IST.

---

## 📂 Project Structure

```
yt_shorts_creator/
├── channel_automator.py         # Autonomous channel scraper & processing orchestrator
├── mass_upload.py               # Selenium YouTube Studio mass-uploader & scheduler
├── main.py                      # Single-video CLI entrypoint
├── install.bat                  # One-click Windows setup script
├── setup.sh                     # One-click Linux/macOS setup script
├── requirements.txt             # Python package dependencies
├── .env.example                 # Environment configuration template
├── .gitignore                   # Ignores credentials, videos, logs, and cookies
├── shorts_generator/            # Core processing engine
│   ├── config.py                # Configuration loader
│   ├── highlights.py            # AI virality scoring & moment extraction
│   └── local/
│       ├── downloader.py        # yt-dlp downloader with disk cache
│       ├── transcription.py     # Faster Whisper speech-to-text
│       ├── llm.py               # Gemini + Groq failover dispatch
│       └── clipper.py           # OpenCV face tracking & FFmpeg 9:16 vertical crop
└── youtube_uploader_selenium/   # Headless browser automation library
```

---

## 🛡️ Reliability & Safeguards

* **Failover Circuit**: Extracts 50+ highlights across long videos without crashing by automatically failing over from Gemini to Groq if rate limits occur.
* **Disk Space Safety**: Source videos (often 2–4 GB) are deleted as soon as rendering completes.
* **Source Video Upload Filter**: `mass_upload.py` strictly ignores raw `source_*.mp4` files, ensuring only 9:16 shorts are uploaded.
* **Windows CUDA Resilience**: Forces CPU Whisper by default to avoid missing `cublas64_12.dll` driver crashes on Windows.

---

## 📜 License
MIT License. Free for personal and commercial use.
