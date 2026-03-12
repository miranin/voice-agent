"""Voice module: ASR (Speech-to-Text) and TTS (Text-to-Speech)."""

from .asr import transcribe
from .tts import synthesize

__all__ = ["transcribe", "synthesize"]
