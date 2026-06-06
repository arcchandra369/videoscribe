#!/usr/bin/env python3
import os
import json
import queue
import threading
from datetime import datetime

from flask import Flask, render_template, request, jsonify, Response, send_file
from config import TRANSCRIPTS_DIR, WHISPER_MODEL

app = Flask(__name__, template_folder="web/templates", static_folder="web/static")
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Per-request event queues for SSE streaming
_event_queues: dict[str, queue.Queue] = {}


def _push(req_id: str, event: str, data: str):
    q = _event_queues.get(req_id)
    if q:
        q.put(f"event: {event}\ndata: {json.dumps(data)}\n\n")


def _sse_done(req_id: str):
    q = _event_queues.get(req_id)
    if q:
        q.put(None)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/history")
def history():
    files = []
    for f in sorted(os.listdir(TRANSCRIPTS_DIR), reverse=True):
        if f.endswith(".txt") and not f.endswith("_processed.txt"):
            files.append(f)
    return jsonify(files[:20])


@app.route("/transcript/<filename>")
def get_transcript(filename):
    path = os.path.join(TRANSCRIPTS_DIR, filename)
    if not os.path.exists(path):
        return jsonify({"error": "Not found"}), 404
    with open(path, encoding="utf-8") as f:
        return jsonify({"content": f.read()})


@app.route("/delete/<filename>", methods=["DELETE"])
def delete_file(filename):
    path = os.path.join(TRANSCRIPTS_DIR, filename)
    if not os.path.exists(path):
        return jsonify({"error": "Not found"}), 404
    os.remove(path)
    return jsonify({"status": "deleted"})


@app.route("/download/<filename>")
def download_file(filename):
    path = os.path.join(TRANSCRIPTS_DIR, filename)
    if not os.path.exists(path):
        return "Not found", 404
    return send_file(path, as_attachment=True)


@app.route("/process", methods=["POST"])
def process():
    data = request.json
    url = data.get("url", "").strip()
    task_choice = data.get("task", "").strip()
    whisper_model = data.get("whisper_model", WHISPER_MODEL)
    req_id = data.get("req_id", "default")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    _event_queues[req_id] = queue.Queue()

    def run():
        import config
        config.WHISPER_MODEL = whisper_model

        try:
            from core.downloader import download_audio, detect_platform
            from core.scanner import scan_file
            from core.transcriber import transcribe
            from core.processor import process_transcript
            import anthropic

            platform = detect_platform(url)
            _push(req_id, "log", f"[→] Platform detected: {platform}")

            _push(req_id, "log", "[↓] Downloading audio...")
            audio_path = download_audio(url)
            _push(req_id, "log", f"[✓] Download complete")

            _push(req_id, "log", "[🔍] Scanning for viruses...")
            clean = scan_file(audio_path)
            if not clean:
                _push(req_id, "scan_status", "THREAT")
                _push(req_id, "log", "[✗] Threat detected — file quarantined")
                _push(req_id, "error", "Virus threat detected. File has been quarantined.")
                _sse_done(req_id)
                return
            _push(req_id, "scan_status", "CLEAN")
            _push(req_id, "log", "[✓] File passed ClamAV scan")

            _push(req_id, "log", f"[🎙] Transcribing with Whisper ({whisper_model} model)...")
            info = transcribe(audio_path, video_title=url.split("/")[-1] or "video")
            _push(req_id, "log", f"[✓] Transcription complete — Language: {info['language'].upper()}")

            task_map = {
                "summarize": "Please provide a comprehensive summary of the following transcript.",
                "keypoints": "Extract the most important key points from this transcript as a clean bullet list.",
                "notes": "Generate detailed, well-structured notes from this transcript.",
                "actions": "Extract every action item or to-do from this transcript. Format as a numbered list.",
                "translate": "Translate the following transcript to Spanish.",
                "blog": "Write a well-structured, engaging blog post based on this transcript.",
            }
            task_instruction = task_map.get(task_choice, task_choice or task_map["summarize"])

            _push(req_id, "log", "[✏] Cleaning transcript (fixing speech-to-text errors)...")
            from core.processor import clean_transcript
            import anthropic as ant
            client = ant.Anthropic(api_key=config.ANTHROPIC_API_KEY)
            cleaned_text = clean_transcript(info["text"], client)
            info["text"] = cleaned_text
            txt_path = os.path.join(config.TRANSCRIPTS_DIR, f"{info['base_name']}.txt")
            if os.path.exists(txt_path):
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(cleaned_text)
            _push(req_id, "transcript", cleaned_text)
            _push(req_id, "log", "[✓] Transcript cleaned")

            _push(req_id, "log", "[🤖] Claude is processing...")

            output_parts = []

            with client.messages.stream(
                model=config.CLAUDE_MODEL,
                max_tokens=4096,
                messages=[{"role": "user", "content": f"{task_instruction}\n\nTRANSCRIPT:\n{info['text']}"}],
            ) as stream:
                for text in stream.text_stream:
                    output_parts.append(text)
                    _push(req_id, "claude_chunk", text)

            full_output = "".join(output_parts)
            out_path = os.path.join(TRANSCRIPTS_DIR, f"{info['base_name']}_processed.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(full_output)

            _push(req_id, "log", f"[✓] Output saved: {os.path.basename(out_path)}")
            _push(req_id, "done", {
                "transcript_file": os.path.basename(info["txt_path"]),
                "output_file": os.path.basename(out_path),
            })

        except Exception as e:
            _push(req_id, "error", str(e))
        finally:
            _sse_done(req_id)

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"status": "started", "req_id": req_id})


@app.route("/stream/<req_id>")
def stream(req_id):
    def generate():
        q = _event_queues.get(req_id)
        if not q:
            yield "event: error\ndata: \"Unknown request\"\n\n"
            return
        while True:
            msg = q.get()
            if msg is None:
                yield "event: close\ndata: \"done\"\n\n"
                break
            yield msg
        _event_queues.pop(req_id, None)

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


if __name__ == "__main__":
    print("\n  VideoScribe Web UI")
    print("  Starting at http://localhost:5000\n")
    app.run(debug=False, threaded=True, port=8080)
