"""
Speech-to-Text (ASR) using faster-whisper.
Local model, no API key required.
"""

from pathlib import Path
from typing import Optional

# Lazy load model on first use
_model = None


def _get_model(model_size: str = "small"):
    """Load faster-whisper model (lazy singleton)."""
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel(model_size, device="auto", compute_type="auto")
    return _model


def transcribe(
    audio_path: str | Path,
    *,
    language: Optional[str] = "ru",
    model_size: str = "small",
    beam_size: int = 5,
    temperature: float = 0.0,
    condition_on_previous_text: bool = True,
) -> str:
    """
    Transcribe audio file to text.

    Args:
        audio_path: Path to audio file (wav, mp3, etc.)
        language: Language code (ru, en, etc.). None = auto-detect
        model_size: faster-whisper model (tiny, base, small, medium, large-v3)
        beam_size: 5 default, 1 = greedy (faster, slightly worse)
        temperature: 0.0 for best accuracy
        condition_on_previous_text: False if model repeats on long audio

    Returns:
        Transcribed text
    """
    model = _get_model(model_size)
    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=beam_size,
        temperature=temperature,
        condition_on_previous_text=condition_on_previous_text,
    )
    return " ".join(s.text.strip() for s in segments).strip()


def transcribe_bytes(
    audio_bytes: bytes,
    *,
    language: Optional[str] = "ru",
    model_size: str = "small",
    beam_size: int = 5,
    temperature: float = 0.0,
    file_suffix: str = ".webm",  # webm = typical browser MediaRecorder output
) -> str:
    """Transcribe audio from bytes (saves to temp file for faster-whisper)."""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=file_suffix, delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name
    try:
        return transcribe(
            tmp_path,
            language=language,
            model_size=model_size,
            beam_size=beam_size,
            temperature=temperature,
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)
