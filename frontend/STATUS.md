# Frontend Engineer Status

## Last Updated
2026-03-12

## Current Status
[x] Done — Next.js 15 + TypeScript + Tailwind

## UI Components
- `app/page.tsx` — главная страница, управление состоянием
- `components/ChatMessage.tsx` — пузырь сообщения (user/assistant) с источниками
- `components/LoadingBubble.tsx` — анимация ожидания ответа
- `components/MicButton.tsx` — кнопка микрофона (idle / recording / loading)
- `components/WaveBars.tsx` — анимация звуковых волн во время записи
- `hooks/useVoiceRecorder.ts` — Web Audio API хук (start/stop, возвращает Blob)
- `types/index.ts` — типы Message, Source, VoiceQueryResponse

## API Calls Made

```
POST /voice-query
Content-Type: multipart/form-data
Body: { audio: Blob (audio/webm) }

Response:
{
  "transcript": string,
  "response_text": string,
  "audio_url": string   // путь вида /audio/response.mp3
}
```

Backend URL задаётся через `NEXT_PUBLIC_BACKEND_URL` в `.env.local` (default: `http://localhost:8000`).

## How to Run

```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
```

## What I Need from Backend Engineer
- Endpoint `POST /voice-query` с multipart/form-data
- CORS разрешить `http://localhost:3000`
- `audio_url` должен быть доступен как статика: `GET /audio/response.mp3`

## Done
- [x] Next.js 15 + TypeScript + Tailwind проект
- [x] Web Audio API запись голоса (useVoiceRecorder hook)
- [x] Отправка аудио на backend (FormData)
- [x] Чат UI с сообщениями пользователя и ассистента
- [x] Проигрывание аудио-ответа
- [x] Анимации: wave bars при записи, loading dots при ожидании
- [x] Transcript box — показывает что распознал backend
- [x] Билд проходит без ошибок
