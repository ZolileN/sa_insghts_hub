import {
  ChartPanel,
  KpiCard,
  PageHeader,
  SourceBadge,
} from "@/components/dashboard/page-parts";
import {
  SimpleBarChart,
  SimpleLineChart,
} from "@/components/charts/recharts";
import { dashPct } from "@/shared/data/display";
import { loadJson } from "@/shared/data/load";

type FinanceData = {
  source?: string;
  scraped_at?: string;
  is_live?: boolean;
  repo_rate_pct?: number;
  prime_rate_pct?: number;
  cpi_headline_pct?: number;
  cpi_period?: string;
  repo_history?: Record<string, number>;
  cpi_history?: Record<string, number>;
  cpi_basket?: Record<string, number>;
  budget?: {
    portal?: string;
    latest_financial_year?: string;
    packages_found?: number;
    note?: string;
  };
};

export default async function FinancePage() {
  const d = await loadJson<FinanceData>("finance");
  const repo = d?.repo_rate_pct;
  const prime = d?.prime_rate_pct;
  const cpi = d?.cpi_headline_pct;
  const spread =
    repo != null && prime != null ? prime - repo : null;
  const realRate =
    prime != null && cpi != null ? prime - cpi : null;
  const inTargetBand = cpi != null && cpi >= 3 && cpi <= 6;

  const repoTrend = Object.entries(d?.repo_history ?? {}).map(([q, r]) => ({
    quarter: q,
    repo: r,
  }));

  const cpiTrend = Object.entries(d?.cpi_history ?? {}).map(([period, val]) => ({
    period,
    cpi: val,
  }));

  const cpiBasket = Object.entries(d?.cpi_basket ?? {}).map(([cat, val]) => ({
    category: cat,
    cpi: val,
  }));

  const monthlyBond =
    prime != null
      ? [800, 1000, 1200, 1500, 2000, 2500].map((price) => ({
          price_k: price / 1000,
          repayment: Math.round(
            (price * 1000 * (prime / 100 / 12)) /
              (1 - Math.pow(1 + prime / 100 / 12, -240)),
          ),
        }))
      : [];

  const hottestCategory =
    cpiBasket.length > 0
      ? cpiBasket.sort((a, b) => b.cpi - a.cpi)[0]
      : null;
  const foodInflation = cpiBasket.find((c) =>
    c.category.startsWith("Food"),
  )?.cpi;
  const transportInflation = cpiBasket.find(
    (c) => c.category === "Transport",
  )?.cpi;
  const housingInflation = cpiBasket.find((c) =>
    c.category.startsWith("Housing"),
  )?.cpi;
  const repoPrior =
    repoTrend.length >= 2 ? repoTrend[repoTrend.length - 2].repo : null;
  const repoChange =
    repo != null && repoPrior != null
      ? Math.round((repo - repoPrior) * 100) / 100
      : null;

  return (
    <div>
      <PageHeader
        title="Interest Rates & Inflation"
        description="SARB policy, prime lending, and CPI — what drives bonds, rents, and business costs."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Repo rate"
          value={dashPct(repo)}
          hint={d?.cpi_period ? `CPI period: ${d.cpi_period}` : "SARB policy rate"}
        />
        <KpiCard
          label="Prime lending rate"
          value={dashPct(prime)}
          hint="Most home loans priced off prime"
        />
        <KpiCard
          label="Headline CPI"
          value={dashPct(cpi)}
          hint="Inflation target band 3–6%"
          trendPositive={inTargetBand}
          trend={
            cpi != null
              ? inTargetBand
                ? "Within SARB band"
                : "Outside target band"
              : undefined
          }
        />
        <KpiCard
          label="Bond on R1.5m home"
          value={
            monthlyBond.length
              ? `R${
                  monthlyBond.find((b) => b.price_k === 1.5)?.repayment?.toLocaleString() ??
                  "—"
                }`
              : "—"
          }
          hint="Est. 20yr at prime — illustrative"
        />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Prime − repo spread"
          value={
            spread != null ? `${spread.toFixed(2)}pp` : "—"
          }
          hint="Bank margin on policy rate"
        />
        <KpiCard
          label="Real borrowing rate"
          value={realRate != null ? `${realRate.toFixed(1)}%` : "—"}
          hint="Prime minus headline CPI"
          trendPositive={realRate != null && realRate < 8}
          trend={
            realRate != null
              ? realRate > 7
                ? "Tight for borrowers"
                : "Moderate real rate"
              : undefined
          }
        />
        <KpiCard
          label="CPI vs target midpoint"
          value={
            cpi != null ? `${(cpi - 4.5).toFixed(1)}pp` : "—"
          }
          hint="Distance from 4.5% midpoint"
          trendPositive={cpi != null && Math.abs(cpi - 4.5) <= 1.5}
        />
        <KpiCard
          label="Hot inflation category"
          value={hottestCategory?.category ?? "—"}
          hint={
            hottestCategory != null
              ? `${hottestCategory.cpi}% annual change`
              : "CPI basket"
          }
          trendPositive={
            hottestCategory != null ? hottestCategory.cpi <= 5 : undefined
          }
        />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Food inflation"
          value={dashPct(foodInflation)}
          hint="Largest household budget pressure"
          trendPositive={foodInflation != null && foodInflation <= 5}
        />
        <KpiCard
          label="Transport inflation"
          value={dashPct(transportInflation)}
          hint="Fuel and mobility costs"
          trendPositive={transportInflation != null && transportInflation <= 5}
        />
        <KpiCard
          label="Housing & utilities"
          value={dashPct(housingInflation)}
          hint="Rent, water, and electricity costs"
          trendPositive={housingInflation != null && housingInflation <= 5}
        />
        <KpiCard
          label="Repo change (quarter)"
          value={
            repoChange != null
              ? `${repoChange >= 0 ? "+" : ""}${repoChange.toFixed(2)}pp`
              : "—"
          }
          hint="Policy rate move since prior quarter"
          trendPositive={repoChange != null && repoChange <= 0}
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        {repoTrend.length > 0 && (
          <ChartPanel title="Repo rate history (quarterly)">
            <SimpleLineChart
              data={repoTrend}
              xKey="quarter"
              lines={[{ key: "repo", color: "#2563eb", name: "Repo %" }]}
            />
          </ChartPanel>
        )}
        {cpiBasket.length > 0 && (
          <ChartPanel title="CPI by category">
            <SimpleBarChart
              data={cpiBasket}
              xKey="category"
              yKey="cpi"
              layout="vertical"
              color="#d97706"
            />
          </ChartPanel>
        )}
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        {cpiTrend.length > 0 && (
          <ChartPanel title="Headline CPI trend">
            <SimpleLineChart
              data={cpiTrend}
              xKey="period"
              lines={[{ key: "cpi", color: "#d97706", name: "CPI %" }]}
            />
          </ChartPanel>
        )}
        {monthlyBond.length > 0 && prime != null && (
          <ChartPanel
            title="Monthly bond repayment vs home price"
            description={`At prime ${prime}% over 20 years`}
          >
            <SimpleBarChart
              data={monthlyBond}
              xKey="price_k"
              yKey="repayment"
              color="#059669"
            />
          </ChartPanel>
        )}
      </div>

      <SourceBadge
        source="South African Reserve Bank · Statistics South Africa · National Treasury"
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
