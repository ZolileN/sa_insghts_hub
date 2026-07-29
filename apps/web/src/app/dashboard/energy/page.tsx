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
    calendar_year_hours?: Record<string, number>;
    current_fy_hours?: number;
  };
};

/** All years with monthly hour breakdowns (legacy + modern keys). */
function monthlyYears(d: EnergyData): string[] {
  const years = new Set<string>();
  for (const y of Object.keys(d.monthly_hours_by_year ?? {})) years.add(y);
  if (d.monthly_hours_2023) years.add("2023");
  if (d.monthly_hours_2024) years.add("2024");
  return [...years].sort();
}

function monthlyHoursForYear(d: EnergyData, year: string): Record<string, number> {
  if (d.monthly_hours_by_year?.[year]) return d.monthly_hours_by_year[year];
  if (year === "2024" && d.monthly_hours_2024) return d.monthly_hours_2024;
  if (year === "2023" && d.monthly_hours_2023) return d.monthly_hours_2023;
  return {};
}

/** Latest calendar year in annual totals (scraped live + cache). */
function primaryOutageYear(d: EnergyData): string {
  const years = Object.keys(d.annual_totals ?? {})
    .filter((y) => /^\d{4}$/.test(y))
    .sort();
  if (years.length) return years[years.length - 1];
  return String(new Date().getFullYear());
}

function latestTariffYear(d: EnergyData): string | null {
  const keys = Object.keys(d.electricity_tariff_history ?? {}).filter((y) =>
    /^\d{4}$/.test(y),
  );
  return keys.length ? keys.sort().pop() ?? null : null;
}

function energyMixForYear(d: EnergyData, year: string): Record<string, number> {
  if (d.energy_mix_by_year?.[year]) return d.energy_mix_by_year[year];
  if (year === "2024" && d.energy_mix_pct_2024) return d.energy_mix_pct_2024;
  return {};
}

function latestMixYear(d: EnergyData): string | null {
  const years = Object.keys(d.energy_mix_by_year ?? {}).filter((y) =>
    /^\d{4}$/.test(y),
  );
  if (d.energy_mix_pct_2024) years.push("2024");
  const unique = [...new Set(years)].sort();
  return unique.length ? unique[unique.length - 1] : null;
}

export default async function EnergyPage() {
  const d = await loadJson<EnergyData>("energy");
  const data: EnergyData = d ?? {};
  const stage = data.current_stage ?? 0;

  const outageYear = primaryOutageYear(data);
  const prevOutageYear = String(Number(outageYear) - 1);

  const annualHours =
    data.annual_totals?.[outageYear] ??
    data.fy_stats?.loadshedding_hours_fy ??
    Object.values(monthlyHoursForYear(data, outageYear)).reduce((a, b) => a + b, 0);

  const hoursPrev =
    data.annual_totals?.[prevOutageYear] ??
    Object.values(monthlyHoursForYear(data, prevOutageYear)).reduce((a, b) => a + b, 0);

  const hoursReductionPct =
    hoursPrev > 0 ? pctChange(annualHours, hoursPrev) : null;

  const tariffYear = latestTariffYear(data) ?? outageYear;
  const tariff = data.electricity_tariff_history?.[tariffYear] ?? 0;

  const mixYear = latestMixYear(data);
  const mix = mixYear ? energyMixForYear(data, mixYear) : {};

  const upcoming = data.upcoming_outages?.length ?? 0;
  const monthlyBill = estimateMonthlyElectricityBill(400, tariff);
  const streak = data.fy_stats?.consecutive_days_without;

  const monthlyYearsList = monthlyYears(data);
  const chartPrevYear =
    monthlyYearsList.length >= 2
      ? monthlyYearsList[monthlyYearsList.length - 2]
      : null;
  const chartCurrentYear =
    monthlyYearsList.length >= 1
      ? monthlyYearsList[monthlyYearsList.length - 1]
      : null;

  const monthlyCompare =
    chartPrevYear && chartCurrentYear
      ? Object.keys(monthlyHoursForYear(data, chartCurrentYear)).map((m) => ({
          month: m,
          [chartPrevYear]: monthlyHoursForYear(data, chartPrevYear)[m] ?? 0,
          [chartCurrentYear]: monthlyHoursForYear(data, chartCurrentYear)[m] ?? 0,
        }))
      : [];

  const monthlyChartHistorical =
    chartCurrentYear != null && chartCurrentYear !== outageYear;

  const annual = Object.entries(data.annual_totals ?? {})
    .filter(([year]) => /^\d{4}$/.test(year))
    .map(([year, h]) => ({ year, hours: h }));

  const mixChart = Object.entries(mix).map(([name, pct]) => ({
    name,
    pct,
  }));

  const tariffTrend = Object.entries(data.electricity_tariff_history ?? {})
    .filter(([year]) => /^\d{4}$/.test(year))
    .map(([year, c]) => ({ year, tariff: c }));

  const outageHint = data.fy_stats?.financial_year
    ? `FY ${data.fy_stats.financial_year} · Eskom media`
    : data.annual_totals?.[outageYear] != null
      ? "Calendar year · scraped totals"
      : "Scheduled outage hours";

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
          label={`Outage hours ${outageYear}`}
          value={formatNumber(annualHours)}
          hint={outageHint}
          trendPositive={hoursPrev > 0 && annualHours < hoursPrev}
          trend={
            hoursPrev > 0
              ? `vs ${formatNumber(hoursPrev)} hrs in ${prevOutageYear}`
              : undefined
          }
        />
        <KpiCard
          label="Electricity tariff"
          value={tariff ? `${tariff} c/kWh` : "—"}
          hint={
            tariffYear === String(new Date().getFullYear())
              ? `Latest published (${tariffYear})`
              : `Latest published (${tariffYear}) — check NERSA for newer`
          }
        />
        <KpiCard
          label="Solar in mix"
          value={mix.Solar != null ? `${mix.Solar}%` : "—"}
          hint={
            mixYear
              ? `Coal ${mix.Coal ?? 0}% · mix ${mixYear}`
              : "Generation mix not in cache"
          }
        />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label={`Outage change vs ${prevOutageYear}`}
          value={
            hoursReductionPct != null
              ? `${hoursReductionPct.toFixed(0)}%`
              : "—"
          }
          hint={`${outageYear} hours compared to ${prevOutageYear}`}
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
        {monthlyCompare.length > 0 && chartPrevYear && chartCurrentYear ? (
          <ChartPanel
            title={`Monthly outage hours — ${chartPrevYear} vs ${chartCurrentYear}`}
            description={
              monthlyChartHistorical
                ? `Historical monthly series (live scrape has ${outageYear} annual total: ${formatNumber(annualHours)} hrs).`
                : undefined
            }
          >
            <MultiBarChart
              data={monthlyCompare}
              xKey="month"
              keys={[
                { key: chartPrevYear, color: "#dc2626", name: chartPrevYear },
                { key: chartCurrentYear, color: "#059669", name: chartCurrentYear },
              ]}
            />
          </ChartPanel>
        ) : (
          <ChartPanel title="Monthly outage hours">
            <p className="text-sm text-muted-foreground">
              No monthly breakdown in cache. Annual total for {outageYear}:{" "}
              {formatNumber(annualHours)} hrs (from live Eskom scrape).
            </p>
          </ChartPanel>
        )}
        {mixChart.length > 0 && mixYear ? (
          <ChartPanel
            title={`Energy generation mix ${mixYear}`}
            description={
              mixYear !== String(new Date().getFullYear())
                ? "Latest published annual mix in cache — not scraped live each run."
                : undefined
            }
          >
            <SimplePieChart data={mixChart} nameKey="name" valueKey="pct" />
          </ChartPanel>
        ) : (
          <ChartPanel title="Energy generation mix">
            <p className="text-sm text-muted-foreground">
              Generation mix not available from live scrape.
            </p>
          </ChartPanel>
        )}
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
