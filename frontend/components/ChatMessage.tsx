import { Message } from "@/types";

export default function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[82%] rounded-[18px] px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
          isUser
            ? "bg-[--accent] text-white rounded-br-[4px]"
            : "bg-[--surface] border border-[--border] text-[--text] rounded-bl-[4px]"
        }`}
      >
        {message.text}

        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 flex flex-col gap-1">
            {message.sources.map((s, i) => (
              <a
                key={i}
                href={s.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-[--accent] opacity-80 hover:opacity-100 hover:underline truncate"
              >
                {s.title}
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
