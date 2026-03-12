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

    Tries faster-whisper first (local, free).
    Falls back to OpenAI Whisper API if not installed.

    Args:
        audio_path: Path to audio file (WAV, MP3, M4A, etc.)

    Returns:
        Transcribed text string.
    """
    try:
        return _transcribe_faster_whisper(audio_path)
    except ImportError:
        logger.warning("faster-whisper not installed, falling back to OpenAI Whisper API")
        return _transcribe_openai(audio_path)


def _transcribe_faster_whisper(audio_path: str) -> str:
    from faster_whisper import WhisperModel

    model_size = os.getenv("WHISPER_MODEL", "small")
    logger.info(f"[ASR] Loading faster-whisper model: {model_size}")

    model = WhisperModel(
        model_size,
        device="cpu",
        compute_type="int8",      # memory-efficient
    )

    segments, info = model.transcribe(
        audio_path,
        language="ru",            # Russian — change to None for auto-detect
        beam_size=1,              # fast (greedy), increase to 5 for better accuracy
        condition_on_previous_text=False,  # prevents looping on silence
    )

    text = " ".join(segment.text.strip() for segment in segments)
    logger.info(f"[ASR] Transcribed ({info.language}, {info.duration:.1f}s): {text[:80]}")
    return text.strip()


def _transcribe_openai(audio_path: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    logger.info("[ASR] Using OpenAI Whisper API")

    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="ru",
        )

    text = result.text.strip()
    logger.info(f"[ASR] Transcribed: {text[:80]}")
    return text
