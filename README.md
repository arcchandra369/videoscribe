# VideoScribe 🎙️

AI-powered video transcription and analysis tool. Paste any video URL from YouTube, Facebook, TikTok, Twitter/X, Instagram, Reddit, Twitch, or 1000+ other sites — VideoScribe downloads the audio, scans it for viruses, transcribes it with OpenAI Whisper, and lets you process the transcript with Claude AI.

---

## Features

- 🌐 Supports 1000+ video platforms via yt-dlp
- 🔒 ClamAV virus scanning on every downloaded file
- 🎙️ Local transcription via OpenAI Whisper (no data sent to external servers)
- 🤖 Claude AI processing — summarize, extract key points, generate notes, translate, and more
- 🖥️ Web UI + CLI — use whichever you prefer
- 🗑️ Auto-deletes audio files after transcription
- 🔑 You bring your own Anthropic API key — no shared credentials

---

## Requirements

Before running setup, install these system dependencies:

### ffmpeg (required)
| OS | Command |
|---|---|
| macOS | `brew install ffmpeg` |
| Ubuntu/Debian | `sudo apt install ffmpeg` |
| Windows | Download from https://ffmpeg.org/download.html and add to PATH |

### ClamAV (recommended for virus scanning)
| OS | Command |
|---|---|
| macOS | `brew install clamav` |
| Ubuntu/Debian | `sudo apt install clamav clamav-daemon` |
| Windows | Download from https://www.clamav.net/downloads |

To disable virus scanning, set `CLAMAV_ENABLED=false` in your `.env` file.

### Python 3.8+
Download from https://www.python.org/downloads/

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/videoscribe.git
cd videoscribe
```

### 2. Run setup
```bash
bash setup.sh
```
This installs all Python dependencies, creates required folders, and copies `.env.example` to `.env`.

### 3. Add your Anthropic API key
Open the `.env` file that was just created and replace the placeholder with your real key:
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```
Get your API key at: https://console.anthropic.com

### 4. (Optional) Configure settings
Other settings in `.env` you can adjust:
```
WHISPER_MODEL=base          # tiny/base/small/medium/large — larger = more accurate but slower
CLAMAV_ENABLED=true         # set false to skip virus scanning
AUTO_DELETE_AUDIO=true      # deletes downloaded audio after transcription
MAX_VIDEO_DURATION_MINUTES=120
```

---

## Usage

### Web UI (recommended)
```bash
python3 app.py
```
Then open **http://localhost:8080** in your browser. `localhost` always means your own machine — this works on any OS.

> **macOS note:** If ffmpeg isn't found, run with: `PATH="/opt/homebrew/bin:$PATH" python3 app.py`

### CLI
```bash
# Interactive mode
python3 main.py

# Direct mode
python3 main.py --url "https://youtube.com/watch?v=..." --task "summarize"
python3 main.py --url "https://..." --task "extract key points" --whisper-model medium
python3 main.py --url "https://..." --no-delete   # keep audio file after transcription
python3 main.py --url "https://..." --no-scan     # skip virus scan (not recommended)
```

---

## How It Works

```
Video URL → yt-dlp (audio download) → ClamAV (virus scan) → Whisper (transcription) → Claude AI (processing)
```

1. **Download** — yt-dlp extracts only the audio track (not the full video) to save space
2. **Scan** — ClamAV checks the file for threats before anything else touches it
3. **Transcribe** — Whisper runs locally on your machine, no data sent anywhere
4. **Clean** — Claude corrects speech-to-text errors (homophones, technical terms, proper nouns)
5. **Process** — Claude AI processes the transcript based on your chosen task

---

## Supported Platforms

YouTube, Facebook, Twitter/X, TikTok, Instagram, Reddit, Twitch, Vimeo, Dailymotion, and 1000+ more via [yt-dlp](https://github.com/yt-dlp/yt-dlp).

**Note on private videos:** Private or login-required videos require passing browser cookies to yt-dlp. See [yt-dlp cookie documentation](https://github.com/yt-dlp/yt-dlp#how-do-i-pass-cookies-to-yt-dlp) for details.

---

## Privacy & Security

- Your Anthropic API key is stored locally in `.env` and never committed to git
- Audio files are downloaded temporarily and auto-deleted after transcription
- Whisper transcription runs 100% locally — audio is never uploaded anywhere
- Only the text transcript is sent to the Anthropic API for processing
- Every downloaded file is scanned by ClamAV before processing

---

## Whisper Model Guide

| Model | Speed | Accuracy | Best For |
|---|---|---|---|
| tiny | Fastest | Basic | Quick drafts |
| base | Fast | Good | General use (default) |
| small | Moderate | Better | Most content |
| medium | Slow | Great | Technical content |
| large | Slowest | Best | Maximum accuracy |

---

## License

MIT License — free to use, modify, and distribute.

---

## Contributing

Pull requests welcome. Please open an issue first to discuss significant changes.
