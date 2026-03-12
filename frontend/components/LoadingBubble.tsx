export default function LoadingBubble() {
  return (
    <div className="flex justify-start">
      <div className="bg-[--surface] border border-[--border] rounded-[18px] rounded-bl-[4px] px-4 py-3">
        <div className="flex items-center gap-1">
          <span className="loading-dot w-1.5 h-1.5 rounded-full bg-[--text-muted] inline-block" />
          <span className="loading-dot w-1.5 h-1.5 rounded-full bg-[--text-muted] inline-block" />
          <span className="loading-dot w-1.5 h-1.5 rounded-full bg-[--text-muted] inline-block" />
        </div>
      </div>
    </div>
  );
}
