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
import { dashNum, dashPct, dashFixed, dashText } from "@/shared/data/display";
import { provinceRank } from "@/shared/data/intelligence";
import { loadJson } from "@/shared/data/load";
import { buildProvinceMarkers } from "@/shared/data/province-map";
import { provinceLabel, resolveProvince } from "@/shared/data/province";
import { formatNumber } from "@/shared/utils";

type EmploymentData = {
  source?: string;
  scraped_at?: string;
  is_live?: boolean;
  period?: string;
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
      expanded_unemployment?: number;
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

  const unemp = prov?.unemployment ?? d?.unemployment_rate_pct;
  const youth = prov?.youth_unemployment ?? d?.youth_unemployment_pct;
  const expanded =
    prov?.expanded_unemployment ?? d?.expanded_unemployment_pct;
  const income = prov?.median_income_r;
  const gini = d?.gini_coefficient;
  const minWage = d?.national_min_wage_hourly_r;
  const youthGap =
    unemp != null && youth != null ? youth - unemp : null;

  const unempByProv = Object.fromEntries(
    PROVINCE_LIST.map((p) => [p, d?.provinces?.[p]?.unemployment ?? 0]),
  );
  const unempRank =
    province !== "All Provinces"
      ? provinceRank(unempByProv, province, true)
      : null;

  const unempByProvChart = PROVINCE_LIST.map((p) => ({
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

  const monthlyMinWage =
    minWage != null ? Math.round(minWage * 160) : null;

  const mapMarkers = buildProvinceMarkers(unempByProv);

  return (
    <div>
      <PageHeader
        title="Unemployment & Income"
        description={`Stats SA QLFS — labour market health and household income. ${dashText(d?.period)}`}
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label={`Unemployment (${provinceLabel(province)})`}
          value={dashPct(unemp)}
          hint="Official unemployment rate"
        />
        <KpiCard
          label="Youth unemployment"
          value={dashPct(youth)}
          hint="Ages 15–24 — policy-critical"
          trendPositive={false}
        />
        <KpiCard
          label="Employed persons"
          value={
            d?.employed_millions != null ? `${d.employed_millions}m` : "—"
          }
          hint={
            expanded != null
              ? `Expanded unemployment: ${expanded}%`
              : "Expanded unemployment"
          }
        />
        <KpiCard
          label={`Median income (${provinceLabel(province)})`}
          value={income != null ? `R${formatNumber(income)}` : "—"}
          hint={
            minWage != null ? `Min wage: R${minWage}/hr` : "Median monthly income"
          }
        />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Gini coefficient"
          value={dashFixed(gini, 2)}
          hint="Income inequality (0 = equal)"
          trendPositive={gini != null && gini < 0.65}
          trend={
            gini == null
              ? undefined
              : gini >= 0.65
                ? "High inequality"
                : "Moderate inequality"
          }
        />
        <KpiCard
          label={`Expanded unemployment (${provinceLabel(province)})`}
          value={dashPct(expanded)}
          hint="Includes discouraged work-seekers"
          trendPositive={expanded != null && expanded < 40}
        />
        <KpiCard
          label="Youth unemployment gap"
          value={
            youthGap != null ? `+${youthGap.toFixed(1)}pp` : "—"
          }
          hint="Youth rate minus overall unemployment"
          trendPositive={youthGap != null && youthGap < 25}
        />
        <KpiCard
          label={
            unempRank != null
              ? `Unemployment rank (${province})`
              : "National min wage (monthly)"
          }
          value={
            unempRank != null
              ? `#${unempRank} of 9`
              : monthlyMinWage != null
                ? `R${formatNumber(monthlyMinWage)}`
                : "—"
          }
          hint={
            unempRank != null
              ? "Higher rank = worse labour market"
              : "~160 hours at sectoral floor"
          }
        />
      </div>

      <ChartPanel
        title="Employment map"
        description="Unemployment % by province — click to focus a region"
        className="mt-6"
      >
        <GeoMap
          markers={mapMarkers}
          province={province}
          city="All areas"
          valueLabel="unemployment %"
        />
      </ChartPanel>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartPanel
          title="Unemployment rate by province"
          description="Click a bar to drill into provincial labour market"
        >
          <DrillableSimpleBarChart
            data={unempByProvChart}
            xKey="province"
            yKey="rate"
            color="#dc2626"
            province={province}
            city="All areas"
            drillLevel="province"
          />
        </ChartPanel>
        <ChartPanel
          title="Median monthly income by province (R)"
          description="Click a bar to drill into provincial income"
        >
          <DrillableSimpleBarChart
            data={incomeByProv}
            xKey="province"
            yKey="income"
            color="#059669"
            province={province}
            city="All areas"
            drillLevel="province"
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
        source={`${d?.source ?? "Stats SA QLFS"} · Wazimap · labour.gov.za`}
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
