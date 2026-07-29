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

type EmploymentData = {
  source?: string;
  scraped_at?: string;
  is_live?: boolean;
  unemployment_rate_pct?: number;
  youth_unemployment_pct?: number;
  expanded_unemployment_pct?: number;
  employed_millions?: number;
  gini_coefficient?: number;
  national_min_wage_hourly_r?: number;
  provinces?: Record<
    string,
    {
      unemployment?: number;
      youth_unemployment?: number;
      median_income_r?: number;
    }
  >;
  trend?: Record<string, number>;
};

export default async function EmploymentPage({
  searchParams,
}: {
  searchParams: Promise<{ province?: string }>;
}) {
  const { province: provinceParam } = await searchParams;
  const province = resolveProvince(provinceParam);
  const d = await loadJson<EmploymentData>("employment");
  const prov = province !== "All Provinces" ? d?.provinces?.[province] : null;

  const unemp = prov?.unemployment ?? d?.unemployment_rate_pct ?? 32.9;
  const youth = prov?.youth_unemployment ?? d?.youth_unemployment_pct ?? 60.7;
  const income = prov?.median_income_r ?? 9800;

  const unempByProv = PROVINCE_LIST.map((p) => ({
    province: p,
    rate: d?.provinces?.[p]?.unemployment ?? 0,
  }));

  const incomeByProv = PROVINCE_LIST.map((p) => ({
    province: p,
    income: d?.provinces?.[p]?.median_income_r ?? 0,
  }));

  const trend = Object.entries(d?.trend ?? {}).map(([q, rate]) => ({
    quarter: q,
    rate,
  }));

  return (
    <div>
      <PageHeader
        title="Unemployment & Income"
        description="Stats SA QLFS — labour market health and household income by province."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label={`Unemployment (${provinceLabel(province)})`}
          value={`${unemp}%`}
          hint="Official unemployment rate"
        />
        <KpiCard
          label="Youth unemployment"
          value={`${youth}%`}
          hint="Ages 15–24 — policy-critical"
          trendPositive={false}
        />
        <KpiCard
          label="Employed persons"
          value={`${d?.employed_millions ?? 16.7}m`}
          hint={`Expanded unemployment: ${d?.expanded_unemployment_pct ?? 43.1}%`}
        />
        <KpiCard
          label={`Median income (${provinceLabel(province)})`}
          value={`R${formatNumber(income)}`}
          hint={`Min wage: R${d?.national_min_wage_hourly_r ?? 28.79}/hr`}
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartPanel title="Unemployment rate by province">
          <SimpleBarChart
            data={unempByProv}
            xKey="province"
            yKey="rate"
            color="#dc2626"
          />
        </ChartPanel>
        <ChartPanel title="Median monthly income by province (R)">
          <SimpleBarChart
            data={incomeByProv}
            xKey="province"
            yKey="income"
            color="#059669"
          />
        </ChartPanel>
      </div>

      <div className="mt-6">
        <ChartPanel title="National unemployment trend (quarterly)">
          <SimpleLineChart
            data={trend}
            xKey="quarter"
            lines={[{ key: "rate", color: "#2563eb", name: "Unemployment %" }]}
          />
        </ChartPanel>
      </div>

      <SourceBadge
        source={d?.source ?? "Stats SA QLFS"}
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
