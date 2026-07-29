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

type EducationData = {
  source?: string;
  scraped_at?: string;
  is_live?: boolean;
  exam_year?: number;
  national_pass_rate_pct?: number;
  bachelor_pass_pct?: number;
  total_wrote?: number;
  distinction_rate_pct?: number;
  provinces?: Record<
    string,
    { pass_rate?: number; bachelor_pct?: number; wrote?: number }
  >;
  subjects?: Record<string, { pass_rate?: number; hq_pass_rate?: number }>;
  pass_trend?: Record<string, number>;
  bachelor_trend?: Record<string, number>;
};

export default async function EducationPage({
  searchParams,
}: {
  searchParams: Promise<{ province?: string }>;
}) {
  const { province: provinceParam } = await searchParams;
  const province = resolveProvince(provinceParam);
  const d = await loadJson<EducationData>("education");
  const prov = province !== "All Provinces" ? d?.provinces?.[province] : null;
  const year = d?.exam_year ?? 2024;

  const passRate = prov?.pass_rate ?? d?.national_pass_rate_pct ?? 87.3;
  const bachelor = prov?.bachelor_pct ?? d?.bachelor_pass_pct ?? 45.6;

  const passByProv = PROVINCE_LIST.map((p) => ({
    province: p,
    pass: d?.provinces?.[p]?.pass_rate ?? 0,
  }));

  const subjects = Object.entries(d?.subjects ?? {})
    .map(([name, s]) => ({
      subject: name,
      pass: s.pass_rate ?? 0,
    }))
    .sort((a, b) => b.pass - a.pass)
    .slice(0, 8);

  const years = Object.keys(d?.pass_trend ?? {}).sort();
  const trend = years.map((y) => ({
    year: y,
    pass: d?.pass_trend?.[y] ?? 0,
    bachelor: d?.bachelor_trend?.[y] ?? 0,
  }));

  return (
    <div>
      <PageHeader
        title="Education & Matric Data"
        description={`NSC ${year} results — pass rates and university readiness by province.`}
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label={`Pass rate (${provinceLabel(province)})`}
          value={`${passRate}%`}
          hint={`National NSC ${year}`}
        />
        <KpiCard
          label="Bachelor pass rate"
          value={`${bachelor}%`}
          hint="University-ready cohort"
          trendPositive={bachelor >= 40}
        />
        <KpiCard
          label="Candidates wrote"
          value={formatNumber(d?.total_wrote ?? 756000)}
          hint={`Distinctions: ${d?.distinction_rate_pct ?? 7.2}%`}
        />
        <KpiCard
          label="National pass rate"
          value={`${d?.national_pass_rate_pct ?? 87.3}%`}
          hint="All provinces combined"
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartPanel title="Matric pass rate by province">
          <SimpleBarChart
            data={passByProv}
            xKey="province"
            yKey="pass"
            color="#2563eb"
          />
        </ChartPanel>
        <ChartPanel title="Key subject pass rates">
          <SimpleBarChart
            data={subjects}
            xKey="subject"
            yKey="pass"
            layout="vertical"
            color="#7c3aed"
          />
        </ChartPanel>
      </div>

      {trend.length > 0 && (
        <div className="mt-6">
          <ChartPanel title="Pass rate trend">
            <SimpleLineChart
              data={trend}
              xKey="year"
              lines={[
                { key: "pass", color: "#2563eb", name: "Pass %" },
                { key: "bachelor", color: "#059669", name: "Bachelor %" },
              ]}
            />
          </ChartPanel>
        </div>
      )}

      <SourceBadge
        source={d?.source ?? "DBE NSC"}
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
