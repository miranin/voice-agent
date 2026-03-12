# 🎙 Voice AI Event Assistant — Team Guide

This repository contains a **team project (4 members)** to build a **Voice AI Assistant** that helps users find events in **Almaty**.

The assistant will listen to a user's voice, search event websites, and respond with voice.

**Example interaction:**

> User: "Куда можно сходить сегодня вечером в Алматы?"
>
> Assistant: "Сегодня есть стендап в 19:00 и джаз концерт в 20:00."

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
| Automation Engineer | Playwright scraping |

---

## 📁 Project Structure

After cloning, the project should look like this:

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

Activate environment:

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
pip install fastapi uvicorn openai langchain playwright faster-whisper elevenlabs
```

Install Playwright browser:

```bash
playwright install
```

---

## 🔑 Step 4 — Setup API Keys

Create a file called `.env` and add:

```env
OPENAI_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
```

---

## 🎤 Speech Recognition (ASR)

Possible options:
- Whisper
- Faster-Whisper
- OpenAI Whisper API

**Recommended:** `faster-whisper` (fast and lightweight)

---

## 🔊 Text to Speech (TTS)

We will use **ElevenLabs API**.

Documentation: https://elevenlabs.io/docs

---

## 🌐 Event Websites

The assistant should search events from:

- https://sxodim.com
- https://ticketon.kz
- https://kino.kz

Automation engineer will implement scrapers.

---

## 👨‍💻 Task Distribution

### Frontend Engineer

**Folder:** `frontend/`

**Tasks:**
- Microphone recording
- Send audio to backend
- Display transcript
- Play assistant audio
- Display chat messages

**Tech:** React / Next.js, Web Audio API

---

### Backend Engineer

**Folder:** `backend/`

**Tasks:**
- Create FastAPI server
- Receive audio from frontend
- Call ASR service
- Call AI agent
- Call TTS service
- Return response

**Example endpoint:** `POST /voice-query`

**Response format:**
```json
{
  "transcript": "...",
  "response_text": "...",
  "audio_url": "..."
}
```

---

### AI Engineer

**Folder:** `agent/`

**Tasks:**
- Build LangChain agent
- Write system prompt
- Process user requests
- Call automation tools when needed

**Example query:** "Куда можно сходить сегодня?"

The agent should generate helpful recommendations.

---

### Web Automation Engineer

**Folder:** `mcp_tools/`

**Tasks:**
- Build Playwright scrapers
- Open event websites
- Extract event information
- Return structured JSON

**Example output:**
```json
[
  {
    "title": "Standup Show",
    "time": "19:00",
    "location": "Almaty Arena"
  }
]
```

---

## 🔄 Development Workflow

Each team member should work in their own branch.

**Create branch:**
```bash
git checkout -b feature/my-module
```

**Commit changes:**
```bash
git add .
git commit -m "implement feature"
```

**Push changes:**
```bash
git push origin feature/my-module
```

Then open a **Pull Request**.

---

## 🎯 Definition of Done

The project is complete when:

- ✔ User can speak to the assistant
- ✔ Speech converts to text
- ✔ AI agent understands request
- ✔ Agent searches event websites
- ✔ Response generated
- ✔ Response returned as voice
- ✔ UI displays conversation

---

## 🚀 Final Demo

1. User opens the website
2. Clicks the microphone
3. User says: *"Куда можно сходить сегодня вечером?"*
4. Assistant responds with voice: *"Сегодня есть стендап в 19:00 и концерт в 20:00."*
