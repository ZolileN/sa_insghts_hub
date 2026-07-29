import {
  ChartPanel,
  KpiCard,
  PageHeader,
  SourceBadge,
} from "@/components/dashboard/page-parts";
import { DrillableSimpleBarChart } from "@/components/charts/drillable-simple-bar-chart";
import { GeoMap } from "@/components/maps/crime-map";
import {
  SimpleLineChart,
} from "@/components/charts/recharts";
import { PROVINCE_LIST } from "@/shared/data/constants";
import { loadJson } from "@/shared/data/load";
import { buildProvinceMarkers } from "@/shared/data/province-map";
import { provinceLabel, resolveProvince } from "@/shared/data/province";
import { formatNumber } from "@/shared/utils";

type HealthData = {
  source?: string;
  scraped_at?: string;
  is_live?: boolean;
  dhis2_connected?: boolean;
  hiv?: {
    plhiv_millions?: number;
    prevalence_15_49_pct?: number;
    on_art_millions?: number;
    art_coverage_pct?: number;
    report_year?: string;
    annual?: Record<string, Record<string, number>>;
    new_infections_2023?: number;
    aids_deaths_2023?: number;
  };
  tb?: {
    incidence_per_100k?: number;
    treatment_success_pct?: number;
    tb_hiv_coinfection_pct?: number;
    report_year?: string;
    annual?: Record<string, Record<string, number>>;
    notifications_2023?: number;
    dr_tb_cases_2023?: number;
  };
  health_system?: {
    maternal_mortality_per_100k?: number;
    under5_mortality_per_1000?: number;
    public_hospitals?: number;
    private_hospitals?: number;
    nhi_implementation?: string;
  };
  provinces?: Record<
    string,
    {
      hiv_prevalence_pct?: number;
      tb_per_100k?: number;
      doctors_per_100k?: number;
      art_coverage_pct?: number;
    }
  >;
  plhiv_trend?: Record<string, number>;
  art_trend?: Record<string, number>;
  surveillance?: {
    report_week?: number;
    report_period?: string;
    measles_confirmed_ytd?: number;
    measles_new_since_prior_report?: number;
    rubella_confirmed_ytd?: number;
    top_province_measles?: string;
    latest_reports?: Array<{ title: string; url: string; date: string }>;
  };
};

function yearMetric(
  section: Record<string, unknown> | undefined,
  metric: string,
): { year: string | null; value: number | null } {
  if (!section) return { year: null, value: null };

  const annual = section.annual as Record<string, Record<string, number>> | undefined;
  const reportYear = section.report_year as string | undefined;
  const years = Object.keys(annual ?? {})
    .filter((y) => /^\d{4}$/.test(y))
    .sort();
  const year = reportYear ?? years.at(-1) ?? null;

  if (year && annual?.[year]?.[metric] != null) {
    return { year, value: annual[year][metric] };
  }

  for (const [k, v] of Object.entries(section)) {
    const m = k.match(new RegExp(`^${metric}_(\\d{4})$`));
    if (m && typeof v === "number") return { year: m[1], value: v };
  }

  return { year: null, value: null };
}

export default async function HealthPage({
  searchParams,
}: {
  searchParams: Promise<{ province?: string }>;
}) {
  const { province: provinceParam } = await searchParams;
  const province = resolveProvince(provinceParam);
  const d = await loadJson<HealthData>("health");
  const hiv = d?.hiv ?? {};
  const tb = d?.tb ?? {};
  const system = d?.health_system ?? {};
  const prov = province !== "All Provinces" ? d?.provinces?.[province] : null;

  const hivPrev = prov?.hiv_prevalence_pct ?? hiv.prevalence_15_49_pct;
  const artCoverage = prov?.art_coverage_pct ?? hiv.art_coverage_pct;
  const doctors = prov?.doctors_per_100k ?? 0;

  const newHiv = yearMetric(hiv as Record<string, unknown>, "new_infections");
  const aidsDeaths = yearMetric(hiv as Record<string, unknown>, "aids_deaths");
  const drTb = yearMetric(tb as Record<string, unknown>, "dr_tb_cases");

  const doctorsByProv = PROVINCE_LIST.map((p) => ({
    province: p,
    doctors: d?.provinces?.[p]?.doctors_per_100k ?? 0,
  }));

  const tbByProv = PROVINCE_LIST.map((p) => ({
    province: p,
    tb: d?.provinces?.[p]?.tb_per_100k ?? 0,
  }));

  const plhivTrend = d?.plhiv_trend ?? {};
  const artTrendData = d?.art_trend ?? {};
  const years = Object.keys(plhivTrend).sort();
  const epidemicTrend = years.map((y) => ({
    year: y,
    plhiv: plhivTrend[y] ?? 0,
    art: artTrendData[y] ?? 0,
  }));

  const surv = d?.surveillance ?? {};

  const hivByProvMap = Object.fromEntries(
    PROVINCE_LIST.map((p) => [p, d?.provinces?.[p]?.hiv_prevalence_pct ?? 0]),
  );
  const mapMarkers = buildProvinceMarkers(hivByProvMap);

  return (
    <div>
      <PageHeader
        title="Healthcare & Disease Burden"
        description="HIV, TB, and health system capacity — prevalence, treatment coverage, and provincial burden."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label={`HIV prevalence (${provinceLabel(province)})`}
          value={hivPrev != null ? `${hivPrev}%` : "—"}
          hint="Ages 15–49"
        />
        <KpiCard
          label="On ART nationally"
          value={hiv.on_art_millions != null ? `${hiv.on_art_millions}m` : "—"}
          hint={
            hiv.art_coverage_pct != null
              ? `${hiv.art_coverage_pct}% treatment coverage`
              : "Treatment coverage"
          }
        />
        <KpiCard
          label="TB incidence"
          value={tb.incidence_per_100k != null ? `${tb.incidence_per_100k}` : "—"}
          hint="Per 100,000 population"
        />
        <KpiCard
          label="Doctors per 100k"
          value={
            province !== "All Provinces"
              ? formatNumber(doctors)
              : "Varies"
          }
          hint={system.nhi_implementation ?? "NHI Phase 1"}
        />
      </div>

      {(surv.measles_confirmed_ytd != null || surv.latest_reports?.length) && (
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            label="Measles confirmed (YTD)"
            value={formatNumber(surv.measles_confirmed_ytd ?? 0)}
            hint={surv.report_period ?? "NICD laboratory surveillance"}
            trendPositive={(surv.measles_confirmed_ytd ?? 9999) < 3500}
          />
          <KpiCard
            label="New measles cases"
            value={formatNumber(surv.measles_new_since_prior_report ?? 0)}
            hint="Since prior weekly outbreak report"
          />
          <KpiCard
            label="Rubella confirmed (YTD)"
            value={formatNumber(surv.rubella_confirmed_ytd ?? 0)}
            hint="NICD weekly surveillance"
          />
          <KpiCard
            label="NICD report week"
            value={surv.report_week != null ? `Week ${surv.report_week}` : "—"}
            hint={surv.top_province_measles ?? "Provincial outbreak tracking"}
          />
        </div>
      )}

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label={
            newHiv.year
              ? `New HIV infections (${newHiv.year})`
              : "New HIV infections"
          }
          value={newHiv.value != null ? formatNumber(newHiv.value) : "—"}
          hint={
            newHiv.year
              ? `Annual estimate · latest in cache (${newHiv.year})`
              : "Not in cache"
          }
          trendPositive={newHiv.value != null && newHiv.value < 150000}
        />
        <KpiCard
          label={
            aidsDeaths.year ? `AIDS deaths (${aidsDeaths.year})` : "AIDS deaths"
          }
          value={aidsDeaths.value != null ? formatNumber(aidsDeaths.value) : "—"}
          hint={
            aidsDeaths.year
              ? `Mortality burden · latest in cache (${aidsDeaths.year})`
              : "Not in cache"
          }
          trendPositive={aidsDeaths.value != null && aidsDeaths.value < 60000}
        />
        <KpiCard
          label="Maternal mortality"
          value={
            system.maternal_mortality_per_100k != null
              ? `${system.maternal_mortality_per_100k}`
              : "—"
          }
          hint="Per 100,000 live births"
          trendPositive={
            system.maternal_mortality_per_100k != null &&
            system.maternal_mortality_per_100k < 120
          }
        />
        <KpiCard
          label={`ART coverage (${provinceLabel(province)})`}
          value={artCoverage != null ? `${artCoverage}%` : "—"}
          hint={
            tb.treatment_success_pct != null
              ? `TB treatment success: ${tb.treatment_success_pct}%`
              : "TB treatment success"
          }
          trendPositive={artCoverage != null && artCoverage >= 70}
        />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Under-5 mortality"
          value={
            system.under5_mortality_per_1000 != null
              ? `${system.under5_mortality_per_1000}`
              : "—"
          }
          hint="Per 1,000 live births"
          trendPositive={
            system.under5_mortality_per_1000 != null &&
            system.under5_mortality_per_1000 < 35
          }
        />
        <KpiCard
          label="TB–HIV co-infection"
          value={
            tb.tb_hiv_coinfection_pct != null ? `${tb.tb_hiv_coinfection_pct}%` : "—"
          }
          hint="Of TB patients co-infected"
        />
        <KpiCard
          label="Hospital beds (public)"
          value={
            system.public_hospitals != null
              ? formatNumber(system.public_hospitals)
              : "—"
          }
          hint={
            system.private_hospitals != null
              ? `${system.private_hospitals} private hospitals`
              : "Public hospitals"
          }
        />
        <KpiCard
          label={
            drTb.year ? `Drug-resistant TB (${drTb.year})` : "Drug-resistant TB"
          }
          value={drTb.value != null ? formatNumber(drTb.value) : "—"}
          hint={
            drTb.year
              ? `Latest annual report in cache (${drTb.year})`
              : "Not in cache"
          }
          trendPositive={drTb.value != null && drTb.value < 7000}
        />
      </div>

      <ChartPanel
        title="Health map"
        description="HIV prevalence by province — click a marker or chart bar to focus a province"
        className="mt-6"
      >
        <GeoMap
          markers={mapMarkers}
          province={province}
          city="All areas"
          valueLabel="HIV prevalence %"
        />
      </ChartPanel>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartPanel
          title="Doctors per 100k by province"
          description="Click a bar to drill into provincial view"
        >
          <DrillableSimpleBarChart
            data={doctorsByProv}
            xKey="province"
            yKey="doctors"
            color="#2563eb"
            province={province}
            city="All areas"
            drillLevel="province"
          />
        </ChartPanel>
        <ChartPanel
          title="TB incidence by province"
          description="Click a bar to drill into provincial view"
        >
          <DrillableSimpleBarChart
            data={tbByProv}
            xKey="province"
            yKey="tb"
            color="#dc2626"
            province={province}
            city="All areas"
            drillLevel="province"
          />
        </ChartPanel>
      </div>

      {epidemicTrend.length > 0 && (
        <div className="mt-6">
          <ChartPanel title="HIV treatment scale-up (millions)">
            <SimpleLineChart
              data={epidemicTrend}
              xKey="year"
              lines={[
                { key: "plhiv", color: "#dc2626", name: "PLHIV" },
                { key: "art", color: "#059669", name: "On ART" },
              ]}
            />
          </ChartPanel>
        </div>
      )}

      <SourceBadge
        source="National Department of Health · SANAC · SAMRC · NICD"
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
