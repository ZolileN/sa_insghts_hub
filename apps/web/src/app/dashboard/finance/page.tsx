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
  const repo = d?.repo_rate_pct ?? 6.75;
  const prime = d?.prime_rate_pct ?? 10.25;
  const cpi = d?.cpi_headline_pct ?? 3.5;
  const spread = prime - repo;
  const realRate = prime - cpi;
  const inTargetBand = cpi >= 3 && cpi <= 6;

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

  const bondPrices = [800, 1000, 1200, 1500, 2000, 2500];
  const monthlyBond = bondPrices.map((price) => ({
    price_k: price / 1000,
    repayment:
      Math.round(
        (price * 1000 * (prime / 100 / 12)) /
          (1 - Math.pow(1 + prime / 100 / 12, -240)),
      ),
  }));

  const hottestCategory = cpiBasket.sort((a, b) => b.cpi - a.cpi)[0];
  const budget = d?.budget ?? {};

  return (
    <div>
      <PageHeader
        title="Interest Rates & Inflation"
        description="SARB policy, prime lending, and CPI — what drives bonds, rents, and business costs."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Repo rate"
          value={`${repo}%`}
          hint={d?.cpi_period ? `CPI period: ${d.cpi_period}` : "SARB policy rate"}
        />
        <KpiCard
          label="Prime lending rate"
          value={`${prime}%`}
          hint="Most home loans priced off prime"
        />
        <KpiCard
          label="Headline CPI"
          value={`${cpi}%`}
          hint="Inflation target band 3–6%"
          trendPositive={inTargetBand}
          trend={inTargetBand ? "Within SARB band" : "Outside target band"}
        />
        <KpiCard
          label="Bond on R1.5m home"
          value={`R${monthlyBond.find((b) => b.price_k === 1.5)?.repayment?.toLocaleString() ?? "—"}`}
          hint="Est. 20yr at prime — illustrative"
        />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Prime − repo spread"
          value={`${spread.toFixed(2)}pp`}
          hint="Bank margin on policy rate"
        />
        <KpiCard
          label="Real borrowing rate"
          value={`${realRate.toFixed(1)}%`}
          hint="Prime minus headline CPI"
          trendPositive={realRate < 8}
          trend={
            realRate > 7 ? "Tight for borrowers" : "Moderate real rate"
          }
        />
        <KpiCard
          label="CPI vs target midpoint"
          value={`${(cpi - 4.5).toFixed(1)}pp`}
          hint="Distance from 4.5% midpoint"
          trendPositive={Math.abs(cpi - 4.5) <= 1.5}
        />
        <KpiCard
          label="Hot inflation category"
          value={hottestCategory?.category ?? "Food"}
          hint={`${hottestCategory?.cpi ?? "—"}% annual change`}
          trendPositive={(hottestCategory?.cpi ?? 6) <= 5}
        />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Budget data portal"
          value={budget.packages_found != null ? `${budget.packages_found} datasets` : "Vulekamali"}
          hint={budget.latest_financial_year ?? "National Treasury open budget"}
        />
        <KpiCard
          label="Open budget FY"
          value={budget.latest_financial_year ?? "2025-26"}
          hint={budget.portal ?? "https://vulekamali.gov.za"}
        />
        <KpiCard
          label="eTenders procurement"
          value="National Treasury"
          hint="https://www.etenders.gov.za"
        />
        <KpiCard
          label="Budget feed status"
          value={budget.packages_found ? "CKAN live" : "Cached"}
          hint={budget.note ?? "Division of revenue & ENE datasets"}
          trendPositive={Boolean(budget.packages_found)}
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartPanel title="Repo rate history (quarterly)">
          <SimpleLineChart
            data={repoTrend}
            xKey="quarter"
            lines={[{ key: "repo", color: "#2563eb", name: "Repo %" }]}
          />
        </ChartPanel>
        <ChartPanel title="CPI by category">
          <SimpleBarChart
            data={cpiBasket}
            xKey="category"
            yKey="cpi"
            layout="vertical"
            color="#d97706"
          />
        </ChartPanel>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartPanel title="Headline CPI trend">
          <SimpleLineChart
            data={cpiTrend}
            xKey="period"
            lines={[{ key: "cpi", color: "#d97706", name: "CPI %" }]}
          />
        </ChartPanel>
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
      </div>

      <SourceBadge
        source={`${d?.source ?? "SARB · Stats SA"} · Vulekamali · eTenders`}
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
