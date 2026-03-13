"""
ASR (Automatic Speech Recognition) module.

Uses faster-whisper for local, fast transcription.
Falls back to OpenAI Whisper API if local model is unavailable.

Usage:
    from backend.asr import transcribe
    text = transcribe("path/to/audio.wav")
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def transcribe(audio_path: str) -> str:
    """
    Transcribe audio file to text.

    Uses OpenAI Whisper API first (most accurate for Russian/Kazakh).
    Falls back to faster-whisper if OpenAI key is missing.

    Args:
        audio_path: Path to audio file (WAV, MP3, M4A, etc.)

    Returns:
        Transcribed text string.
    """
    if os.getenv("OPENAI_API_KEY"):
        try:
            return _transcribe_openai(audio_path)
        except Exception as e:
            logger.warning(f"OpenAI Whisper failed: {e}. Falling back to local model.")
    return _transcribe_faster_whisper(audio_path)


_fw_model = None  # cached — loaded once

def _transcribe_faster_whisper(audio_path: str) -> str:
    global _fw_model
    from faster_whisper import WhisperModel

    if _fw_model is None:
        model_size = os.getenv("WHISPER_MODEL", "small")
        logger.info(f"[ASR] Loading faster-whisper model: {model_size}")
        _fw_model = WhisperModel(model_size, device="cpu", compute_type="int8")

    segments, info = _fw_model.transcribe(
        audio_path,
        language="ru",
        beam_size=5,                       # was 1 (greedy) — 5 is much more accurate
        initial_prompt=_INITIAL_PROMPT,
        condition_on_previous_text=False,
        vad_filter=True,                   # skip silent parts
    )

    text = " ".join(segment.text.strip() for segment in segments)
    logger.info(f"[ASR] Transcribed ({info.language}, {info.duration:.1f}s): {text[:80]}")
    return text.strip()


_INITIAL_PROMPT = (
    "Алматы, афиша, мероприятия, концерт, стендап, выставка, кино, билеты, "
    "Казахстан, EverJazz, Punch Stand Up Club, sxodim, ticketon, kino.kz, "
    "куда сходить, что посмотреть, когда, сегодня, завтра, в эту субботу"
)

def _transcribe_openai(audio_path: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    logger.info("[ASR] Using OpenAI Whisper API")

    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="ru",
            prompt=_INITIAL_PROMPT,   # biases Whisper toward Almaty vocabulary
        )

    text = result.text.strip()
    logger.info(f"[ASR] Transcribed: {text[:80]}")
    return text
