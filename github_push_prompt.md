# Claude Code Prompt — Push VideoScribe to GitHub Safely

---

## PASTE THIS ENTIRE PROMPT INTO CLAUDE CODE:

---

I have a finished Python app called VideoScribe in the current directory. I need you to prepare it for a public GitHub release. This means:

1. Creating a bulletproof `.gitignore` that protects all sensitive files
2. Creating a professional `README.md` so anyone can set it up easily
3. Verifying no sensitive data exists anywhere in the codebase
4. Initializing git and pushing to a new public GitHub repo

Work through each step below carefully and completely.

---

## STEP 1 — CREATE `.gitignore`

Create a `.gitignore` file in the project root with the following content. Do not skip any of these entries — each one protects something specific:

```
# ── API Keys & Secrets ──────────────────────────────
.env
*.env
.env.local
.env.production
secrets.json
credentials.json

# ── Downloaded Media (temp files) ───────────────────
downloads/
*.mp3
*.mp4
*.m4a
*.webm
*.wav
*.ogg
*.flac

# ── Quarantine (flagged virus files) ────────────────
quarantine/

# ── Transcript output files ─────────────────────────
transcripts/

# ── Graphify knowledge graph output ─────────────────
graphify-out/

# ── Python cache ────────────────────────────────────
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.egg-info/
dist/
build/
*.egg
.eggs/

# ── Virtual environments ─────────────────────────────
venv/
.venv/
env/
ENV/
.env/

# ── Whisper model cache ──────────────────────────────
~/.cache/whisper/
*.pt

# ── macOS system files ───────────────────────────────
.DS_Store
.AppleDouble
.LSOverride
Thumbs.db

# ── IDE / Editor files ───────────────────────────────
.vscode/
.idea/
*.swp
*.swo
*~

# ── Logs ─────────────────────────────────────────────
*.log
logs/

# ── Test artifacts ───────────────────────────────────
.pytest_cache/
.coverage
htmlcov/
```

---

## STEP 2 — SECURITY AUDIT

Before touching git, scan the entire codebase for any accidentally hardcoded sensitive data.

Run the following checks and report the results of each:

### 2a — Scan for hardcoded API keys
```bash
grep -rn "sk-ant-" . --include="*.py" --include="*.js" --include="*.html" --include="*.json" --exclude-dir=".git"
grep -rn "ANTHROPIC_API_KEY\s*=\s*['\"]sk" . --include="*.py" --exclude-dir=".git"
```
If any matches are found: stop, report exactly which file and line, and ask me how to proceed before continuing.

### 2b — Scan for any other API key patterns
```bash
grep -rn "api_key\s*=\s*['\"][a-zA-Z0-9]" . --include="*.py" --exclude-dir=".git" -i
grep -rn "password\s*=\s*['\"][^'\"]" . --include="*.py" --exclude-dir=".git" -i
grep -rn "secret\s*=\s*['\"][^'\"]" . --include="*.py" --exclude-dir=".git" -i
```
If any real values (not placeholder text like "your_key_here") are found: stop and report.

### 2c — Confirm `.env` file exists but will be ignored
```bash
ls -la .env 2>/dev/null && echo ".env EXISTS — must be gitignored" || echo ".env not found"
```

### 2d — Confirm sensitive directories are empty or will be ignored
```bash
ls downloads/ 2>/dev/null | head -5
ls quarantine/ 2>/dev/null | head -5
ls transcripts/ 2>/dev/null | head -5
```
Report what's in these folders. They will be gitignored but confirm they exist locally.

Report a clean summary at the end:
```
SECURITY AUDIT RESULTS:
  ✓ No hardcoded API keys found
  ✓ .env is present locally but will be gitignored
  ✓ downloads/, quarantine/, transcripts/ will be gitignored
  ✓ Safe to proceed
```
If anything fails this audit, stop and report before proceeding to Step 3.

---

## STEP 3 — CREATE `README.md`

Create a professional, well-structured `README.md` in the project root. It must include every section below — do not skip any.

```markdown
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
# Open http://localhost:8080 in your browser
```

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
4. **Process** — Claude AI processes the transcript based on your instructions

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
```

---

## STEP 4 — INITIALIZE GIT & VERIFY

Run these commands one at a time and confirm each succeeds:

```bash
# Initialize git repo (skip if already initialized)
git init

# Stage all files
git add .

# CRITICAL: Run this before committing and show me the full output
git status
```

After running `git status`, carefully review the output and confirm:
- `.env` does **NOT** appear in the staged files list
- `downloads/` does **NOT** appear
- `quarantine/` does **NOT** appear  
- `transcripts/` does **NOT** appear
- `graphify-out/` does **NOT** appear
- `.env.example` **DOES** appear (this is safe — it has no real values)
- `README.md` **DOES** appear
- `requirements.txt` **DOES** appear

If `.env` or any sensitive file appears in the staged list, run `git rm --cached .env` immediately and do NOT proceed until it is removed.

Print a confirmation:
```
GIT STATUS REVIEW:
  ✓ .env is NOT staged
  ✓ downloads/ is NOT staged
  ✓ quarantine/ is NOT staged
  ✓ transcripts/ is NOT staged
  ✓ README.md is staged
  ✓ .env.example is staged
  ✓ Safe to commit
```

---

## STEP 5 — COMMIT

Once the status check passes:

```bash
git commit -m "Initial release — VideoScribe v1.0

- yt-dlp audio extraction from 1000+ platforms
- ClamAV virus scanning before transcription
- OpenAI Whisper local transcription
- Claude AI transcript processing with streaming
- Flask web UI + CLI interface
- Auto-delete audio after transcription
- Chunked processing for long videos"
```

---

## STEP 6 — PUSH TO GITHUB

### Check if GitHub CLI is installed:
```bash
gh --version
```

### If GitHub CLI is installed:
```bash
# Authenticate if needed
gh auth status || gh auth login

# Create the repo and push
gh repo create videoscribe --public --push --source=. --description "AI-powered video transcription tool — supports YouTube, Facebook, TikTok, and 1000+ sites"
```

### If GitHub CLI is NOT installed:
Print these instructions clearly for me to follow manually:

```
GitHub CLI is not installed. Follow these steps:

OPTION A — Install GitHub CLI (recommended):
  macOS:   brew install gh
  Windows: winget install --id GitHub.cli
  Linux:   https://github.com/cli/cli/blob/trunk/docs/install_linux.md

  Then run:
    gh auth login
    gh repo create videoscribe --public --push --source=. --description "AI-powered video transcription tool"

OPTION B — Manual push via GitHub website:
  1. Go to https://github.com/new
  2. Name the repo: videoscribe
  3. Set visibility: Public
  4. Do NOT check "Initialize with README" (we already have one)
  5. Click "Create repository"
  6. Copy the repo URL (e.g. https://github.com/YOUR_USERNAME/videoscribe.git)
  7. Run these commands:
       git remote add origin https://github.com/YOUR_USERNAME/videoscribe.git
       git branch -M main
       git push -u origin main
```

---

## STEP 7 — FINAL VERIFICATION

After pushing, run:

```bash
# Confirm what was pushed
git log --oneline
git remote -v
```

Then print a final summary:

```
✓ GITHUB PUSH COMPLETE

  Repo URL:     https://github.com/YOUR_USERNAME/videoscribe
  Branch:       main
  Commits:      1

  FILES PUSHED (safe):
    ✓ README.md
    ✓ .gitignore
    ✓ .env.example        (placeholder values only — no real API key)
    ✓ requirements.txt
    ✓ setup.sh
    ✓ main.py
    ✓ app.py
    ✓ config.py
    ✓ core/
    ✓ utils/
    ✓ web/

  FILES KEPT LOCAL (never pushed):
    ✗ .env                (your API key stays on your machine only)
    ✗ downloads/          (temp audio files)
    ✗ quarantine/         (virus-flagged files)
    ✗ transcripts/        (your personal transcripts)
    ✗ graphify-out/       (local knowledge graph)

  WHAT USERS WILL DO:
    1. git clone your repo
    2. bash setup.sh
    3. Add their OWN Anthropic API key to .env
    4. python3 app.py
```

---

## NOTES

- Never run `git add .env` at any point
- If you ever update the app and want to push changes: `git add .` → `git status` (verify) → `git commit -m "message"` → `git push`
- To add a new environment variable in the future: add the placeholder to `.env.example` (push this), add the real value to `.env` (never push this)
