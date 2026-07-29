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
import {
  digitalFraudSharePct,
  lastTwoFromRecord,
  pctChange,
} from "@/shared/data/intelligence";
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

  const trendPair = lastTwoFromRecord(d?.trend_r_billion ?? {});
  const yoyLossPct =
    trendPair != null ? pctChange(trendPair[3], trendPair[1]) : null;

  const digitalShare = digitalFraudSharePct(categories);
  const totalIncidents = Object.values(categories).reduce(
    (a, c) => a + (c.incidents ?? 0),
    0,
  );
  const lossPerIncident =
    totalIncidents > 0 ? Math.round((totalB * 1000) / totalIncidents) : 0;

  const simSwap = categories["SIM swap/account takeover"];
  const simLossPerIncident =
    simSwap?.incidents
      ? Math.round((simSwap.losses_rm ?? 0) / simSwap.incidents)
      : 0;

  return (
    <div>
      <PageHeader
        title="Bank Fraud & Financial Crime"
        description="SABRIC banking fraud — digital threat vectors, loss momentum, and category risk. Sources: SABRIC, FSCA warnings, SIU reports."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Total banking fraud losses"
          value={`R${totalB}bn`}
          hint="SABRIC annual reported losses"
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

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="YoY loss momentum"
          value={
            yoyLossPct != null
              ? `${yoyLossPct >= 0 ? "+" : ""}${yoyLossPct.toFixed(1)}%`
              : "—"
          }
          hint={
            trendPair
              ? `${trendPair[0]} → ${trendPair[2]} (R bn)`
              : "Annual trend"
          }
          trendPositive={yoyLossPct != null ? yoyLossPct <= 5 : undefined}
          trend={
            yoyLossPct != null && yoyLossPct > 10
              ? "Losses accelerating"
              : "Moderate growth"
          }
        />
        <KpiCard
          label="Digital fraud share"
          value={`${digitalShare}%`}
          hint="Card-not-present, online, SIM swap, BEC, scams"
          trendPositive={digitalShare < 70}
        />
        <KpiCard
          label="Avg loss per incident"
          value={`R${formatNumber(lossPerIncident)}`}
          hint="Across all reported categories"
        />
        <KpiCard
          label="SIM swap loss / incident"
          value={`R${formatNumber(simLossPerIncident)}`}
          hint="Highest-impact takeover events"
          trendPositive={simLossPerIncident < 50000}
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
        source={`${d?.source ?? "SABRIC"} · FSCA public warnings · SIU reports`}
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
