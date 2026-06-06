import os
import json
from datetime import datetime

from config import WHISPER_MODEL, TRANSCRIPTS_DIR
from utils import logger
from utils.file_manager import sanitize_filename, cleanup_audio

VALID_MODELS = ["tiny", "base", "small", "medium", "large"]


def transcribe(audio_path: str, video_title: str = "transcript") -> dict:
    logger.step("🎙", f"Transcribing with Whisper ({WHISPER_MODEL} model)...")
    logger.info("Models: tiny=fastest, base=good, small=better, medium=great, large=best/slowest")

    try:
        import whisper
    except ImportError:
        raise RuntimeError("openai-whisper is not installed. Run: pip install openai-whisper")

    model_name = WHISPER_MODEL if WHISPER_MODEL in VALID_MODELS else "base"
    if model_name != WHISPER_MODEL:
        logger.warning(f"Unknown model '{WHISPER_MODEL}', falling back to 'base'")

    logger.info(f"Loading Whisper model '{model_name}' (will auto-download on first use)...")
    model = whisper.load_model(model_name)

    result = model.transcribe(audio_path, verbose=False)

    transcript_text = result.get("text", "").strip()
    language = result.get("language", "unknown")
    segments = result.get("segments", [])

    if not transcript_text:
        raise RuntimeError("Transcription produced empty output — audio may be silent or corrupt.")

    logger.success(f"Transcription complete — Language: {language.upper()}")

    safe_title = sanitize_filename(video_title)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{safe_title}_{ts}"

    txt_path = os.path.join(TRANSCRIPTS_DIR, f"{base_name}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(transcript_text)
    logger.success(f"Transcript saved: {txt_path}")

    json_path = os.path.join(TRANSCRIPTS_DIR, f"{base_name}.json")
    metadata = {
        "title": video_title,
        "language": language,
        "model": model_name,
        "timestamp": ts,
        "segments": segments,
        "transcript": transcript_text,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    cleanup_audio(audio_path)

    return {
        "text": transcript_text,
        "language": language,
        "segments": segments,
        "txt_path": txt_path,
        "json_path": json_path,
        "base_name": base_name,
    }
