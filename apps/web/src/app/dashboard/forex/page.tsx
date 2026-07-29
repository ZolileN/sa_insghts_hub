import {
  ChartPanel,
  KpiCard,
  PageHeader,
  SourceBadge,
} from "@/components/dashboard/page-parts";
import { SimpleBarChart, SimpleLineChart } from "@/components/charts/recharts";
import { lastTwoFromRecord, pctChange } from "@/shared/data/intelligence";
import { loadJson } from "@/shared/data/load";
import { formatNumber } from "@/shared/utils";

type ForexData = {
  source?: string;
  scraped_at?: string;
  is_live?: boolean;
  live_rates?: {
    usd_zar?: number;
    eur_zar?: number;
    gbp_zar?: number;
    usd_bwp?: number;
    usd_ngn?: number;
    usd_kes?: number;
    timestamp?: string;
  };
  usd_zar_history?: Record<string, number>;
  intelligence?: {
    import_cost_per_usd_1000_r?: number;
    sarb_official_url?: string;
  };
};

export default async function ForexPage() {
  const d = await loadJson<ForexData>("forex");
  const rates = d?.live_rates ?? {};
  const usdZar = rates.usd_zar ?? 18.64;
  const eurZar = rates.eur_zar ?? 20.21;
  const gbpZar = rates.gbp_zar ?? 23.48;
  const eurUsdImplied = usdZar > 0 ? eurZar / usdZar : 0;

  const historyPair = lastTwoFromRecord(d?.usd_zar_history ?? {});
  const zarMomentum =
    historyPair != null ? pctChange(historyPair[3], historyPair[1]) : null;

  const importCost =
    d?.intelligence?.import_cost_per_usd_1000_r ??
    Math.round(usdZar * 1000);

  const historyChart = Object.entries(d?.usd_zar_history ?? {}).map(
    ([month, rate]) => ({ month, rate }),
  );

  const crosses = [
    { pair: "USD/ZAR", rate: usdZar },
    { pair: "EUR/ZAR", rate: eurZar },
    { pair: "GBP/ZAR", rate: gbpZar },
    { pair: "USD/BWP", rate: rates.usd_bwp ?? 13.72 },
    { pair: "USD/KES", rate: rates.usd_kes ?? 129.5 },
    { pair: "USD/NGN", rate: rates.usd_ngn ?? 1600 },
  ];

  return (
    <div>
      <PageHeader
        title="ZAR Exchange Rate & Forex"
        description="Live rand crosses — imports, remittances, and offshore limits."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="USD/ZAR"
          value={`R${usdZar.toFixed(2)}`}
          hint={rates.timestamp ?? "Latest available"}
        />
        <KpiCard label="EUR/ZAR" value={`R${eurZar.toFixed(2)}`} />
        <KpiCard label="GBP/ZAR" value={`R${gbpZar.toFixed(2)}`} />
        <KpiCard
          label="£1,000 UK remittance"
          value={`R${formatNumber(Math.round(gbpZar * 1000))}`}
          hint="Sterling inflow at today's rate"
        />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="ZAR momentum (monthly)"
          value={
            zarMomentum != null
              ? `${zarMomentum >= 0 ? "+" : ""}${zarMomentum.toFixed(1)}%`
              : "—"
          }
          hint={
            historyPair
              ? `USD/ZAR ${historyPair[0]} → ${historyPair[2]}`
              : "SARB / market history"
          }
          trendPositive={zarMomentum != null && zarMomentum < 0}
          trend={
            zarMomentum != null && zarMomentum > 2
              ? "Rand weakening"
              : "Rand stable or firmer"
          }
        />
        <KpiCard
          label="Import cost proxy"
          value={`R${formatNumber(importCost)}`}
          hint="Per US$1,000 of imports"
        />
        <KpiCard
          label="EUR/USD implied"
          value={eurUsdImplied.toFixed(3)}
          hint="Cross-rate from ZAR pairs"
        />
        <KpiCard
          label="Regional USD/BWP"
          value={`P${(rates.usd_bwp ?? 14.07).toFixed(2)}`}
          hint="Southern Africa peer comparison"
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartPanel title="Major currency crosses vs ZAR">
          <SimpleBarChart
            data={crosses}
            xKey="pair"
            yKey="rate"
            color="#2563eb"
          />
        </ChartPanel>
        {historyChart.length > 0 && (
          <ChartPanel title="USD/ZAR trend (recent months)">
            <SimpleLineChart
              data={historyChart}
              xKey="month"
              lines={[{ key: "rate", color: "#059669", name: "USD/ZAR" }]}
            />
          </ChartPanel>
        )}
      </div>

      <SourceBadge
        source="South African Reserve Bank · Frankfurter · open.er-api.com"
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
