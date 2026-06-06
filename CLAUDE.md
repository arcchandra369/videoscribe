# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

**Web UI (preferred):**
```bash
PATH="/opt/homebrew/bin:$PATH" python3 app.py
# Open http://localhost:8080
```
Port 5000 is blocked on macOS by Control Center — the app is configured to use 8080.

**CLI:**
```bash
python3 main.py
python3 main.py --url "https://..." --task "summarize"
```

**First-time setup:**
```bash
bash setup.sh          # checks ffmpeg, ClamAV, installs pip deps, creates .env
brew install ffmpeg    # required for audio extraction
pip3 install -r requirements.txt
```

## Architecture

The pipeline has five sequential stages:

1. **`core/downloader.py`** — `download_audio(url)` uses `yt-dlp` + FFmpeg to extract audio as MP3 into `downloads/`. Detects platform, enforces `MAX_VIDEO_DURATION_MINUTES`, retries once on failure.

2. **`core/scanner.py`** — `scan_file(path)` runs ClamAV virus scan (tries `clamd` socket first, falls back to `clamscan` CLI). Infected files are moved to `quarantine/`. If ClamAV is unavailable, scan is skipped with a warning.

3. **`core/transcriber.py`** — `transcribe(audio_path)` runs OpenAI Whisper locally. Saves `transcripts/<name>.txt` and `<name>.json` (with segments/metadata). Deletes audio after if `AUTO_DELETE_AUDIO=true`.

4. **`core/processor.py`** — `clean_transcript(text, client)` runs a Claude streaming pass to fix Whisper speech-to-text errors (e.g. "clawd"→"Claude", homophones, technical terms) before the main task. Then `process_transcript(text, task, base_name)` sends the cleaned transcript to Claude with streaming. Transcripts over 160,000 chars are chunked with overlap, processed separately, then merged. Saves output to `transcripts/<name>_processed.txt`.

**Web layer (`app.py`):** Flask server with SSE streaming — the `/process` endpoint runs the pipeline in a background thread and pushes log/status/chunk events to the browser via `/stream/<req_id>`. Has `TEMPLATES_AUTO_RELOAD=True` so template changes apply without restart. Endpoints: `GET /history`, `GET /transcript/<f>`, `GET /download/<f>`, `DELETE /delete/<f>`, `POST /process`, `GET /stream/<req_id>`.

**Config (`config.py`):** All settings come from `.env` via `python-dotenv`. `CLAUDE_MODEL` is hardcoded to `claude-opus-4-5` (not in `.env`). Directories (`downloads/`, `quarantine/`, `transcripts/`) are created at import time.

**Frontend (`web/templates/index.html`, `web/static/style.css`):** White/black/blue professional theme using Inter (body) and Playfair Display (brand name). Log and content boxes use a dark (`#0f172a`) background. The history section starts empty on page load — items only appear after a transcription in the current session. Each history item has a download button and an ✕ delete button that removes the file from disk via `DELETE /delete/<filename>`.

## Key configuration

`.env` values:
- `ANTHROPIC_API_KEY` — required
- `WHISPER_MODEL` — `tiny/base/small/medium/large` (default: `base`; `medium` recommended for better accuracy)
- `CLAMAV_ENABLED` — set `false` to skip virus scanning entirely
- `MAX_VIDEO_DURATION_MINUTES` — default 120; use `--confirm-long` CLI flag to override per-run
- `AUTO_DELETE_AUDIO` — deletes MP3 from `downloads/` after transcription

## Transcript cleaning

After Whisper transcribes, `clean_transcript()` in `core/processor.py` makes a streaming Claude call with a system prompt instructing it to fix speech-to-text misrecognitions while preserving meaning exactly. Uses `max_tokens=16000` per chunk (claude-opus-4-5 max output is 64,000). The cleaned text overwrites the raw `.txt` file and is what gets shown in the browser and passed to the main processing task.

## Dependencies

Requires system-level `ffmpeg` (for yt-dlp audio extraction) and optionally `clamav` (for virus scanning). All Python deps are in `requirements.txt`. On macOS, ffmpeg is at `/opt/homebrew/bin/ffmpeg` — always prefix server launch with `PATH="/opt/homebrew/bin:$PATH"` when running from a background process.

## Knowledge graph (graphify)

A graphify knowledge graph has been built for this codebase. Outputs live in `graphify-out/`:
- `graph.html` — interactive visualization, open in any browser
- `graph.json` — raw graph data (265 nodes, 351 edges, 41 communities)
- `GRAPH_REPORT.md` — full audit report with god nodes, surprising connections, suggested questions

**To query the graph** (answer questions about the codebase):
```bash
graphify query "how does SSE streaming work in app.py"
```

**To rebuild after significant code changes:**
```bash
cd videoscribe
graphify --update    # re-extracts only changed files
```

**Key graph findings:**
- God nodes (highest centrality): `download_audio` → `scan_file` → `transcribe` → `clean_transcript` → `process_transcript` — this is the exact pipeline execution order
- The prompt engineering content in `transcripts/` (community 1) is structurally isolated from the pipeline code (community 0) — the app has no code-level awareness of what it transcribes
- `rate_limit_retry` is a singleton in `processor.py` — not reused by downloader or scanner which handle retries independently

**Communities of note:**
- Community 0: Claude API Pipeline (config, all core processor functions)
- Community 1: Prompt Engineering Concepts (transcript content)
- Community 2: Virus Scanner & File Utils
- Community 3 & 4: Flask Routes + Web/SSE layer
- Community 6: Transcript Processor (clean + process functions)
- Community 7: Frontend JS Logic (download, delete, SSE handlers)
