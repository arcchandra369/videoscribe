import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
AUTO_DELETE_AUDIO = os.getenv("AUTO_DELETE_AUDIO", "true").lower() == "true"
CLAMAV_ENABLED = os.getenv("CLAMAV_ENABLED", "true").lower() == "true"
MAX_VIDEO_DURATION_MINUTES = int(os.getenv("MAX_VIDEO_DURATION_MINUTES", "120"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
QUARANTINE_DIR = os.path.join(BASE_DIR, "quarantine")
TRANSCRIPTS_DIR = os.path.join(BASE_DIR, "transcripts")

for d in [DOWNLOADS_DIR, QUARANTINE_DIR, TRANSCRIPTS_DIR]:
    os.makedirs(d, exist_ok=True)

CLAUDE_MODEL = "claude-opus-4-5"

def is_first_run():
    return ANTHROPIC_API_KEY in ("", "your_anthropic_api_key_here")
