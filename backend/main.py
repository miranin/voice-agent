"""
FastAPI backend for Voice AI Event Assistant.
Orchestrates: ASR -> Agent -> TTS
"""
import os
import uuid
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# Voice module (ASR + TTS)
try:
    from backend.voice.asr import transcribe_bytes as transcribe_audio
    from backend.voice.tts import synthesize as text_to_speech
    VOICE_AVAILABLE = True
except ImportError as e:
    VOICE_AVAILABLE = False
    _import_error = str(e)

load_dotenv()

app = FastAPI(title="Voice AI Event Assistant", version="0.1.0")

# Temp dir for audio responses
AUDIO_DIR = Path("audio_cache")
AUDIO_DIR.mkdir(exist_ok=True)


def get_agent_response(text: str) -> str:
    """
    Placeholder for LangChain agent.
    AI Engineer will replace this with real agent call.
    """
    # Mock response until agent module is ready
    return (
        f"Вы сказали: «{text}». "
        "Я пока работаю в режиме заглушки — агент с поиском событий будет подключён позже."
    )


@app.get("/")
def root():
    return {"status": "ok", "message": "Voice AI Event Assistant API"}


@app.post("/voice-query")
async def voice_query(audio: UploadFile = File(...)):
    """
    Full pipeline: Audio -> ASR -> Agent -> TTS -> Audio
    Accepts: multipart/form-data with 'audio' file (wav, mp3, webm)
    Returns: transcript, response_text, audio file
    """
    if not VOICE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail=f"Voice module not loaded: {_import_error}. Install deps: pip install -r requirements.txt"
        )

    # 1. ASR
    content = await audio.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty audio file")

    transcript = transcribe_audio(content)
    if not transcript.strip():
        raise HTTPException(status_code=400, detail="Could not transcribe audio")

    # 2. Agent (placeholder)
    response_text = get_agent_response(transcript)

    # 3. TTS
    try:
        audio_bytes = text_to_speech(response_text)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    if not audio_bytes:
        raise HTTPException(
            status_code=503,
            detail="TTS failed. Check ELEVENLABS_API_KEY in .env"
        )

    # Save and return
    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = AUDIO_DIR / filename
    filepath.write_bytes(audio_bytes)

    return FileResponse(
        filepath,
        media_type="audio/mpeg",
        headers={
            "X-Transcript": transcript,
            "X-Response-Text": response_text,
        },
    )


@app.post("/api/voice-query")
async def api_voice_query(audio: UploadFile = File(...)):
    """
    JSON + audio: returns transcript, response_text, audio_url
    For frontend that needs structured response.
    """
    if not VOICE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail=f"Voice module not loaded: {_import_error}"
        )

    content = await audio.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty audio file")

    transcript = transcribe_audio(content)
    if not transcript.strip():
        raise HTTPException(status_code=400, detail="Could not transcribe audio")

    response_text = get_agent_response(transcript)
    try:
        audio_bytes = text_to_speech(response_text)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    if not audio_bytes:
        raise HTTPException(status_code=503, detail="TTS failed")

    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = AUDIO_DIR / filename
    filepath.write_bytes(audio_bytes)

    return {
        "transcript": transcript,
        "response_text": response_text,
        "audio_url": f"/audio/{filename}",
    }


@app.get("/audio/{filename}")
def get_audio(filename: str):
    """Serve cached audio file."""
    filepath = AUDIO_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Audio not found")
    return FileResponse(filepath, media_type="audio/mpeg")
