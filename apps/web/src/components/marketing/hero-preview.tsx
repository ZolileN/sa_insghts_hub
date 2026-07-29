import { Card } from "@/components/ui/card";
import { cn } from "@/shared/utils";

type ProvinceMurder = { province: string; murders: number };

export function HeroPreview({
  period,
  kpis,
  provinces,
}: {
  period: string;
  kpis: {
    murders: number;
    carjackings: number;
    burglary: number;
    sexual: number;
  };
  provinces: ProvinceMurder[];
}) {
  const maxMurders = Math.max(...provinces.map((p) => p.murders), 1);
  const top4 = [...provinces]
    .sort((a, b) => b.murders - a.murders)
    .slice(0, 4);

  return (
    <Card className="overflow-hidden shadow-lg">
      <div className="flex items-center gap-2 border-b border-[var(--border)] bg-[var(--accent)] px-4 py-2.5">
        <span className="h-2.5 w-2.5 rounded-full bg-red-400" />
        <span className="h-2.5 w-2.5 rounded-full bg-amber-400" />
        <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />
        <span className="ml-2 font-mono text-[10px] uppercase tracking-wide text-[var(--muted-foreground)]">
          Libo Insights — Crime Statistics
        </span>
      </div>
      <div className="p-4">
        <div className="grid grid-cols-2 gap-2">
          <PreviewKpi label={`Murders (${period})`} value={kpis.murders.toLocaleString()} delta="▼ 8.7% YoY" positive />
          <PreviewKpi label="Carjackings" value={kpis.carjackings.toLocaleString()} delta="▲ 2.1% YoY" />
          <PreviewKpi label="Residential Burglary" value={kpis.burglary.toLocaleString()} delta="▼ 3.4% YoY" positive />
          <PreviewKpi label="Sexual Offences" value={kpis.sexual.toLocaleString()} delta="▼ 1.2% YoY" positive />
        </div>
        <div className="mt-3 rounded-lg border border-[var(--border)] bg-[var(--accent)]/50 p-3">
          <p className="mb-3 font-mono text-[9px] uppercase tracking-wider text-[var(--muted-foreground)]">
            Murder rate by province
          </p>
          {top4.map((p) => (
            <div key={p.province} className="mb-2 flex items-center gap-2 last:mb-0">
              <span className="w-20 shrink-0 text-right font-mono text-[9px] text-[var(--muted-foreground)]">
                {p.province.replace("KwaZulu-Natal", "KZN").replace("Western Cape", "WC").replace("Eastern Cape", "EC").replace("Gauteng", "GP")}
              </span>
              <div className="h-2 flex-1 overflow-hidden rounded bg-white/80">
                <div
                  className={cn(
                    "h-full rounded",
                    p.province === "Western Cape" ? "bg-emerald-500" : "bg-gradient-to-r from-red-500 to-orange-500",
                  )}
                  style={{ width: `${(p.murders / maxMurders) * 100}%` }}
                />
              </div>
              <span className="w-10 font-mono text-[9px] tabular-nums">{p.murders.toLocaleString()}</span>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}

function PreviewKpi({
  label,
  value,
  delta,
  positive,
}: {
  label: string;
  value: string;
  delta: string;
  positive?: boolean;
}) {
  return (
    <div className="rounded-lg border border-[var(--border)] bg-white/70 p-2.5 dark:bg-slate-900/30">
      <p className="font-mono text-[8px] uppercase tracking-wide text-[var(--muted-foreground)]">{label}</p>
      <p className="mt-0.5 text-lg font-semibold tabular-nums">{value}</p>
      <p
        className={cn(
          "mt-0.5 font-mono text-[8px]",
          positive ? "text-[var(--success)]" : "text-[var(--destructive)]",
        )}
      >
        {delta}
      </p>
    </div>
  );
}
