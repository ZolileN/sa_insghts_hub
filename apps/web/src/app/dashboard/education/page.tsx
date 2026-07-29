import {
  ChartPanel,
  KpiCard,
  PageHeader,
  SourceBadge,
} from "@/components/dashboard/page-parts";
import { DrillableSimpleBarChart } from "@/components/charts/drillable-simple-bar-chart";
import { GeoMap } from "@/components/maps/crime-map";
import {
  SimpleBarChart,
  SimpleLineChart,
} from "@/components/charts/recharts";
import { PROVINCE_LIST } from "@/shared/data/constants";
import { loadJson } from "@/shared/data/load";
import { buildProvinceMarkers } from "@/shared/data/province-map";
import { provinceLabel, resolveProvince } from "@/shared/data/province";
import { dashNum, dashPct } from "@/shared/data/display";
import { formatNumber } from "@/shared/utils";

type EducationData = {
  source?: string;
  scraped_at?: string;
  is_live?: boolean;
  exam_year?: number;
  national_pass_rate_pct?: number;
  bachelor_pass_pct?: number;
  total_wrote?: number;
  total_passed?: number;
  distinction_rate_pct?: number;
  provinces?: Record<
    string,
    { pass_rate?: number; bachelor_pct?: number; wrote?: number }
  >;
  subjects?: Record<string, { pass_rate?: number; hq_pass_rate?: number }>;
  trend?: Record<string, { pass_rate?: number; bachelor?: number }>;
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
  const year = d?.exam_year;
  const passRate = prov?.pass_rate ?? d?.national_pass_rate_pct;
  const bachelor = prov?.bachelor_pct ?? d?.bachelor_pass_pct;
  const bachelorGap = bachelor != null ? bachelor - 50 : null;
  const maths = d?.subjects?.Mathematics;
  const mathsHq = maths?.hq_pass_rate;

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

  const trendEntries = Object.entries(d?.trend ?? {}).sort(([a], [b]) =>
    a.localeCompare(b),
  );
  const trend = trendEntries.map(([y, v]) => ({
    year: y,
    pass: v.pass_rate ?? 0,
    bachelor: v.bachelor ?? 0,
  }));

  const passRatePrior =
    trendEntries.length >= 2
      ? trendEntries[trendEntries.length - 2][1].pass_rate ?? 0
      : null;
  const passMomentum =
    passRatePrior != null && passRate != null
      ? passRate - passRatePrior
      : null;

  const passByProvMap = Object.fromEntries(
    PROVINCE_LIST.map((p) => [p, d?.provinces?.[p]?.pass_rate ?? 0]),
  );
  const mapMarkers = buildProvinceMarkers(passByProvMap);

  return (
    <div>
      <PageHeader
        title="Education & Matric Data"
        description={
          year != null
            ? `NSC ${year} results — pass rates, subject performance, and university readiness.`
            : "NSC results — pass rates, subject performance, and university readiness."
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label={`Pass rate (${provinceLabel(province)})`}
          value={dashPct(passRate)}
          hint={year != null ? `National NSC ${year}` : "National NSC"}
        />
        <KpiCard
          label="Bachelor pass rate"
          value={dashPct(bachelor)}
          hint="University-ready cohort"
          trendPositive={bachelor != null && bachelor >= 40}
        />
        <KpiCard
          label="Candidates wrote"
          value={dashNum(d?.total_wrote)}
          hint={
            d?.distinction_rate_pct != null
              ? `Distinctions: ${d.distinction_rate_pct}%`
              : "Candidates who wrote"
          }
        />
        <KpiCard
          label="National pass rate"
          value={dashPct(d?.national_pass_rate_pct)}
          hint="All provinces combined"
        />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Candidates passed"
          value={dashNum(d?.total_passed)}
          hint={
            d?.total_passed != null && d?.total_wrote != null && d.total_wrote > 0
              ? `${((d.total_passed / d.total_wrote) * 100).toFixed(1)}% of cohort`
              : "Candidates who passed"
          }
          trendPositive={
            d?.total_passed != null && d.total_passed > 600000
          }
        />
        <KpiCard
          label="Distinction rate"
          value={dashPct(d?.distinction_rate_pct)}
          hint="Top achievers nationally"
          trendPositive={
            d?.distinction_rate_pct != null && d.distinction_rate_pct >= 7
          }
        />
        <KpiCard
          label="Maths higher-grade pass"
          value={dashPct(mathsHq)}
          hint={
            maths?.pass_rate != null
              ? `Overall maths pass: ${maths.pass_rate}%`
              : "Mathematics higher-grade"
          }
          trendPositive={mathsHq != null && mathsHq >= 30}
        />
        <KpiCard
          label="Bachelor readiness gap"
          value={
            bachelorGap != null
              ? `${bachelorGap >= 0 ? "+" : ""}${bachelorGap.toFixed(1)}pp`
              : "—"
          }
          hint="Vs 50% university-ready benchmark"
          trendPositive={bachelorGap != null && bachelorGap >= -5}
          trend={
            passMomentum != null
              ? `${passMomentum >= 0 ? "+" : ""}${passMomentum.toFixed(1)}pp pass vs prior year`
              : undefined
          }
        />
      </div>

      <ChartPanel
        title="Education map"
        description="Matric pass rate by province — click to compare regions"
        className="mt-6"
      >
        <GeoMap
          markers={mapMarkers}
          province={province}
          city="All areas"
          valueLabel="pass rate %"
        />
      </ChartPanel>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartPanel
          title="Matric pass rate by province"
          description="Click a bar to drill into provincial results"
        >
          <DrillableSimpleBarChart
            data={passByProv}
            xKey="province"
            yKey="pass"
            color="#2563eb"
            province={province}
            city="All areas"
            drillLevel="province"
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
        source={`${d?.source ?? "DBE NSC"} · EMIS master lists · DHET`}
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
