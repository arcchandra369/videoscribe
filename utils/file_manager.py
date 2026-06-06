import os
import re
import shutil
import time
from datetime import datetime
from config import DOWNLOADS_DIR, QUARANTINE_DIR, TRANSCRIPTS_DIR, AUTO_DELETE_AUDIO
from utils import logger


def sanitize_filename(title: str) -> str:
    title = re.sub(r'[^\w\s\-]', '', title)
    title = re.sub(r'\s+', '_', title.strip())
    return title[:80]


def get_temp_path(filename: str) -> str:
    return os.path.join(DOWNLOADS_DIR, filename)


def get_transcript_path(filename: str) -> str:
    return os.path.join(TRANSCRIPTS_DIR, filename)


def quarantine_file(filepath: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    basename = os.path.basename(filepath)
    dest = os.path.join(QUARANTINE_DIR, f"{ts}_{basename}")
    shutil.move(filepath, dest)
    return dest


def cleanup_audio(filepath: str):
    if AUTO_DELETE_AUDIO and filepath and os.path.exists(filepath):
        os.remove(filepath)
        logger.success(f"Audio file deleted (AUTO_DELETE_AUDIO=true)")


def cleanup_stale_downloads(max_age_hours: int = 24):
    now = time.time()
    cutoff = now - (max_age_hours * 3600)
    if not os.path.isdir(DOWNLOADS_DIR):
        return
    for fname in os.listdir(DOWNLOADS_DIR):
        fpath = os.path.join(DOWNLOADS_DIR, fname)
        if os.path.isfile(fpath) and os.path.getmtime(fpath) < cutoff:
            os.remove(fpath)
            logger.info(f"Removed stale download: {fname}")


def check_disk_space(min_mb: int = 500) -> bool:
    stat = shutil.disk_usage(DOWNLOADS_DIR)
    free_mb = stat.free / (1024 * 1024)
    if free_mb < min_mb:
        logger.warning(f"Low disk space: {free_mb:.0f}MB free (minimum {min_mb}MB recommended)")
        return False
    return True
