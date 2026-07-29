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
import { formatCurrency, formatNumber } from "@/shared/utils";

type PropertyData = {
  source?: string;
  scraped_at?: string;
  is_live?: boolean;
  national?: {
    median_price_r?: number;
    yoy_growth_pct?: number;
    avg_rental_yield_pct?: number;
    days_on_market?: number;
    prime_rate_pct?: number;
  };
  provinces?: Record<
    string,
    {
      median_price_r?: number;
      yoy_growth_pct?: number;
      rental_yield_pct?: number;
      days_on_market?: number;
    }
  >;
  price_trend?: Record<string, Record<string, number>>;
};

export default async function PropertyPage({
  searchParams,
}: {
  searchParams: Promise<{ province?: string }>;
}) {
  const { province: provinceParam } = await searchParams;
  const province = resolveProvince(provinceParam);
  const d = await loadJson<PropertyData>("property");
  const nat = d?.national ?? {};
  const prov = province !== "All Provinces" ? d?.provinces?.[province] : null;

  const median = prov?.median_price_r ?? nat.median_price_r ?? 1280000;
  const yieldPct = prov?.rental_yield_pct ?? nat.avg_rental_yield_pct ?? 8.4;
  const yoy = prov?.yoy_growth_pct ?? nat.yoy_growth_pct ?? 2.3;
  const dom = prov?.days_on_market ?? nat.days_on_market ?? 76;

  const scatter = PROVINCE_LIST.map((p) => ({
    province: p,
    yield: d?.provinces?.[p]?.rental_yield_pct ?? 0,
    growth: d?.provinces?.[p]?.yoy_growth_pct ?? 0,
  }));

  const medians = PROVINCE_LIST.map((p) => ({
    province: p,
    median_k: (d?.provinces?.[p]?.median_price_r ?? 0) / 1000,
  }));

  const trendQuarters = ["Q1-24", "Q2-24", "Q3-24", "Q4-24"];
  const trendData = trendQuarters.map((q) => ({
    quarter: q,
    National: d?.price_trend?.National?.[q] ?? 0,
    "Western Cape": d?.price_trend?.["Western Cape"]?.[q] ?? 0,
    Gauteng: d?.price_trend?.Gauteng?.[q] ?? 0,
  }));

  return (
    <div>
      <PageHeader
        title="Property Prices & Rental"
        description="Median prices, rental yields, and market velocity — what matters for buy vs rent decisions."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label={`Median price (${provinceLabel(province)})`}
          value={formatCurrency(median)}
          hint="Published barometer figures"
        />
        <KpiCard
          label="Rental yield"
          value={`${yieldPct}%`}
          hint="Gross yield — income investors watch this"
          trendPositive={yieldPct >= 8}
          trend={yieldPct >= 8 ? "Above national average" : "Below national average"}
        />
        <KpiCard
          label="YoY price growth"
          value={`${yoy}%`}
          trendPositive={yoy > 0}
          trend={yoy > 0 ? "Prices rising" : "Prices flat or falling"}
        />
        <KpiCard
          label="Days on market"
          value={formatNumber(dom)}
          hint={`Prime rate context: ${nat.prime_rate_pct ?? 10.25}%`}
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartPanel
          title="Yield vs growth by province"
          description="Higher yield often trades off with slower capital growth"
        >
          <SimpleBarChart
            data={scatter.map((s) => ({
              province: s.province,
              yield: s.yield,
            }))}
            xKey="province"
            yKey="yield"
            color="#059669"
          />
        </ChartPanel>
        <ChartPanel
          title="Median price by province (R thousands)"
          description="Where entry prices differ most"
        >
          <SimpleBarChart
            data={medians}
            xKey="province"
            yKey="median_k"
            color="#2563eb"
          />
        </ChartPanel>
      </div>

      <div className="mt-6">
        <ChartPanel title="Price index trend (selected regions)">
          <SimpleLineChart
            data={trendData}
            xKey="quarter"
            lines={[
              { key: "National", color: "#64748b", name: "National" },
              { key: "Western Cape", color: "#2563eb", name: "Western Cape" },
              { key: "Gauteng", color: "#d97706", name: "Gauteng" },
            ]}
          />
        </ChartPanel>
      </div>

      <SourceBadge
        source={d?.source ?? "FNB · Lightstone · PayProp"}
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
