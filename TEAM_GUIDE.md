# 🎙 Voice AI Event Assistant — Team Guide

This repository contains a **team project (3-4 members)** to build a **Voice AI Assistant** that helps users find events in **Almaty**.

The assistant listens to the user's voice, searches event websites using MCP Playwright, and responds with voice.

**Example interaction:**

> User: "Привет! Куда можно сходить сегодня вечером в Алматы? Желательно на концерт или стендап."
>
> Assistant: "Сегодня вечером есть классный стендап на Абая в 19:00 и джазовый концерт в 20:00. Куда бы ты хотел?"

---

## 🧠 System Architecture

Full pipeline:

```
Frontend (Voice UI)
        ↓
Backend (FastAPI)
        ↓
ASR (Speech-to-Text)
        ↓
LangChain Agent
        ↓
MCP Playwright (Web Search)
        ↓
TTS (Text-to-Speech)
        ↓
Audio Response
```

---

## 👥 Team Structure (4 Members)

Each team member is responsible for **one module**.

| Role | Responsibility |
|------|----------------|
| Frontend Engineer | Voice UI |
| Backend Engineer | API + pipeline |
| AI Engineer | LangChain Agent |
| Automation Engineer | MCP Playwright scraping |

---

## 📁 Project Structure

```
voice-agent/
├── frontend/
├── backend/
├── agent/
├── mcp_tools/
├── README.md
└── TEAM_GUIDE.md
```

---

## 🔧 Step 1 — Clone the Repository

```bash
git clone https://github.com/miranin/voice-agent.git
cd voice-agent
```

---

## 🔧 Step 2 — Create Python Environment

```bash
python -m venv venv
```

Activate:

**Mac / Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

---

## 🔧 Step 3 — Install Dependencies

```bash
pip install fastapi uvicorn openai langchain faster-whisper elevenlabs playwright python-dotenv
```

Install ElevenLabs SDK separately (latest version):

```bash
pip install elevenlabs
```

Install Playwright browser:

```bash
playwright install chromium
```

---

## 🔑 Step 4 — Setup API Keys

Create a `.env` file in the root:

```env
OPENAI_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
```

---

## 🎤 Speech Recognition (ASR)

### Cloud APIs
- OpenAI Whisper API
- Google Speech-to-Text
- AssemblyAI

### Local Models (recommended)

| Model | Notes |
|-------|-------|
| [faster-whisper-small](https://huggingface.co/Systran/faster-whisper-small) | Fastest, lowest memory — good starting point |
| [whisper-large-v3-turbo](https://huggingface.co/openai/whisper-large-v3-turbo) | Best accuracy, optimized speed |
| [nvidia/parakeet-tdt-0.6b-v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) | Great performance/speed ratio |

**Recommended for this project:** `faster-whisper-small`

### ASR Hyperparameter Tips (Whisper-based)

- **`beam_size`** — default `5`. Set to `1` (greedy) for faster inference with slight quality tradeoff.
- **`temperature`** — use `0.0` for best accuracy. If the model hallucinates or loops, try `[0.0, 0.2, 0.4]`.
- **`condition_on_previous_text`** — set to `False` if the model repeats itself on long audio. Slightly less context but more stable.

---

## 🔊 Text to Speech (TTS)

### Cloud APIs (recommended)

- **ElevenLabs API** — best voice quality, supports streaming with minimal latency
- OpenAI TTS

### ElevenLabs Quick Setup

```python
from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key="your_key_here")

audio = client.text_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",  # default voice
    text="Сегодня есть стендап в 19:00.",
    model_id="eleven_multilingual_v2",
)

with open("response.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### Local / Open-Source Models

| Model | Notes |
|-------|-------|
| [Fish Speech (fishaudio/s2-pro)](https://huggingface.co/fishaudio/s2-pro) | Excellent quality, voice cloning |
| [XTTS-v2](https://huggingface.co/coqui/XTTS-v2) | Russian + English, voice cloning, streaming |
| [suno/bark](https://huggingface.co/suno/bark) | Expressive, GPU-heavy |

---

## 🌐 Event Websites

The agent should search events from:

- https://sxodim.com/almaty
- https://ticketon.kz
- https://kino.kz

Automation engineer configures which sites the agent uses based on user queries.

---

## 👨‍💻 Task Distribution

### Frontend Engineer

**Folder:** `frontend/`

**Tasks:**
- Microphone recording (Web Audio API)
- Send audio to backend
- Display transcript in real-time
- Play assistant audio response
- Show chat messages and loading animation

**Tech:** React / Vue / Vanilla JS, Web Audio API

---

### Backend Engineer

**Folder:** `backend/`

**Tasks:**
- Create FastAPI server
- Receive audio from frontend
- Call ASR service (transcribe audio → text)
- Call AI agent with transcribed text
- Call TTS service (response text → audio)
- Return audio response to frontend

**Example endpoint:** `POST /voice-query`

**Response format:**
```json
{
  "transcript": "Куда сходить сегодня вечером?",
  "response_text": "Сегодня есть стендап в 19:00...",
  "audio_url": "/audio/response.mp3"
}
```

---

### AI Engineer

**Folder:** `agent/`

**Tasks:**
- Build LangChain agent
- Write system prompt (agent knows about Almaty event sites)
- Process user queries and decide when to use web tools
- Call MCP Playwright tools when event search is needed
- Return structured response

**Example query:** "Куда можно сходить сегодня вечером?"

The agent should autonomously decide to use Playwright to search relevant sites.

---

### Web Automation Engineer

**Folder:** `mcp_tools/`

**Tasks:**
- Set up MCP Playwright server
- Build scrapers for each event site
- Extract event title, time, location, URL
- Return structured JSON to agent

**Example output:**
```json
[
  {
    "title": "Standup Show",
    "time": "19:00",
    "location": "Almaty Arena",
    "url": "https://sxodim.com/almaty/..."
  }
]
```

---

## 🔄 Development Workflow

Each team member works in their own branch.

```bash
# Create your branch
git checkout -b feature/your-module

# Commit your work
git add .
git commit -m "feat: implement ASR module"

# Push and open a Pull Request
git push origin feature/your-module
```

Then open a Pull Request on GitHub for review.

---

## 🎯 Definition of Done

| Criterion | Description |
|-----------|-------------|
| ✅ End-to-end flow | User speaks → gets voice response |
| ✅ MCP Playwright | Agent searches real event sites |
| ✅ Audio quality | ASR transcribes correctly, TTS sounds natural |
| ✅ Code structure | Backend/Frontend separated, API is clean |
| ✅ Team Git usage | Branches, commits, and PRs from all members |

---

## 🌟 Bonus Tasks (Advanced)

### 1. Real-time ASR via WebSocket

Run `faster-whisper-small` locally and stream audio chunks from frontend to backend via **WebSocket**. Show transcription on screen while the user is still speaking.

### 2. Streaming TTS

Use **ElevenLabs Streaming API** (or XTTS-v2 / Fish Speech stream) so the assistant starts playing audio before the full response is generated — dramatically reduces perceived latency.

```python
# ElevenLabs streaming example
audio_stream = client.text_to_speech.convert_as_stream(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    text="Сегодня есть стендап в 19:00...",
    model_id="eleven_multilingual_v2",
)
```

---

## 🚀 Final Demo Flow

1. User opens the website
2. Clicks the microphone button
3. Says: *"Куда можно сходить сегодня вечером в Алматы?"*
4. System transcribes speech → sends to agent → agent searches sxodim.com
5. Agent responds: *"Сегодня есть стендап в 19:00 и джазовый концерт в 20:00."*
6. Response plays as voice, text shown in chat UI
