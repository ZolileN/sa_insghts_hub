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
  };
  health_system?: {
    maternal_mortality_per_100k?: number;
    under5_mortality_per_1000?: number;
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
  hiv_trend?: Record<string, number>;
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
  const prov = province !== "All Provinces" ? d?.provinces?.[province] : null;

  const hivPrev = prov?.hiv_prevalence_pct ?? hiv.prevalence_15_49_pct ?? 18.3;
  const doctors = prov?.doctors_per_100k ?? 0;

  const doctorsByProv = PROVINCE_LIST.map((p) => ({
    province: p,
    doctors: d?.provinces?.[p]?.doctors_per_100k ?? 0,
  }));

  const tbByProv = PROVINCE_LIST.map((p) => ({
    province: p,
    tb: d?.provinces?.[p]?.tb_per_100k ?? 0,
  }));

  const years = Object.keys(d?.hiv_trend ?? {}).sort();
  const epidemicTrend = years.map((y) => ({
    year: y,
    plhiv: d?.hiv_trend?.[y] ?? 0,
    art: d?.art_trend?.[y] ?? 0,
  }));

  return (
    <div>
      <PageHeader
        title="Healthcare & Disease Burden"
        description="HIV, TB, and health system capacity — provincial pressure on clinics and outcomes."
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
          value={province !== "All Provinces" ? formatNumber(doctors) : "Varies"}
          hint={d?.health_system?.nhi_implementation ?? "NHI Phase 1"}
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
        source={d?.source ?? "NDOH · SANAC"}
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
