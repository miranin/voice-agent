"""
Backend server — Voice AI Event Assistant.

Endpoints:
    POST /voice-query   — main pipeline: audio → ASR → Agent → TTS → audio
    GET  /health        — health check

Run:
    uvicorn backend.main:app --reload --port 8000
"""

import os
import uuid
import base64
import logging
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# --- App setup -----------------------------------------------------------

app = FastAPI(title="Voice AI Event Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated audio files at /audio/<filename>
AUDIO_DIR = Path(__file__).parent / "audio"
AUDIO_DIR.mkdir(exist_ok=True)
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

# --- Lazy imports (heavy models load once on first request) --------------

_asr = None
_tts = None
_agent = None

def get_asr():
    global _asr
    if _asr is None:
        from backend.asr import transcribe
        _asr = transcribe
    return _asr

def get_tts():
    global _tts
    if _tts is None:
        from backend.tts import synthesize
        _tts = synthesize
    return _tts

def get_agent():
    global _agent
    if _agent is None:
        from agent.agent import run_agent
        _agent = run_agent
    return _agent

# --- Endpoints -----------------------------------------------------------

def _strip_markdown(text: str) -> str:
    """Remove markdown so TTS doesn't read ** or [link](url) aloud."""
    import re
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)          # **bold**
    text = re.sub(r'\*(.+?)\*', r'\1', text)               # *italic*
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # [text](url)
    text = re.sub(r'#+\s', '', text)                        # ## headings
    text = re.sub(r'`(.+?)`', r'\1', text)                 # `code`
    return text.strip()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "voice-ai-backend"}


@app.post("/voice-query")
async def voice_query(audio: UploadFile = File(...)):
    """
    Full pipeline: audio → transcript → agent response → TTS audio.

    Request:  multipart/form-data, field name = "audio"
    Response:
        {
            "transcript":    "Куда сходить сегодня вечером?",
            "response_text": "Сегодня есть стендап в 19:00...",
            "audio_url":     "/audio/abc123.mp3",
            "sources":       [{"title": "...", "url": "..."}]
        }
    """
    request_id = uuid.uuid4().hex[:8]
    logger.info(f"[{request_id}] New voice query — file={audio.filename}, type={audio.content_type}")

    # 1. Save incoming audio to a temp file
    suffix = Path(audio.filename).suffix if audio.filename else ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    try:
        # 2. ASR — audio → text
        logger.info(f"[{request_id}] Running ASR...")
        transcript = get_asr()(tmp_path)
        if not transcript:
            raise HTTPException(status_code=422, detail="Could not transcribe audio. Please speak more clearly.")
        logger.info(f"[{request_id}] Transcript: {transcript}")

        # 3. Agent — text → response
        logger.info(f"[{request_id}] Running agent...")
        agent_result = get_agent()(transcript)
        response_text = agent_result.get("response_text", "")
        sources       = agent_result.get("sources", [])
        logger.info(f"[{request_id}] Response: {response_text[:80]}")

        # 4. TTS — response text → audio file (strip markdown first)
        response_text = _strip_markdown(response_text)
        logger.info(f"[{request_id}] Running TTS...")
        audio_filename = f"{request_id}.mp3"
        audio_path     = str(AUDIO_DIR / audio_filename)
        get_tts()(response_text, audio_path)

        # Encode audio as base64 — avoids all CORS/autoplay issues in browser
        with open(audio_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("utf-8")

        logger.info(f"[{request_id}] Done. Audio encoded as base64.")

        return JSONResponse({
            "transcript":    transcript,
            "response_text": response_text,
            "audio_b64":     audio_b64,
            "sources":       sources,
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Pipeline error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
    finally:
        # Clean up temp audio input file
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@app.on_event("startup")
async def startup():
    logger.info("Backend started. Audio dir: %s", AUDIO_DIR)
    logger.info("OPENAI_API_KEY:     %s", "set" if os.getenv("OPENAI_API_KEY") else "NOT SET")
    logger.info("ELEVENLABS_API_KEY: %s", "set" if os.getenv("ELEVENLABS_API_KEY") else "NOT SET")
