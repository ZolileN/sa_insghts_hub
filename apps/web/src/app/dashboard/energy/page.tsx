import {
  ChartPanel,
  KpiCard,
  PageHeader,
  SourceBadge,
} from "@/components/dashboard/page-parts";
import {
  MultiBarChart,
  SimpleLineChart,
  SimplePieChart,
} from "@/components/charts/recharts";
import { estimateMonthlyElectricityBill, pctChange } from "@/shared/data/intelligence";
import { loadJson } from "@/shared/data/load";
import { formatNumber } from "@/shared/utils";

type EnergyData = {
  source?: string;
  scraped_at?: string;
  is_live?: boolean;
  current_stage?: number;
  stage_label?: string;
  active?: boolean;
  upcoming_outages?: unknown[];
  monthly_hours_2024?: Record<string, number>;
  monthly_hours_2023?: Record<string, number>;
  annual_totals?: Record<string, number>;
  electricity_tariff_history?: Record<string, number>;
  energy_mix_pct_2024?: Record<string, number>;
};

export default async function EnergyPage() {
  const d = await loadJson<EnergyData>("energy");
  const stage = d?.current_stage ?? 0;
  const hours2024 = Object.values(d?.monthly_hours_2024 ?? {}).reduce(
    (a, b) => a + b,
    0,
  );
  const hours2023 = Object.values(d?.monthly_hours_2023 ?? {}).reduce(
    (a, b) => a + b,
    0,
  );
  const hoursReductionPct = pctChange(hours2024, hours2023);
  const tariff2024 = d?.electricity_tariff_history?.["2024"] ?? 436;
  const mix = d?.energy_mix_pct_2024 ?? {};
  const renewablePct =
    (mix.Solar ?? 0) + (mix.Wind ?? 0) + (mix.Hydro ?? 0) + (mix.Other ?? 0);
  const upcoming = d?.upcoming_outages?.length ?? 0;
  const monthlyBill = estimateMonthlyElectricityBill(400, tariff2024);

  const monthlyCompare = Object.keys(d?.monthly_hours_2024 ?? {}).map((m) => ({
    month: m,
    "2023": d?.monthly_hours_2023?.[m] ?? 0,
    "2024": d?.monthly_hours_2024?.[m] ?? 0,
  }));

  const annual = Object.entries(d?.annual_totals ?? {}).map(([year, h]) => ({
    year,
    hours: h,
  }));

  const mixChart = Object.entries(mix).map(([name, pct]) => ({
    name,
    pct,
  }));

  const tariffTrend = Object.entries(d?.electricity_tariff_history ?? {}).map(
    ([year, c]) => ({ year, tariff: c }),
  );

  return (
    <div>
      <PageHeader
        title="Load Shedding & Energy"
        description="Eskom stage, outage hours, tariffs, and generation mix — power reliability and cost."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Current load shedding"
          value={d?.stage_label ?? "Unknown"}
          hint={d?.active ? "Active outages" : "Grid stable"}
          trendPositive={!d?.active}
          trend={stage === 0 ? "No load shedding" : `Stage ${stage}`}
        />
        <KpiCard
          label="Outage hours 2024"
          value={formatNumber(hours2024)}
          hint="Total scheduled outage hours"
          trendPositive={hours2024 < hours2023}
          trend={`vs ${formatNumber(hours2023)} hrs in 2023`}
        />
        <KpiCard
          label="Electricity tariff"
          value={`${tariff2024} c/kWh`}
          hint="Homes & business cost pressure"
        />
        <KpiCard
          label="Solar in mix"
          value={`${mix.Solar ?? 10}%`}
          hint={`Coal still ${mix.Coal ?? 57}%`}
        />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Outage reduction vs 2023"
          value={
            hoursReductionPct != null
              ? `${hoursReductionPct.toFixed(0)}%`
              : "—"
          }
          hint="Fewer scheduled hours in 2024"
          trendPositive={hoursReductionPct != null && hoursReductionPct < 0}
          trend={
            hoursReductionPct != null && hoursReductionPct < -50
              ? "Major improvement"
              : "Still elevated risk"
          }
        />
        <KpiCard
          label="Upcoming schedules"
          value={formatNumber(upcoming)}
          hint="Planned outage windows ahead"
          trendPositive={upcoming === 0}
        />
        <KpiCard
          label="Est. monthly bill (400 kWh)"
          value={`R${formatNumber(monthlyBill)}`}
          hint={`At ${tariff2024} c/kWh — household proxy`}
        />
        <KpiCard
          label="Renewable share"
          value={`${renewablePct}%`}
          hint="Solar + wind + hydro + other"
          trendPositive={renewablePct >= 15}
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartPanel title="Monthly outage hours — 2023 vs 2024">
          <MultiBarChart
            data={monthlyCompare}
            xKey="month"
            keys={[
              { key: "2023", color: "#dc2626", name: "2023" },
              { key: "2024", color: "#059669", name: "2024" },
            ]}
          />
        </ChartPanel>
        <ChartPanel title="Energy generation mix 2024">
          <SimplePieChart data={mixChart} nameKey="name" valueKey="pct" />
        </ChartPanel>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartPanel title="Annual load shedding hours">
          <SimpleLineChart
            data={annual}
            xKey="year"
            lines={[{ key: "hours", color: "#d97706", name: "Hours" }]}
          />
        </ChartPanel>
        <ChartPanel title="Electricity tariff trend (c/kWh)">
          <SimpleLineChart
            data={tariffTrend}
            xKey="year"
            lines={[{ key: "tariff", color: "#2563eb", name: "Tariff" }]}
          />
        </ChartPanel>
      </div>

      <SourceBadge
        source="Eskom · CSIR · DMRE fuel prices"
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
