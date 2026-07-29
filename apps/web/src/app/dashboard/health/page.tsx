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
import { PROVINCE_LIST } from "@/shared/data/constants";
import { loadJson } from "@/shared/data/load";
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
    new_infections_2023?: number;
    aids_deaths_2023?: number;
  };
  tb?: {
    incidence_per_100k?: number;
    treatment_success_pct?: number;
    tb_hiv_coinfection_pct?: number;
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
};

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

  const hivPrev = prov?.hiv_prevalence_pct ?? hiv.prevalence_15_49_pct ?? 18.3;
  const artCoverage =
    prov?.art_coverage_pct ?? hiv.art_coverage_pct ?? 73;
  const doctors = prov?.doctors_per_100k ?? 0;

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

  return (
    <div>
      <PageHeader
        title="Healthcare & Disease Burden"
        description="HIV, TB, and health system capacity. Sources: SAMRC, NICD, Healthsites.io, SANAC, DHIS2."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label={`HIV prevalence (${provinceLabel(province)})`}
          value={`${hivPrev}%`}
          hint="Ages 15–49"
        />
        <KpiCard
          label="On ART nationally"
          value={`${hiv.on_art_millions ?? 5.7}m`}
          hint={`${hiv.art_coverage_pct ?? 73}% treatment coverage`}
        />
        <KpiCard
          label="TB incidence"
          value={`${tb.incidence_per_100k ?? 468}`}
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

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="New HIV infections (2023)"
          value={formatNumber(hiv.new_infections_2023 ?? 140000)}
          hint="Annual new infections estimate"
          trendPositive={(hiv.new_infections_2023 ?? 140000) < 150000}
        />
        <KpiCard
          label="AIDS deaths (2023)"
          value={formatNumber(hiv.aids_deaths_2023 ?? 57000)}
          hint="Mortality burden"
          trendPositive={(hiv.aids_deaths_2023 ?? 57000) < 60000}
        />
        <KpiCard
          label="Maternal mortality"
          value={`${system.maternal_mortality_per_100k ?? 118}`}
          hint="Per 100,000 live births"
          trendPositive={(system.maternal_mortality_per_100k ?? 118) < 120}
        />
        <KpiCard
          label={`ART coverage (${provinceLabel(province)})`}
          value={`${artCoverage}%`}
          hint={`TB treatment success: ${tb.treatment_success_pct ?? 81}%`}
          trendPositive={artCoverage >= 70}
        />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Under-5 mortality"
          value={`${system.under5_mortality_per_1000 ?? 34}`}
          hint="Per 1,000 live births"
          trendPositive={(system.under5_mortality_per_1000 ?? 34) < 35}
        />
        <KpiCard
          label="TB–HIV co-infection"
          value={`${tb.tb_hiv_coinfection_pct ?? 60}%`}
          hint="Of TB patients co-infected"
        />
        <KpiCard
          label="Hospital beds (public)"
          value={formatNumber(system.public_hospitals ?? 407)}
          hint={`${system.private_hospitals ?? 211} private hospitals`}
        />
        <KpiCard
          label="DHIS2 facility feed"
          value={d?.dhis2_connected ? "Connected" : "Cached"}
          hint="Facility-level indicators (planned)"
          trendPositive={d?.dhis2_connected ?? false}
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartPanel title="Doctors per 100k by province">
          <SimpleBarChart
            data={doctorsByProv}
            xKey="province"
            yKey="doctors"
            color="#2563eb"
          />
        </ChartPanel>
        <ChartPanel title="TB incidence by province">
          <SimpleBarChart
            data={tbByProv}
            xKey="province"
            yKey="tb"
            color="#dc2626"
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
        source={`${d?.source ?? "NDOH · SANAC"} · SAMRC · NICD · Healthsites.io`}
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
