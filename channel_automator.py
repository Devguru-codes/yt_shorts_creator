import argparse
import sys
import subprocess
import yt_dlp
import logging
import json
import os
from pathlib import Path
from shorts_generator import generate_shorts

# Fix Windows charmap encode error for arrow characters (→)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("automator.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

HISTORY_FILE = "processed_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return set(json.load(f))
        except Exception as e:
            logging.error(f"Failed to load history: {e}")
            return set()
    return set()

def save_history(history_set):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(list(history_set), f, indent=4)
    except Exception as e:
        logging.error(f"Failed to save history: {e}")

def get_channel_videos(channel_url, max_videos=50):
    if "/@" in channel_url and not channel_url.endswith("/videos") and not channel_url.endswith("/shorts") and not channel_url.endswith("/streams"):
        channel_url = channel_url.rstrip("/") + "/videos"
        
    logging.info(f"Scraping channel: {channel_url}")
    ydl_opts = {
        'extract_flat': 'in_playlist',
        'playlist_end': max_videos,
        'quiet': True,
        'no_warnings': True,
    }
    videos = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(channel_url, download=False)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry and (entry.get('url') or entry.get('webpage_url')):
                        videos.append(entry.get('url') or entry.get('webpage_url'))
            else:
                videos.append(info.get('url') or info.get('webpage_url'))
        except Exception as e:
            logging.error(f"Error extracting channel info: {e}")
            
    # yt-dlp flat extraction sometimes ignores playlist_end, so we enforce it here
    videos = videos[:max_videos]
    logging.info(f"Filtered down to {len(videos)} videos to process.")
    return videos

def main():
    parser = argparse.ArgumentParser(description="Automated Channel-to-Shorts Pipeline")
    parser.add_argument("channel_url", help="YouTube Channel or Playlist URL")
    parser.add_argument("--max-videos", type=int, default=3, help="Max recent videos to scan (default 3)")
    parser.add_argument("--num-clips", type=int, default=3, help="How many shorts to render per video (default: 3)")
    parser.add_argument("--auto-upload", action="store_true", help="Automatically trigger mass_upload.py after generation")
    args = parser.parse_args()

    history = load_history()
    videos = get_channel_videos(args.channel_url, args.max_videos)
    
    # Filter out already processed videos
    new_videos = [v for v in videos if v not in history]
    
    if not new_videos:
        logging.info("No new videos found to process. They are all in the history index!")
        return 0
        
    logging.info(f"Starting processing for {len(new_videos)} new videos.")
        
    for idx, video_url in enumerate(new_videos, 1):
        logging.info("=========================================")
        logging.info(f"Processing Video {idx}/{len(new_videos)}: {video_url}")
        logging.info("=========================================")
        
        try:
            result = generate_shorts(
                youtube_url=video_url,
                num_clips=args.num_clips,
                aspect_ratio="9:16",
                download_format="720",
                language=None,
                mode="local",
            )
            logging.info(f"Successfully processed {video_url}. Generated {len(result.get('shorts', []))} shorts.")
            
            # Add to history and save immediately so we don't repeat on crash
            history.add(video_url)
            save_history(history)
            
            # Clean up the gigantic source video to prevent disk space exhaustion!
            source_path = result.get("source_video_url")
            if source_path and os.path.exists(source_path):
                try:
                    os.remove(source_path)
                    base = os.path.splitext(source_path)[0]
                    if os.path.exists(base + ".json"):
                        os.remove(base + ".json")
                    if os.path.exists(base + ".srt"):
                        os.remove(base + ".srt")
                    logging.info(f"Cleaned up 2-hour source video to free space: {source_path}")
                except Exception as e:
                    logging.warning(f"Could not delete source video {source_path}: {e}")
                    
            if args.auto_upload:
                logging.info(f"Triggering Automatic Mass Upload for {video_url}...")
                try:
                    subprocess.run([sys.executable, "mass_upload.py", "output"], check=True)
                except Exception as e:
                    logging.error(f"Failed to run mass_upload.py: {e}")
            
        except Exception as e:
            logging.error(f"Failed to process {video_url}: {e}")
            
if __name__ == "__main__":
    sys.exit(main())
