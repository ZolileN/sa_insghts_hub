import {
  ChartPanel,
  KpiCard,
  PageHeader,
  SourceBadge,
} from "@/components/dashboard/page-parts";
import {
  SimpleBarChart,
  SimpleLineChart,
  SimplePieChart,
} from "@/components/charts/recharts";
import { loadJson } from "@/shared/data/load";
import { formatNumber } from "@/shared/utils";

type FraudData = {
  source?: string;
  scraped_at?: string;
  is_live?: boolean;
  total_losses_r_billion?: number;
  sim_swap_incidents?: number;
  categories?: Record<string, { losses_rm?: number; incidents?: number }>;
  trend_r_billion?: Record<string, number>;
};

export default async function FraudPage() {
  const d = await loadJson<FraudData>("fraud");
  const totalB = d?.total_losses_r_billion ?? 3.3;
  const categories = d?.categories ?? {};

  const pieData = Object.entries(categories).map(([name, v]) => ({
    name,
    losses: v.losses_rm ?? 0,
  }));

  const incidentData = Object.entries(categories)
    .map(([name, v]) => ({
      category: name,
      incidents: v.incidents ?? 0,
    }))
    .sort((a, b) => b.incidents - a.incidents)
    .slice(0, 6);

  const trend = Object.entries(d?.trend_r_billion ?? {}).map(([year, val]) => ({
    year,
    billions: val,
  }));

  const topCategory = pieData.sort((a, b) => b.losses - a.losses)[0];

  return (
    <div>
      <PageHeader
        title="Bank Fraud & Financial Crime"
        description="SABRIC banking fraud — where digital crime concentrates and how losses are trending."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Total banking fraud losses"
          value={`R${totalB}bn`}
          hint="Annual reported losses"
        />
        <KpiCard
          label="SIM swap incidents"
          value={formatNumber(d?.sim_swap_incidents ?? 39)}
          hint="Account takeover vector"
        />
        <KpiCard
          label="Top loss category"
          value={topCategory?.name ?? "Card not present"}
          hint={`R${formatNumber(topCategory?.losses ?? 0)}m estimated`}
        />
        <KpiCard
          label="Fraud categories tracked"
          value={formatNumber(Object.keys(categories).length)}
          hint="SABRIC annual taxonomy"
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartPanel title="Losses by fraud type (R millions)">
          <SimplePieChart data={pieData} nameKey="name" valueKey="losses" />
        </ChartPanel>
        <ChartPanel title="Incident volume by category">
          <SimpleBarChart
            data={incidentData}
            xKey="category"
            yKey="incidents"
            layout="vertical"
            color="#7c3aed"
          />
        </ChartPanel>
      </div>

      <div className="mt-6">
        <ChartPanel title="Total fraud losses trend (R billions)">
          <SimpleLineChart
            data={trend}
            xKey="year"
            lines={[{ key: "billions", color: "#dc2626", name: "Losses (R bn)" }]}
          />
        </ChartPanel>
      </div>

      <SourceBadge
        source={d?.source ?? "SABRIC"}
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
