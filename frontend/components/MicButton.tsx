import { RecorderState } from "@/hooks/useVoiceRecorder";

interface MicButtonProps {
  state: RecorderState;
  onClick: () => void;
}

const MicIcon = () => (
  <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
    <line x1="12" y1="19" x2="12" y2="23" />
    <line x1="8" y1="23" x2="16" y2="23" />
  </svg>
);

const labels: Record<RecorderState, string> = {
  idle: "Нажми и говори",
  recording: "Говори...",
  loading: "Обработка...",
};

export default function MicButton({ state, onClick }: MicButtonProps) {
  const isRecording = state === "recording";
  const isLoading = state === "loading";

  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      aria-label={labels[state]}
      className={[
        "w-20 h-20 rounded-full flex flex-col items-center justify-center gap-1",
        "border-2 transition-all duration-200 active:scale-95",
        "disabled:opacity-50 disabled:cursor-not-allowed",
        isRecording
          ? "bg-red-500 border-red-500 mic-recording text-white"
          : "bg-[--surface] border-[--border] text-[--text] hover:border-[--accent]",
      ].join(" ")}
    >
      <MicIcon />
      <span className="text-[10px] uppercase tracking-wider text-[--text-muted]">
        {labels[state]}
      </span>
    </button>
  );
}
