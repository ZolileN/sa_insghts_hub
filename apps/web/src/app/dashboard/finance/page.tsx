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
  repo_history?: Record<string, number>;
  cpi_basket?: Record<string, number>;
};

export default async function FinancePage() {
  const d = await loadJson<FinanceData>("finance");
  const repo = d?.repo_rate_pct ?? 6.75;
  const prime = d?.prime_rate_pct ?? 10.25;
  const cpi = d?.cpi_headline_pct ?? 3.5;

  const repoTrend = Object.entries(d?.repo_history ?? {}).map(([q, r]) => ({
    quarter: q,
    repo: r,
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

  return (
    <div>
      <PageHeader
        title="Interest Rates & Inflation"
        description="SARB policy rate, prime lending rate, and CPI — what drives bonds, rents, and business costs."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Repo rate"
          value={`${repo}%`}
          hint="SARB policy rate"
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
          trendPositive={cpi <= 6}
        />
        <KpiCard
          label="Bond on R1.5m home"
          value={`R${monthlyBond.find((b) => b.price_k === 1.5)?.repayment?.toLocaleString() ?? "—"}`}
          hint="Est. 20yr at prime — illustrative"
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

      <div className="mt-6">
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
        source={d?.source ?? "SARB · Stats SA"}
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
