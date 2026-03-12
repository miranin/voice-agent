"use client";

import { useRef, useState, useEffect, useCallback } from "react";
import { Message, VoiceQueryResponse } from "@/types";
import { useVoiceRecorder } from "@/hooks/useVoiceRecorder";
import ChatMessage from "@/components/ChatMessage";
import LoadingBubble from "@/components/LoadingBubble";
import MicButton from "@/components/MicButton";
import WaveBars from "@/components/WaveBars";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

const INITIAL_MESSAGE: Message = {
  id: "init",
  role: "assistant",
  text: "Привет! Нажми на кнопку и спроси, куда сходить сегодня в Алматы 🎶",
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([INITIAL_MESSAGE]);
  const [isLoading, setIsLoading] = useState(false);
  const [transcript, setTranscript] = useState<string>("");
  const chatRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const { state, start, stop } = useVoiceRecorder();

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isLoading]);

  const sendAudio = useCallback(async (blob: Blob) => {
    setIsLoading(true);
    try {
      const form = new FormData();
      form.append("audio", blob, "recording.webm");

      const res = await fetch(`${BACKEND_URL}/voice-query`, {
        method: "POST",
        body: form,
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      const data: VoiceQueryResponse = await res.json();

      setTranscript(data.transcript);

      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "user", text: data.transcript },
        { id: crypto.randomUUID(), role: "assistant", text: data.response_text },
      ]);

      // Play audio response
      if (data.audio_url) {
        if (audioRef.current) audioRef.current.pause();
        audioRef.current = new Audio(`${BACKEND_URL}${data.audio_url}`);
        audioRef.current.play();
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          text: "Что-то пошло не так. Попробуй ещё раз.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleMicClick = useCallback(async () => {
    if (state === "recording") {
      const blob = await stop();
      if (blob) await sendAudio(blob);
    } else if (state === "idle") {
      setTranscript("");
      await start();
    }
  }, [state, start, stop, sendAudio]);

  return (
    <div className="w-full max-w-[600px] h-dvh flex flex-col px-4">
      {/* Header */}
      <header className="flex-shrink-0 py-6 text-center">
        <h1 className="text-xl font-bold tracking-tight">🎙 Голосовой помощник</h1>
        <p className="text-sm text-[--text-muted] mt-1">Спроси, куда сходить в Алматы</p>
      </header>

      {/* Chat */}
      <div
        ref={chatRef}
        className="flex-1 overflow-y-auto flex flex-col gap-3 pb-4 scrollbar-thin"
      >
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        {isLoading && <LoadingBubble />}
      </div>

      {/* Controls */}
      <div className="flex-shrink-0 pb-8 flex flex-col items-center gap-4">
        {transcript && (
          <div className="w-full bg-[--surface] border border-[--border] rounded-xl px-4 py-2.5 text-sm">
            <span className="text-[--text-muted] font-semibold mr-1.5">Вы сказали:</span>
            <span>{transcript}</span>
          </div>
        )}

        <MicButton state={state} onClick={handleMicClick} />

        {state === "recording" && <WaveBars />}
      </div>
    </div>
  );
}
