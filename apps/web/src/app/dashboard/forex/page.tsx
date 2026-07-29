import {
  ChartPanel,
  KpiCard,
  PageHeader,
  SourceBadge,
} from "@/components/dashboard/page-parts";
import { SimpleBarChart, SimpleLineChart } from "@/components/charts/recharts";
import { dashFixed, dashNum } from "@/shared/data/display";
import { lastTwoFromRecord, pctChange } from "@/shared/data/intelligence";
import { loadJson } from "@/shared/data/load";

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
  const usdZar = rates.usd_zar;
  const eurZar = rates.eur_zar;
  const gbpZar = rates.gbp_zar;
  const eurUsdImplied =
    usdZar != null && eurZar != null && usdZar > 0 ? eurZar / usdZar : null;

  const historyPair = lastTwoFromRecord(d?.usd_zar_history ?? {});
  const zarMomentum =
    historyPair != null ? pctChange(historyPair[3], historyPair[1]) : null;

  const importCost =
    d?.intelligence?.import_cost_per_usd_1000_r ??
    (usdZar != null ? Math.round(usdZar * 1000) : null);

  const historyChart = Object.entries(d?.usd_zar_history ?? {}).map(
    ([month, rate]) => ({ month, rate }),
  );

  const crosses = [
    usdZar != null ? { pair: "USD/ZAR", rate: usdZar } : null,
    eurZar != null ? { pair: "EUR/ZAR", rate: eurZar } : null,
    gbpZar != null ? { pair: "GBP/ZAR", rate: gbpZar } : null,
    rates.usd_bwp != null ? { pair: "USD/BWP", rate: rates.usd_bwp } : null,
    rates.usd_kes != null ? { pair: "USD/KES", rate: rates.usd_kes } : null,
    rates.usd_ngn != null ? { pair: "USD/NGN", rate: rates.usd_ngn } : null,
  ].filter(Boolean) as { pair: string; rate: number }[];

  return (
    <div>
      <PageHeader
        title="ZAR Exchange Rate & Forex"
        description="Live rand crosses — imports, remittances, and offshore limits."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="USD/ZAR"
          value={usdZar != null ? `R${usdZar.toFixed(2)}` : "—"}
          hint={rates.timestamp ?? "Live scrape"}
        />
        <KpiCard
          label="EUR/ZAR"
          value={eurZar != null ? `R${eurZar.toFixed(2)}` : "—"}
        />
        <KpiCard
          label="GBP/ZAR"
          value={gbpZar != null ? `R${gbpZar.toFixed(2)}` : "—"}
        />
        <KpiCard
          label="£1,000 UK remittance"
          value={
            gbpZar != null
              ? `R${dashNum(Math.round(gbpZar * 1000))}`
              : "—"
          }
          hint="Sterling inflow at scraped rate"
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
              : zarMomentum != null
                ? "Rand stable or firmer"
                : undefined
          }
        />
        <KpiCard
          label="Import cost proxy"
          value={importCost != null ? `R${dashNum(importCost)}` : "—"}
          hint="Per US$1,000 of imports"
        />
        <KpiCard
          label="EUR/USD implied"
          value={dashFixed(eurUsdImplied, 3)}
          hint="Cross-rate from ZAR pairs"
        />
        <KpiCard
          label="Regional USD/BWP"
          value={
            rates.usd_bwp != null ? `P${rates.usd_bwp.toFixed(2)}` : "—"
          }
          hint="Southern Africa peer comparison"
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        {crosses.length > 0 ? (
          <ChartPanel title="Major currency crosses vs ZAR">
            <SimpleBarChart
              data={crosses}
              xKey="pair"
              yKey="rate"
              color="#2563eb"
            />
          </ChartPanel>
        ) : null}
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
