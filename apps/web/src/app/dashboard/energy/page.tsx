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
  monthly_hours_by_year?: Record<string, Record<string, number>>;
  monthly_hours_2024?: Record<string, number>;
  monthly_hours_2023?: Record<string, number>;
  annual_totals?: Record<string, number>;
  electricity_tariff_history?: Record<string, number>;
  energy_mix_by_year?: Record<string, Record<string, number>>;
  energy_mix_pct_2024?: Record<string, number>;
  fy_stats?: {
    loadshedding_hours_fy?: number;
    consecutive_days_without?: number;
    eaf_pct?: number;
    financial_year?: string;
  };
};

function monthlyHoursForYear(d: EnergyData, year: string): Record<string, number> {
  if (d.monthly_hours_by_year?.[year]) return d.monthly_hours_by_year[year];
  if (year === "2024" && d.monthly_hours_2024) return d.monthly_hours_2024;
  if (year === "2023" && d.monthly_hours_2023) return d.monthly_hours_2023;
  return {};
}

function latestMonthlyYear(d: EnergyData): string | null {
  const years = Object.keys(d.monthly_hours_by_year ?? {});
  if (years.length) return years.sort().pop() ?? null;
  if (d.monthly_hours_2024) return "2024";
  return null;
}

function latestTariffYear(d: EnergyData): string | null {
  const keys = Object.keys(d.electricity_tariff_history ?? {});
  return keys.length ? keys.sort().pop() ?? null : null;
}

function energyMix(d: EnergyData): Record<string, number> {
  const byYear = d.energy_mix_by_year;
  if (byYear) {
    const y = Object.keys(byYear).sort().pop();
    if (y) return byYear[y];
  }
  return d.energy_mix_pct_2024 ?? {};
}

function mixYearLabel(d: EnergyData): string {
  const byYear = d.energy_mix_by_year;
  if (byYear && Object.keys(byYear).length) {
    return Object.keys(byYear).sort().pop() ?? "latest";
  }
  return "2024";
}

export default async function EnergyPage() {
  const d = await loadJson<EnergyData>("energy");
  const data: EnergyData = d ?? {};
  const stage = data.current_stage ?? 0;

  const currentYear = latestMonthlyYear(data) ?? String(new Date().getFullYear());
  const prevYear = String(Number(currentYear) - 1);
  const hoursCurrent = Object.values(monthlyHoursForYear(data, currentYear)).reduce(
    (a, b) => a + b,
    0,
  );
  const hoursPrev = Object.values(monthlyHoursForYear(data, prevYear)).reduce(
    (a, b) => a + b,
    0,
  );
  const annualHours =
    data.annual_totals?.[currentYear] ??
    data.fy_stats?.loadshedding_hours_fy ??
    hoursCurrent;
  const hoursReductionPct = hoursPrev > 0 ? pctChange(annualHours, hoursPrev) : null;

  const tariffYear = latestTariffYear(data) ?? currentYear;
  const tariff = data.electricity_tariff_history?.[tariffYear] ?? 0;
  const mix = energyMix(data);
  const mixYear = mixYearLabel(data);
  const upcoming = data.upcoming_outages?.length ?? 0;
  const monthlyBill = estimateMonthlyElectricityBill(400, tariff);
  const streak = data.fy_stats?.consecutive_days_without;

  const monthlyCompare = Object.keys(monthlyHoursForYear(data, currentYear)).map((m) => ({
    month: m,
    [prevYear]: monthlyHoursForYear(data, prevYear)[m] ?? 0,
    [currentYear]: monthlyHoursForYear(data, currentYear)[m] ?? 0,
  }));

  const annual = Object.entries(data.annual_totals ?? {}).map(([year, h]) => ({
    year,
    hours: h,
  }));

  const mixChart = Object.entries(mix).map(([name, pct]) => ({
    name,
    pct,
  }));

  const tariffTrend = Object.entries(data.electricity_tariff_history ?? {}).map(
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
          value={data.stage_label ?? "Unknown"}
          hint={data.active ? "Active outages" : "Grid stable"}
          trendPositive={!data.active}
          trend={stage === 0 ? "No load shedding" : `Stage ${stage}`}
        />
        <KpiCard
          label={`Outage hours ${currentYear}`}
          value={formatNumber(annualHours)}
          hint={
            data.fy_stats?.financial_year
              ? `FY ${data.fy_stats.financial_year} · Eskom media`
              : "Scheduled outage hours"
          }
          trendPositive={hoursPrev > 0 && annualHours < hoursPrev}
          trend={
            hoursPrev > 0
              ? `vs ${formatNumber(hoursPrev)} hrs in ${prevYear}`
              : undefined
          }
        />
        <KpiCard
          label="Electricity tariff"
          value={tariff ? `${tariff} c/kWh` : "—"}
          hint={`Latest published (${tariffYear})`}
        />
        <KpiCard
          label="Solar in mix"
          value={`${mix.Solar ?? 0}%`}
          hint={`Coal ${mix.Coal ?? 0}% · mix ${mixYear}`}
        />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label={`Outage change vs ${prevYear}`}
          value={
            hoursReductionPct != null
              ? `${hoursReductionPct.toFixed(0)}%`
              : "—"
          }
          hint={`Calendar/FY hours compared to ${prevYear}`}
          trendPositive={hoursReductionPct != null && hoursReductionPct < 0}
        />
        <KpiCard
          label="Days without load shedding"
          value={streak != null ? formatNumber(streak) : "—"}
          hint="Consecutive days (Eskom media)"
          trendPositive={streak != null && streak > 30}
        />
        <KpiCard
          label="Upcoming schedules"
          value={formatNumber(upcoming)}
          hint="Planned outage windows ahead"
          trendPositive={upcoming === 0}
        />
        <KpiCard
          label="Est. monthly bill (400 kWh)"
          value={tariff ? `R${formatNumber(monthlyBill)}` : "—"}
          hint={tariff ? `At ${tariff} c/kWh` : "Tariff unavailable"}
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartPanel
          title={`Monthly outage hours — ${prevYear} vs ${currentYear}`}
        >
          <MultiBarChart
            data={monthlyCompare}
            xKey="month"
            keys={[
              { key: prevYear, color: "#dc2626", name: prevYear },
              { key: currentYear, color: "#059669", name: currentYear },
            ]}
          />
        </ChartPanel>
        <ChartPanel title={`Energy generation mix ${mixYear}`}>
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
        source={data.source ?? "Eskom · CSIR · DMRE"}
        scrapedAt={data.scraped_at}
        isLive={data.is_live}
      />
    </div>
  );
}
