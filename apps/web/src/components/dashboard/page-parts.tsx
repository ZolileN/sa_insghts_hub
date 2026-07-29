import { Card } from "@/components/ui/card";
import { formatDataAsOf } from "@/shared/data/display";
import { cn } from "@/shared/utils";

interface PageHeaderProps {
  title: string;
  description?: string;
  children?: React.ReactNode;
}

export function PageHeader({ title, description, children }: PageHeaderProps) {
  return (
    <div className="page-heading-row mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-[var(--foreground)]">
          {title}
        </h1>
        {description && (
          <p className="mt-1 max-w-2xl text-sm text-[var(--muted-foreground)]">
            {description}
          </p>
        )}
      </div>
      {children && (
        <div className="flex shrink-0 items-center gap-3">{children}</div>
      )}
    </div>
  );
}

interface KpiCardProps {
  label: string;
  value: string;
  hint?: string;
  trend?: string;
  trendPositive?: boolean;
  className?: string;
}

export function KpiCard({
  label,
  value,
  hint,
  trend,
  trendPositive,
  className,
}: KpiCardProps) {
  return (
    <Card className={cn("p-4", className)}>
      <p className="text-xs font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
        {label}
      </p>
      <p className="mt-2 text-2xl font-semibold tabular-nums tracking-tight">
        {value}
      </p>
      {hint && (
        <p className="mt-1 text-xs text-[var(--muted-foreground)]">{hint}</p>
      )}
      {trend && (
        <p
          className={cn(
            "mt-2 text-xs font-medium",
            trendPositive ? "text-[var(--success)]" : "text-[var(--destructive)]",
          )}
        >
          {trend}
        </p>
      )}
    </Card>
  );
}

interface SourceBadgeProps {
  source: string;
  scrapedAt?: string | null;
  /** Kept for API compatibility; no longer shown in the footer. */
  isLive?: boolean;
}

export function SourceBadge({ source, scrapedAt, isLive }: SourceBadgeProps) {
  const refreshed = formatDataAsOf(scrapedAt, "");

  return (
    <div className="mt-6 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-[var(--muted-foreground)]">
      <span>Sources: {source}</span>
      {refreshed && <span>· Updated {refreshed}</span>}
    </div>
  );
}

export function ChartPanel({
  title,
  description,
  children,
  className,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <Card className={cn("overflow-hidden", className)}>
      <div className="border-b border-[var(--border)] px-5 py-4">
        <h3 className="text-sm font-semibold">{title}</h3>
        {description && (
          <p className="mt-0.5 text-xs text-[var(--muted-foreground)]">
            {description}
          </p>
        )}
      </div>
      <div className="p-4 pt-2">{children}</div>
    </Card>
  );
}
