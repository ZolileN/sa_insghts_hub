import {
  ChartPanel,
  KpiCard,
  PageHeader,
  SourceBadge,
} from "@/components/dashboard/page-parts";
import { SimpleBarChart } from "@/components/charts/recharts";
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
};

export default async function ForexPage() {
  const d = await loadJson<ForexData>("forex");
  const rates = d?.live_rates ?? {};
  const usdZar = rates.usd_zar ?? 18.64;
  const eurZar = rates.eur_zar ?? 20.21;
  const gbpZar = rates.gbp_zar ?? 23.48;

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
        description="Live rand crosses — critical for imports, remittances, and offshore investment limits."
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
          label="Data status"
          value={d?.is_live ? "Live feed" : "Cached"}
          hint="open.er-api.com + SARB"
          trendPositive={d?.is_live}
        />
      </div>

      <div className="mt-6">
        <ChartPanel title="Major currency crosses vs ZAR">
          <SimpleBarChart
            data={crosses}
            xKey="pair"
            yKey="rate"
            color="#2563eb"
          />
        </ChartPanel>
      </div>

      <SourceBadge
        source={d?.source ?? "open.er-api.com · SARB"}
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
