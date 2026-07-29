import Link from "next/link";
import { MarketingNav } from "@/components/marketing/marketing-nav";
import { DataTicker, type TickerItem } from "@/components/marketing/data-ticker";
import {
  AiChatMock,
  MarketingFooter,
  MarketingHero,
  PricingCard,
  SectionEyebrow,
  SectionTitle,
} from "@/components/marketing/marketing-sections";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { loadJson } from "@/shared/data/load";
import { PROVINCE_LIST } from "@/shared/data/constants";
import {
  AUDIENCE,
  AI_FEATURES,
  PRICING_PLANS,
  TOPIC_MARKETING,
} from "@/shared/marketing/content";

export default async function HomePage() {
  const [forex, finance, employment, education, water, energy, crime] =
    await Promise.all([
      loadJson<{ live_rates?: { usd_zar?: number }; is_live?: boolean }>("forex"),
      loadJson<{ repo_rate_pct?: number; cpi_headline_pct?: number }>("finance"),
      loadJson<{ unemployment_rate_pct?: number }>("employment"),
      loadJson<{ national_pass_rate_pct?: number }>("education"),
      loadJson<{ national_avg_pct?: number }>("water"),
      loadJson<{ stage_label?: string; current_stage?: number }>("energy"),
      loadJson<{
        period?: string;
        national_totals?: Record<string, number>;
        provinces?: Record<string, Record<string, number>>;
      }>("crime"),
    ]);

  const usdZar = forex?.live_rates?.usd_zar ?? 18.64;
  const repo = finance?.repo_rate_pct ?? 6.75;
  const unemployment = employment?.unemployment_rate_pct ?? 32.9;
  const matric = education?.national_pass_rate_pct ?? 87.3;
  const dams = water?.national_avg_pct ?? 78.4;
  const cpi = finance?.cpi_headline_pct ?? 3.5;
  const stageLabel = energy?.stage_label ?? "Stage 0";

  const tickerItems: TickerItem[] = [
    { label: "USD/ZAR", value: `R${usdZar.toFixed(2)}`, delta: "▼ 0.3%", tone: "down" },
    { label: "Repo Rate", value: `${repo}%`, delta: "▲ cut", tone: "up" },
    { label: "Murders 2024/25 Q3", value: "-8.7%", delta: "▼ YoY", tone: "up" },
    { label: "Dam Levels", value: `${dams}%`, delta: "▲ 12pp", tone: "up" },
    { label: "Load Shedding", value: stageLabel, delta: energy?.current_stage === 0 ? "✓ clear" : "", tone: "up" },
    { label: "CPI", value: `${cpi}%`, delta: "▼ easing", tone: "up" },
    { label: "Unemployment", value: `${unemployment}%`, delta: "▲ Q3 2024", tone: "down" },
    { label: "Matric Pass", value: `${matric}%`, delta: "▲ 2024", tone: "up" },
  ];

  const nat = crime?.national_totals ?? {};
  const previewProvinces = PROVINCE_LIST.map((p) => ({
    province: p,
    murders: crime?.provinces?.[p]?.Murder ?? 0,
  }));

  const preview = {
    period: crime?.period?.replace(" - ", " ") ?? "Q3 2024/25",
    kpis: {
      murders: Math.round((nat.Murder ?? 4872) / 4),
      carjackings: Math.round((nat.Carjacking ?? 3241) / 4),
      burglary: Math.round((nat["Residential burglary"] ?? 51204) / 4),
      sexual: Math.round((nat["Sexual offences"] ?? 10891) / 4),
    },
    provinces: previewProvinces,
  };

  return (
    <div className="precision-ops min-h-screen">
      <MarketingNav />
      <DataTicker items={tickerItems} />

      <MarketingHero preview={preview} />

      <section id="topics" className="border-t border-[var(--border)] bg-[var(--accent)]/30 px-6 py-20 lg:px-10">
        <div className="mx-auto max-w-7xl">
          <div className="mb-12 flex flex-col justify-between gap-6 lg:flex-row lg:items-end">
            <div>
              <SectionEyebrow>What we track</SectionEyebrow>
              <SectionTitle>
                10 topics.
                <br />
                One platform.
              </SectionTitle>
            </div>
            <p className="max-w-sm text-sm leading-relaxed text-[var(--muted-foreground)]">
              Every dataset auto-refreshes from official public sources — SAPS, Stats
              SA, SARB, Eskom, DWS, and more.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-2 md:grid-cols-3 lg:grid-cols-5">
            {TOPIC_MARKETING.map((topic) => (
              <Link key={topic.id} href={`/dashboard/${topic.id}`}>
                <Card className="h-full p-4 transition-all hover:border-[var(--primary)]/40 hover:shadow-md">
                  <div className="text-xl">{topic.emoji}</div>
                  <p className="mt-2 text-sm font-semibold leading-snug">{topic.name}</p>
                  <p className="mt-1 font-mono text-[10px] text-[var(--muted-foreground)]">
                    {topic.source}
                  </p>
                  <Badge variant="outline" className="mt-3 text-[9px]">
                    {topic.cadence}
                  </Badge>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section id="audience" className="relative px-6 py-20 lg:px-10">
        <div className="marketing-grid-bg pointer-events-none absolute inset-0 opacity-50" />
        <div className="relative mx-auto max-w-7xl">
          <SectionEyebrow>Who it&apos;s for</SectionEyebrow>
          <SectionTitle>
            Built for people
            <br />
            who act on data.
          </SectionTitle>
          <div className="mt-12 grid gap-px overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--border)] md:grid-cols-2 lg:grid-cols-3">
            {AUDIENCE.map((card) => (
              <div
                key={card.num}
                className="bg-[var(--background)] p-8 transition-colors hover:bg-[var(--accent)]/40"
              >
                <p className="text-4xl font-bold text-[var(--primary)]/20">{card.num}</p>
                <h3 className="mt-2 text-lg font-semibold">{card.role}</h3>
                <p className="mt-3 text-sm leading-relaxed text-[var(--muted-foreground)]">
                  {card.desc}
                </p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {card.tags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full border border-[var(--border)] px-2.5 py-0.5 font-mono text-[10px] text-[var(--muted-foreground)]"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="ai" className="border-t border-[var(--border)] bg-white/50 px-6 py-20 dark:bg-slate-900/20 lg:px-10">
        <div className="mx-auto grid max-w-7xl gap-12 lg:grid-cols-2 lg:items-center">
          <div>
            <SectionEyebrow>AI Analyst</SectionEyebrow>
            <SectionTitle>
              Ask anything.
              <br />
              Get real answers.
            </SectionTitle>
            <p className="mt-6 text-base leading-relaxed text-[var(--muted-foreground)]">
              Every dashboard page has a Claude-powered analyst that knows SA&apos;s data
              cold. Ask it why dam levels dropped, which province is safest to invest in,
              or how the repo rate affects your bond repayment.
            </p>
            <ul className="mt-8 space-y-3">
              {AI_FEATURES.map((feature) => (
                <li
                  key={feature}
                  className="flex gap-3 text-sm text-[var(--muted-foreground)]"
                >
                  <span className="text-[var(--primary)]">→</span>
                  {feature}
                </li>
              ))}
            </ul>
          </div>
          <AiChatMock />
        </div>
      </section>

      <section id="pricing" className="px-6 py-20 lg:px-10">
        <div className="mx-auto max-w-7xl">
          <SectionEyebrow>Pricing</SectionEyebrow>
          <SectionTitle>
            Start free.
            <br />
            Upgrade when it matters.
          </SectionTitle>
          <div className="mt-12 grid gap-6 lg:grid-cols-3">
            {PRICING_PLANS.map((plan) => (
              <PricingCard
                key={plan.tier}
                tier={plan.tier}
                price={plan.price}
                priceSuffix={"priceSuffix" in plan ? plan.priceSuffix : undefined}
                period={plan.period}
                featured={plan.featured}
                badge={"badge" in plan ? plan.badge : undefined}
                cta={plan.cta}
                href={plan.href}
                primary={plan.primary}
                features={[...plan.features]}
              />
            ))}
          </div>
        </div>
      </section>

      <section className="relative overflow-hidden border-t border-[var(--border)] px-6 py-24 lg:px-10">
        <div className="marketing-grid-bg pointer-events-none absolute inset-0" />
        <div className="relative mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
            South Africa&apos;s data,
            <br />
            <span className="text-[var(--primary)]">finally in one place.</span>
          </h2>
          <p className="mt-4 text-[var(--muted-foreground)]">
            Free to use. No signup required. Open the dashboard and start exploring
            right now.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link
              href="/dashboard/crime"
              className="inline-flex h-10 items-center rounded-lg bg-[var(--primary)] px-6 text-sm font-medium text-white hover:opacity-90"
            >
              Open free dashboard →
            </Link>
            <Link
              href="mailto:zolile@mlkcomputer.com"
              className="inline-flex h-10 items-center rounded-lg border border-[var(--border)] px-6 text-sm font-medium hover:bg-[var(--accent)]"
            >
              Get in touch
            </Link>
          </div>
        </div>
      </section>

      <MarketingFooter />
    </div>
  );
}
