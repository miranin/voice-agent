"""
Text-to-Speech (TTS) using ElevenLabs API.
Requires ELEVENLABS_API_KEY in .env
"""

import os
from typing import Iterator

from dotenv import load_dotenv

load_dotenv()

# Default voice IDs from ElevenLabs (multilingual)
DEFAULT_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # Rachel - good for Russian
DEFAULT_MODEL = "eleven_multilingual_v2"


def _get_client():
    """Get ElevenLabs client."""
    from elevenlabs.client import ElevenLabs
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError(
            "ELEVENLABS_API_KEY not set. Add it to .env file."
        )
    return ElevenLabs(api_key=api_key)


def synthesize(
    text: str,
    *,
    voice_id: str = DEFAULT_VOICE_ID,
    model_id: str = DEFAULT_MODEL,
) -> bytes:
    """
    Convert text to speech audio (full response).

    Args:
        text: Text to speak
        voice_id: ElevenLabs voice ID
        model_id: Model (eleven_multilingual_v2 for Russian)

    Returns:
        Audio bytes (MP3 format)
    """
    client = _get_client()
    audio_stream = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id=model_id,
    )
    return b"".join(audio_stream)


def synthesize_stream(
    text: str,
    *,
    voice_id: str = DEFAULT_VOICE_ID,
    model_id: str = DEFAULT_MODEL,
) -> Iterator[bytes]:
    """
    Convert text to speech with streaming (lower latency).

    Yields:
        Audio chunks (MP3) as they are generated
    """
    client = _get_client()
    stream = client.text_to_speech.convert_as_stream(
        voice_id=voice_id,
        text=text,
        model_id=model_id,
    )
    yield from stream
