import os
import re
import time
from datetime import datetime
from urllib.parse import urlparse

import yt_dlp

from config import DOWNLOADS_DIR, MAX_VIDEO_DURATION_MINUTES
from utils import logger
from utils.file_manager import sanitize_filename, check_disk_space

PLATFORM_PATTERNS = {
    "YouTube": r"(youtube\.com|youtu\.be)",
    "Facebook": r"facebook\.com",
    "Twitter/X": r"(twitter\.com|x\.com)",
    "TikTok": r"tiktok\.com",
    "Instagram": r"instagram\.com",
    "Reddit": r"reddit\.com",
    "Twitch": r"twitch\.tv",
    "Vimeo": r"vimeo\.com",
    "Dailymotion": r"dailymotion\.com",
}


def detect_platform(url: str) -> str:
    for name, pattern in PLATFORM_PATTERNS.items():
        if re.search(pattern, url, re.IGNORECASE):
            return name
    return "Unknown"


class ProgressHook:
    def __init__(self):
        self._started = False

    def __call__(self, d):
        if d["status"] == "downloading":
            if not self._started:
                print("", end="", flush=True)
                self._started = True
            pct = d.get("_percent_str", "?%").strip()
            speed = d.get("_speed_str", "").strip()
            eta = d.get("_eta_str", "").strip()
            print(f"\r  [↓] Downloading... {pct}  speed: {speed}  ETA: {eta}   ", end="", flush=True)
        elif d["status"] == "finished":
            print(f"\r  [↓] Download complete{' ' * 40}", flush=True)


def get_video_info(url: str) -> dict:
    ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)


def download_audio(url: str, confirm_long: bool = False) -> str:
    check_disk_space(500)

    platform = detect_platform(url)
    logger.success(f"Platform detected: {platform}")

    logger.info("Fetching video info...")
    try:
        info = get_video_info(url)
    except yt_dlp.utils.DownloadError as e:
        msg = str(e)
        if "Private" in msg or "login" in msg.lower() or "members" in msg.lower():
            raise RuntimeError(
                "This video is private or requires login.\n"
                "  Workaround: use yt-dlp cookies:\n"
                "    python main.py --url URL --cookies /path/to/cookies.txt"
            )
        if "not supported" in msg.lower():
            raise RuntimeError(f"Unsupported URL or platform: {url}")
        raise RuntimeError(f"Could not fetch video info: {msg}")

    title = info.get("title", "untitled")
    duration_sec = info.get("duration", 0) or 0
    duration_min = duration_sec / 60

    logger.success(f"Video: \"{title}\" ({int(duration_min)}m {int(duration_sec % 60)}s)")

    if duration_min > MAX_VIDEO_DURATION_MINUTES and not confirm_long:
        raise RuntimeError(
            f"Video is {duration_min:.1f} minutes long (limit: {MAX_VIDEO_DURATION_MINUTES} min).\n"
            "  Use --confirm-long to proceed anyway."
        )

    safe_title = sanitize_filename(title)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_template = os.path.join(DOWNLOADS_DIR, f"{safe_title}_{ts}.%(ext)s")

    hook = ProgressHook()
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "progress_hooks": [hook],
        "quiet": True,
        "no_warnings": True,
    }

    for attempt in range(2):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            break
        except yt_dlp.utils.DownloadError as e:
            if attempt == 0:
                logger.warning("Download failed, retrying once...")
                time.sleep(2)
            else:
                raise RuntimeError(f"Download failed after retry: {e}")

    expected_path = os.path.join(DOWNLOADS_DIR, f"{safe_title}_{ts}.mp3")
    if not os.path.exists(expected_path):
        for f in os.listdir(DOWNLOADS_DIR):
            if f.startswith(f"{safe_title}_{ts}"):
                expected_path = os.path.join(DOWNLOADS_DIR, f)
                break

    if not os.path.exists(expected_path):
        raise RuntimeError("Downloaded file not found after download completed.")

    logger.success(f"Download complete: {expected_path}")
    return expected_path
