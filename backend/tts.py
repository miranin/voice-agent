"""
TTS (Text-to-Speech) module.

Uses ElevenLabs API (best quality, multilingual, supports Russian).
Falls back to OpenAI TTS if ElevenLabs key is not set.

Usage:
    from backend.tts import synthesize
    audio_path = synthesize("Сегодня есть стендап в 19:00.", output_path="audio/response.mp3")
"""

import os
import logging

logger = logging.getLogger(__name__)

# ElevenLabs default voice — "Rachel" (multilingual v2, works well in Russian)
DEFAULT_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
DEFAULT_MODEL    = "eleven_multilingual_v2"


def synthesize(text: str, output_path: str) -> str:
    """
    Convert text to speech and save to file.

    Tries ElevenLabs first, falls back to OpenAI TTS.

    Args:
        text:        Text to synthesize (Russian supported).
        output_path: Where to save the MP3 file.

    Returns:
        output_path (same value, for convenience).
    """
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")

    if elevenlabs_key:
        try:
            return _synthesize_elevenlabs(text, output_path, elevenlabs_key)
        except Exception as e:
            logger.warning(f"[TTS] ElevenLabs failed: {e}. Trying OpenAI TTS.")

    return _synthesize_openai(text, output_path)


def _synthesize_elevenlabs(text: str, output_path: str, api_key: str) -> str:
    from elevenlabs.client import ElevenLabs

    client   = ElevenLabs(api_key=api_key)
    voice_id = DEFAULT_VOICE_ID
    logger.info(f"[TTS] ElevenLabs → voice={voice_id}, text={text[:60]}")

    audio_stream = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id=DEFAULT_MODEL,
        output_format="mp3_44100_128",
    )

    with open(output_path, "wb") as f:
        for chunk in audio_stream:
            if chunk:
                f.write(chunk)

    logger.info(f"[TTS] Saved to {output_path}")
    return output_path


def _synthesize_openai(text: str, output_path: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    logger.info(f"[TTS] OpenAI TTS → text={text[:60]}")

    response = client.audio.speech.create(
        model="tts-1-hd",
        voice="shimmer",    # bright, expressive, anime-like female voice
        input=text,
    )
    response.stream_to_file(output_path)
    logger.info(f"[TTS] Saved to {output_path}")
    return output_path
