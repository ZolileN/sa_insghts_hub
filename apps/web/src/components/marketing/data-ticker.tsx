import { cn } from "@/shared/utils";

export type TickerItem = {
  label: string;
  value: string;
  delta?: string;
  tone?: "up" | "down" | "neutral";
};

export function DataTicker({ items }: { items: TickerItem[] }) {
  const track = [...items, ...items];

  return (
    <div className="border-b border-[var(--border)] bg-white/60 backdrop-blur-md dark:bg-slate-900/40">
      <div className="marketing-ticker overflow-hidden py-2">
        <div className="marketing-ticker-track flex">
          {track.map((item, i) => (
            <div
              key={`${item.label}-${i}`}
              className="flex shrink-0 items-center gap-2 border-r border-[var(--border)] px-8 text-xs"
            >
              <span className="text-[var(--muted-foreground)]">{item.label}</span>
              <span className="font-mono font-medium tabular-nums text-[var(--foreground)]">
                {item.value}
              </span>
              {item.delta && (
                <span
                  className={cn(
                    "font-mono text-[10px]",
                    item.tone === "up" && "text-[var(--success)]",
                    item.tone === "down" && "text-[var(--destructive)]",
                    item.tone === "neutral" && "text-[var(--muted-foreground)]",
                  )}
                >
                  {item.delta}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
