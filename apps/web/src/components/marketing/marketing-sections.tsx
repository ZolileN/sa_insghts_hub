import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { HeroPreview } from "./hero-preview";
import { cn } from "@/shared/utils";

export function MarketingHero({
  preview,
}: {
  preview: {
    period: string;
    kpis: { murders: number; carjackings: number; burglary: number; sexual: number };
    provinces: { province: string; murders: number }[];
  };
}) {
  return (
    <section className="relative overflow-hidden px-6 py-16 lg:px-10 lg:py-24">
      <div className="marketing-grid-bg pointer-events-none absolute inset-0" />
      <div className="relative mx-auto grid max-w-7xl gap-12 lg:grid-cols-2 lg:items-center">
        <div>
          <p className="mb-4 flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.12em] text-[var(--primary)]">
            <span className="h-px w-6 bg-[var(--primary)]" />
            South Africa&apos;s most complete data platform
          </p>
          <h1 className="text-4xl font-bold leading-[1.05] tracking-tight sm:text-5xl lg:text-6xl">
            Know SA
            <br />
            <span className="text-[var(--primary)]">before</span> you
            <br />
            decide.
          </h1>
          <p className="mt-6 max-w-lg text-base leading-relaxed text-[var(--muted-foreground)]">
            Crime, property, jobs, energy, health, education — all 10 critical data
            categories in one dashboard, live-updated and AI-powered.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button size="lg" asChild>
              <Link href="/dashboard/crime">
                Open free dashboard
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="#pricing">See Pro features</Link>
            </Button>
          </div>
          <div className="mt-12 grid grid-cols-2 gap-6 border-t border-[var(--border)] pt-8 sm:grid-cols-4">
            <StatBlock value="10×" label="data topics tracked" />
            <StatBlock value="9" label="provinces covered" />
            <StatBlock value="AI+" label="Claude analyst built in" />
            <StatBlock value="R0" label="to get started" />
          </div>
        </div>
        <div className="lg:pl-4">
          <HeroPreview
            period={preview.period}
            kpis={preview.kpis}
            provinces={preview.provinces}
          />
        </div>
      </div>
    </section>
  );
}

function StatBlock({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <p className="text-2xl font-bold tracking-tight lg:text-3xl">{value}</p>
      <p className="mt-1 font-mono text-[10px] uppercase tracking-wide text-[var(--muted-foreground)]">
        {label}
      </p>
    </div>
  );
}

export function SectionEyebrow({ children }: { children: React.ReactNode }) {
  return (
    <p className="mb-3 font-mono text-[11px] uppercase tracking-[0.12em] text-[var(--primary)]">
      {children}
    </p>
  );
}

export function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-3xl font-bold leading-tight tracking-tight sm:text-4xl lg:text-5xl">
      {children}
    </h2>
  );
}

export function AiChatMock() {
  return (
    <Card className="overflow-hidden">
      <div className="flex items-center gap-2 border-b border-[var(--border)] bg-[var(--accent)] px-4 py-3">
        <span className="h-2 w-2 rounded-full bg-[var(--primary)]" />
        <span className="font-mono text-[10px] text-[var(--muted-foreground)]">
          Libo Insights AI — Crime Statistics · Western Cape
        </span>
      </div>
      <div className="space-y-3 p-4">
        <div className="rounded-lg rounded-br-sm bg-[var(--primary)]/10 px-3 py-2 text-sm text-right">
          Which Cape Town suburb has the highest murder rate?
        </div>
        <div className="rounded-lg rounded-bl-sm border border-[var(--border)] bg-white/80 px-3 py-2 text-sm leading-relaxed dark:bg-slate-900/40">
          Based on the latest SAPS Q3 2024/25 data, <strong>Nyanga</strong> has the
          highest murder count in Cape Town at 221 cases this quarter, followed closely
          by <strong>Khayelitsha</strong> (229) and <strong>Delft</strong> (189). All
          three are on the Cape Flats. Compared to Q3 last year, Nyanga is down 9.4%
          — the largest improvement in the province.
        </div>
        <div className="rounded-lg rounded-br-sm bg-[var(--primary)]/10 px-3 py-2 text-sm text-right">
          How does WC compare to Gauteng?
        </div>
        <div className="rounded-lg rounded-bl-sm border border-[var(--border)] bg-white/80 px-3 py-2 text-sm leading-relaxed dark:bg-slate-900/40">
          Western Cape has a <strong>lower absolute murder count</strong> (1,204 vs
          Gauteng&apos;s 4,912) but a <strong>higher per-capita rate</strong> due to
          its concentrated urban density in the Cape Flats. Gauteng&apos;s murders are
          more dispersed across Johannesburg, Tshwane, and Ekurhuleni precincts.
        </div>
      </div>
      <div className="flex flex-wrap gap-2 border-t border-[var(--border)] bg-[var(--accent)]/40 p-3">
        {["Is Cape Town safer than Joburg?", "Crime trend since 2020?", "Safest suburb to buy in WC?"].map(
          (chip) => (
            <span
              key={chip}
              className="rounded-full border border-[var(--border)] bg-white/80 px-3 py-1 text-xs text-[var(--primary)] dark:bg-slate-900/50"
            >
              {chip}
            </span>
          ),
        )}
      </div>
    </Card>
  );
}

export function PricingCard({
  tier,
  price,
  priceSuffix,
  period,
  featured,
  badge,
  cta,
  href,
  primary,
  features,
}: {
  tier: string;
  price: string;
  priceSuffix?: string;
  period: string;
  featured?: boolean;
  badge?: string;
  cta: string;
  href: string;
  primary?: boolean;
  features: { text: string; included: boolean }[];
}) {
  return (
    <Card
      className={cn(
        "relative flex flex-col p-6",
        featured && "border-[var(--primary)] shadow-md ring-1 ring-[var(--primary)]/20",
      )}
    >
      {badge && (
        <Badge className="absolute -top-3 left-6" variant="default">
          {badge}
        </Badge>
      )}
      <p className="text-sm font-semibold text-[var(--muted-foreground)]">{tier}</p>
      <p className="mt-2 text-4xl font-bold tracking-tight">
        {price}
        {priceSuffix && (
          <span className="text-lg font-normal text-[var(--muted-foreground)]">
            {priceSuffix}
          </span>
        )}
      </p>
      <p className="mt-1 text-xs text-[var(--muted-foreground)]">{period}</p>
      <ul className="mt-6 flex-1 space-y-2.5 text-sm">
        {features.map((f) => (
          <li key={f.text} className="flex items-start gap-2">
            <span
              className={cn(
                "mt-0.5 shrink-0",
                f.included ? "text-[var(--success)]" : "text-[var(--muted-foreground)]",
              )}
            >
              {f.included ? "✓" : "—"}
            </span>
            <span className={cn(!f.included && "text-[var(--muted-foreground)]")}>
              {f.text}
            </span>
          </li>
        ))}
      </ul>
      <Button
        className="mt-6 w-full"
        variant={primary ? "default" : "outline"}
        asChild
      >
        <Link href={href}>{cta}</Link>
      </Button>
    </Card>
  );
}
