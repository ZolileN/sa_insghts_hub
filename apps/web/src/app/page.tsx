import Link from "next/link";
import { ArrowRight, BarChart3, MapPin, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TOPICS } from "@/shared/data/constants";
import { loadJson } from "@/shared/data/load";

export default async function HomePage() {
  const forex = await loadJson<{
    live_rates?: { usd_zar?: number };
    is_live?: boolean;
  }>("forex");
  const energy = await loadJson<{
    stage_label?: string;
    is_live?: boolean;
  }>("energy");

  return (
    <div className="precision-ops min-h-screen">
      <header className="chrome-bar sticky top-0 z-10 px-6 py-4">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--primary)] text-sm font-bold text-white">
              L
            </div>
            <div>
              <p className="text-sm font-semibold">Libo Insights</p>
              <p className="text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">
                Area intelligence
              </p>
            </div>
          </div>
          <Button asChild>
            <Link href="/dashboard">Open dashboard</Link>
          </Button>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-16 lg:py-24">
        <div className="max-w-3xl">
          <Badge variant="secondary" className="mb-4">
            South Africa public data platform
          </Badge>
          <h1 className="text-4xl font-semibold tracking-tight lg:text-5xl">
            Know an area before you decide.
          </h1>
          <p className="mt-4 text-lg text-[var(--muted-foreground)]">
            Ten critical data topics — crime, property, jobs, energy, health,
            education, forex, and water — in one Precision Ops dashboard with
            province-aware views.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button size="lg" asChild>
              <Link href="/dashboard/crime">
                Explore dashboards
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/dashboard/forex">Live forex</Link>
            </Button>
          </div>
        </div>

        <div className="mt-10 grid gap-4 sm:grid-cols-3">
          <Card className="p-4">
            <p className="text-xs text-[var(--muted-foreground)]">USD/ZAR</p>
            <p className="mt-1 text-2xl font-semibold tabular-nums">
              R{forex?.live_rates?.usd_zar?.toFixed(2) ?? "—"}
            </p>
            <Badge variant={forex?.is_live ? "success" : "warning"} className="mt-2">
              {forex?.is_live ? "Live" : "Cached"}
            </Badge>
          </Card>
          <Card className="p-4">
            <p className="text-xs text-[var(--muted-foreground)]">Load shedding</p>
            <p className="mt-1 text-2xl font-semibold">
              {energy?.stage_label ?? "—"}
            </p>
            <Badge variant={energy?.is_live ? "success" : "warning"} className="mt-2">
              {energy?.is_live ? "Live" : "Cached"}
            </Badge>
          </Card>
          <Card className="p-4">
            <p className="text-xs text-[var(--muted-foreground)]">Topics tracked</p>
            <p className="mt-1 text-2xl font-semibold">10</p>
            <p className="mt-2 text-xs text-[var(--muted-foreground)]">
              Updated via cron scrapers
            </p>
          </Card>
        </div>

        <section className="mt-20">
          <div className="page-heading-row mb-8">
            <h2 className="text-2xl font-semibold">What we track</h2>
            <p className="text-sm text-[var(--muted-foreground)]">
              Official public sources — SAPS, Stats SA, SARB, Eskom, DWS, and more.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {TOPICS.map((topic) => (
              <Link key={topic.id} href={`/dashboard/${topic.id}`}>
                <Card className="h-full transition-shadow hover:shadow-md">
                  <CardContent className="p-5">
                    <div className="flex items-start justify-between gap-2">
                      <p className="font-medium">{topic.label}</p>
                      <Badge variant="outline">{topic.cadence}</Badge>
                    </div>
                    <p className="mt-2 text-sm text-[var(--muted-foreground)]">
                      {topic.description}
                    </p>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </section>

        <section className="mt-20 grid gap-6 lg:grid-cols-3">
          <Card className="p-6">
            <BarChart3 className="h-5 w-5 text-[var(--primary)]" />
            <h3 className="mt-3 font-semibold">Decision-first KPIs</h3>
            <p className="mt-2 text-sm text-[var(--muted-foreground)]">
              Each topic highlights the metrics that matter for area risk, affordability,
              and liveability — not every column in the source file.
            </p>
          </Card>
          <Card className="p-6">
            <MapPin className="h-5 w-5 text-[var(--primary)]" />
            <h3 className="mt-3 font-semibold">Province filter</h3>
            <p className="mt-2 text-sm text-[var(--muted-foreground)]">
              Compare Western Cape vs Gauteng, or drill into a single province on every
              dashboard that supports regional data.
            </p>
          </Card>
          <Card className="p-6">
            <Sparkles className="h-5 w-5 text-[var(--primary)]" />
            <h3 className="mt-3 font-semibold">Built for Libo Insights</h3>
            <p className="mt-2 text-sm text-[var(--muted-foreground)]">
              Next.js dashboard with Precision Ops UI — light, clean, and ready for Pro
              features like AI analyst and alerts.
            </p>
          </Card>
        </section>
      </main>

      <footer className="border-t border-[var(--border)] px-6 py-8 text-center text-sm text-[var(--muted-foreground)]">
        Libo Insights · Cape Town, South Africa
      </footer>
    </div>
  );
}
