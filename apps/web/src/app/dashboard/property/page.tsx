import { GeoMap } from "@/components/maps/crime-map";
import { DrillableSimpleBarChart } from "@/components/charts/drillable-simple-bar-chart";
import {
  ChartPanel,
  KpiCard,
  PageHeader,
  SourceBadge,
} from "@/components/dashboard/page-parts";
import {
  MultiBarChart,
  SimpleLineChart,
} from "@/components/charts/recharts";
import { PROVINCE_LIST } from "@/shared/data/constants";
import { loadJson } from "@/shared/data/load";
import { resolveProvince } from "@/shared/data/province";
import {
  affordabilityVsNational,
  estimateMonthlyBond,
  estimateMonthlyRent,
  rentVsBuyRatio,
  resolveCity,
  resolveSuburb,
  scopeLabel,
  type PropertyMetro,
  type PropertyNational,
} from "@/shared/data/property";
import {
  districtCoords,
  provinceCoords,
  type CrimeMapMarker,
} from "@/shared/data/sa-geo";
import { formatCurrency, formatNumber } from "@/shared/utils";

type PropertyData = {
  source?: string;
  scraped_at?: string;
  is_live?: boolean;
  national?: PropertyNational;
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
  price_trend_r000?: Record<string, number>;
  metros?: Record<string, Record<string, PropertyMetro>>;
};

function scopeMetrics(
  d: PropertyData,
  province: string,
  city: string,
  suburb: string,
): {
  median: number;
  yieldPct: number;
  yoy: number;
  dom: number;
  rentR: number;
  airbnb?: number;
  buildingPlans?: number;
} {
  const nat = d.national ?? {};
  const nationalMedian = nat.median_price_r ?? 1320000;
  const prime = nat.prime_rate_pct ?? 10.5;

  if (province === "All Provinces") {
    const median = nationalMedian;
    const yieldPct = nat.avg_rental_yield_pct ?? 8.2;
    return {
      median,
      yieldPct,
      yoy: nat.yoy_growth_pct ?? 2.8,
      dom: nat.days_on_market ?? 72,
      rentR: estimateMonthlyRent(median, yieldPct),
      airbnb: undefined,
      buildingPlans: undefined,
    };
  }

  const metroMap = d.metros?.[province] ?? {};
  const metroNames = Object.keys(metroMap);

  if (city !== "All areas" && metroMap[city]) {
    const metro = metroMap[city];
    const suburbs = metro.suburbs ?? {};

    if (suburb !== "All suburbs" && suburbs[suburb]) {
      const sub = suburbs[suburb];
      const median =
        sub.median_price_r ??
        metro.median_price_r ??
        d.provinces?.[province]?.median_price_r ??
        nationalMedian;
      const yieldPct =
        sub.rental_yield_pct ?? metro.rental_yield_pct ?? 8.2;
      const rentR =
        sub.estimated_monthly_rent_r ?? estimateMonthlyRent(median, yieldPct);
      return {
        median,
        yieldPct,
        yoy: metro.yoy_growth_pct ?? d.provinces?.[province]?.yoy_growth_pct ?? 2,
        dom:
          sub.days_on_market ??
          metro.days_on_market ??
          d.provinces?.[province]?.days_on_market ??
          72,
        rentR,
        airbnb: metro.airbnb_listings,
        buildingPlans: metro.building_plans_yoy_pct,
      };
    }

    const median = metro.median_price_r ?? d.provinces?.[province]?.median_price_r ?? nationalMedian;
    const yieldPct =
      metro.rental_yield_pct ?? d.provinces?.[province]?.rental_yield_pct ?? 8.2;
    const rentR =
      metro.estimated_monthly_rent_r ?? estimateMonthlyRent(median, yieldPct);
    return {
      median,
      yieldPct,
      yoy: metro.yoy_growth_pct ?? d.provinces?.[province]?.yoy_growth_pct ?? 2,
      dom: metro.days_on_market ?? d.provinces?.[province]?.days_on_market ?? 72,
      rentR,
      airbnb: metro.airbnb_listings,
      buildingPlans: metro.building_plans_yoy_pct,
    };
  }

  const prov = d.provinces?.[province];
  const median = prov?.median_price_r ?? nationalMedian;
  const yieldPct = prov?.rental_yield_pct ?? nat.avg_rental_yield_pct ?? 8.2;
  return {
    median,
    yieldPct,
    yoy: prov?.yoy_growth_pct ?? 2,
    dom: prov?.days_on_market ?? 72,
    rentR: estimateMonthlyRent(median, yieldPct),
    airbnb: undefined,
    buildingPlans: undefined,
  };
}

function buildMapMarkers(
  d: PropertyData,
  province: string,
  city: string,
  suburb: string,
): CrimeMapMarker[] {
  const provData = d.provinces ?? {};

  if (province === "All Provinces") {
    return PROVINCE_LIST.map((p) => ({
      id: p,
      label: p,
      longitude: provinceCoords(p)[0],
      latitude: provinceCoords(p)[1],
      value: (provData[p]?.median_price_r ?? 0) / 1000,
      kind: "province" as const,
    })).filter((m) => m.value > 0);
  }

  const metroMap = d.metros?.[province] ?? {};

  if (city === "All areas") {
    return Object.entries(metroMap).map(([metro, data], i) => {
      const [lng, lat] = districtCoords(metro, province, i);
      return {
        id: `${province}-${metro}`,
        label: metro,
        longitude: lng,
        latitude: lat,
        value: (data.median_price_r ?? 0) / 1000,
        kind: "district" as const,
      };
    }).filter((m) => m.value > 0);
  }

  const metro = metroMap[city];
  const suburbs = metro?.suburbs ?? {};

  if (suburb !== "All suburbs" && suburbs[suburb]) {
    const sub = suburbs[suburb];
    const [lng, lat] = districtCoords(city, province, 0);
    return [
      {
        id: `${city}-${suburb}`,
        label: suburb,
        longitude: lng,
        latitude: lat,
        value: (sub.median_price_r ?? 0) / 1000,
        kind: "suburb" as const,
      },
    ].filter((m) => m.value > 0);
  }

  if (Object.keys(suburbs).length > 0) {
    return Object.entries(suburbs).map(([name, sub], i) => {
      const [lng, lat] = districtCoords(city, province, i);
      return {
        id: `${city}-${name}`,
        label: name,
        longitude: lng,
        latitude: lat,
        value: (sub.median_price_r ?? 0) / 1000,
        kind: "suburb" as const,
      };
    }).filter((m) => m.value > 0);
  }

  const [lng, lat] = districtCoords(city, province, 0);
  return [
    {
      id: `${province}-${city}`,
      label: city,
      longitude: lng,
      latitude: lat,
      value: (metro?.median_price_r ?? 0) / 1000,
      kind: "district" as const,
    },
  ].filter((m) => m.value > 0);
}

export default async function PropertyPage({
  searchParams,
}: {
  searchParams: Promise<{ province?: string; city?: string; suburb?: string }>;
}) {
  const {
    province: provinceParam,
    city: cityParam,
    suburb: suburbParam,
  } = await searchParams;
  const province = resolveProvince(provinceParam);
  const d = await loadJson<PropertyData>("property");
  const nat = d?.national ?? {};

  const metroMap = d?.metros?.[province] ?? {};
  const metroNames =
    province !== "All Provinces"
      ? Object.keys(metroMap).sort((a, b) => a.localeCompare(b))
      : [];

  const city = resolveCity(cityParam, metroNames);
  const suburbNames =
    city !== "All areas"
      ? Object.keys(metroMap[city]?.suburbs ?? {}).sort((a, b) =>
          a.localeCompare(b),
        )
      : [];
  const suburb = resolveSuburb(suburbParam, suburbNames);
  const label = scopeLabel(province, city, suburb);
  const metrics = scopeMetrics(d ?? {}, province, city, suburb);

  const nationalMedian = nat.median_price_r ?? 1320000;
  const prime = nat.prime_rate_pct ?? 10.5;
  const monthlyBond = estimateMonthlyBond(metrics.median, prime);
  const rentBuyRatio = rentVsBuyRatio(metrics.rentR, monthlyBond);
  const affordability = affordabilityVsNational(metrics.median, nationalMedian);
  const bondApproval = nat.bond_approval_rate_pct ?? 62;
  const transferThreshold = nat.transfer_duty_threshold_r ?? 1210000;
  const householdIncome = nat.avg_household_income_r ?? 282000;
  const priceToIncome = Math.round((metrics.median / householdIncome) * 10) / 10;
  const capRateSpread = Math.round((metrics.yieldPct - prime) * 10) / 10;
  const annualRent = metrics.rentR * 12;

  const scatter = PROVINCE_LIST.map((p) => ({
    province: p,
    yield: d?.provinces?.[p]?.rental_yield_pct ?? 0,
    growth: d?.provinces?.[p]?.yoy_growth_pct ?? 0,
  }));

  const medians = PROVINCE_LIST.map((p) => ({
    province: p,
    median_k: (d?.provinces?.[p]?.median_price_r ?? 0) / 1000,
  }));

  const metroMedians =
    province !== "All Provinces"
      ? metroNames.map((metro) => ({
          metro,
          median_k: (metroMap[metro]?.median_price_r ?? 0) / 1000,
        }))
      : [];

  const suburbMedians =
    province !== "All Provinces" && city !== "All areas"
      ? Object.entries(metroMap[city]?.suburbs ?? {}).map(([name, sub]) => ({
          suburb: name,
          median_k: (sub.median_price_r ?? 0) / 1000,
        }))
      : [];

  const trendQuarters = Object.keys(
    d?.price_trend?.National ?? d?.price_trend_r000 ?? {},
  ).slice(-8);
  const trendData = trendQuarters.map((q) => ({
    quarter: q,
    National: d?.price_trend?.National?.[q] ?? d?.price_trend_r000?.[q] ?? 0,
    "Western Cape": d?.price_trend?.["Western Cape"]?.[q] ?? 0,
    Gauteng: d?.price_trend?.Gauteng?.[q] ?? 0,
  }));

  const mapMarkers = buildMapMarkers(d ?? {}, province, city, suburb);
  const mapDescription =
    province === "All Provinces"
      ? "Median price (R thousands) by province — blue markers scale with price"
      : city === "All areas"
        ? `Metro median prices in ${province} — orange markers`
        : suburb !== "All suburbs"
          ? `Suburb focus — ${suburb} in ${city}`
          : `Suburb medians in ${city} — red markers`;

  const yieldCompare =
    province === "All Provinces"
      ? scatter.map((s) => ({ area: s.province, yield: s.yield }))
      : city === "All areas"
        ? metroNames.map((m) => ({
            area: m,
            yield: metroMap[m]?.rental_yield_pct ?? 0,
          }))
        : Object.entries(metroMap[city]?.suburbs ?? {}).map(([name, sub]) => ({
            area: name,
            yield: sub.rental_yield_pct ?? 0,
          }));

  return (
    <div>
      <PageHeader
        title="Property Prices & Rental"
        description="Median prices, rental yields, affordability, and market velocity — drill down: province → metro → suburb. Built for buy vs rent decisions."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label={`Median price (${label})`}
          value={formatCurrency(metrics.median)}
          hint="FNB/Lightstone barometer & metro estimates"
        />
        <KpiCard
          label="Est. monthly bond"
          value={formatCurrency(monthlyBond)}
          hint={`90% loan · ${prime}% prime · 20 years`}
          trend={monthlyBond < metrics.rentR ? "Bond cheaper than rent" : "Rent cheaper than bond"}
          trendPositive={monthlyBond < metrics.rentR}
        />
        <KpiCard
          label="Est. monthly rent"
          value={formatCurrency(metrics.rentR)}
          hint={`Gross yield ${metrics.yieldPct}%`}
        />
        <KpiCard
          label="Rental yield"
          value={`${metrics.yieldPct}%`}
          trendPositive={metrics.yieldPct >= 8}
          trend={
            metrics.yieldPct >= 8
              ? "Income-friendly market"
              : "Growth-focused market"
          }
        />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <KpiCard
          label="Rent vs bond ratio"
          value={`${(rentBuyRatio * 100).toFixed(0)}%`}
          hint="Rent as % of bond payment — under 100% favours buying"
          trendPositive={rentBuyRatio < 1}
          trend={
            rentBuyRatio < 0.85
              ? "Strong buy signal"
              : rentBuyRatio < 1
                ? "Rent below bond"
                : "Rent exceeds bond"
          }
        />
        <KpiCard
          label="Affordability index"
          value={`${affordability}`}
          hint="Local median vs national (100 = national average)"
          trendPositive={affordability <= 100}
          trend={
            affordability > 120
              ? "Premium market"
              : affordability < 90
                ? "Value market"
                : "Near national average"
          }
        />
        <KpiCard
          label="Price-to-income"
          value={`${priceToIncome}x`}
          hint={`Median vs household income (~R${formatNumber(householdIncome)})`}
          trendPositive={priceToIncome <= 5}
        />
        <KpiCard
          label="Cap rate vs prime"
          value={`${capRateSpread > 0 ? "+" : ""}${capRateSpread}pp`}
          hint={`Gross yield ${metrics.yieldPct}% vs prime ${prime}%`}
          trendPositive={capRateSpread > 0}
          trend={
            capRateSpread > 0
              ? "Yield beats borrowing cost"
              : "Prime exceeds gross yield"
          }
        />
        <KpiCard
          label="Est. annual rental"
          value={formatCurrency(annualRent)}
          hint={`${formatCurrency(metrics.rentR)}/month gross income`}
          trendPositive={annualRent > monthlyBond * 12}
        />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Days on market"
          value={formatNumber(metrics.dom)}
          hint={`Bond approval ~${bondApproval}% nationally`}
          trendPositive={metrics.dom < 70}
          trend={metrics.yoy > 0 ? `Prices +${metrics.yoy}% YoY` : "Flat prices"}
        />
        <KpiCard
          label="YoY price growth"
          value={`${metrics.yoy}%`}
          trendPositive={metrics.yoy > 0}
          trend={metrics.yoy > 2 ? "Above inflation target" : "Moderate growth"}
        />
        <KpiCard
          label="Transfer duty threshold"
          value={formatCurrency(transferThreshold)}
          hint={
            metrics.median > transferThreshold
              ? "Median above zero-duty band"
              : "Median within zero-duty band"
          }
        />
        <KpiCard
          label="Bond approval rate"
          value={`${bondApproval}%`}
          hint="National mortgage approval proxy"
          trendPositive={bondApproval >= 60}
        />
      </div>

      {(metrics.airbnb != null || metrics.buildingPlans != null) && (
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {metrics.airbnb != null && (
            <KpiCard
              label="Short-stay supply (Airbnb)"
              value={formatNumber(metrics.airbnb)}
              hint="Inside Airbnb listing count (metro proxy)"
              trend="Higher supply can mean more rental competition"
            />
          )}
          {metrics.buildingPlans != null && (
            <KpiCard
              label="Building plans growth"
              value={`${metrics.buildingPlans}% YoY`}
              hint="Stats SA P0142 / municipal open data proxy"
              trendPositive={metrics.buildingPlans > 0}
              trend={
                metrics.buildingPlans > 2
                  ? "New supply rising"
                  : "Limited new supply"
              }
            />
          )}
        </div>
      )}

      <ChartPanel
        title="Property map"
        description={mapDescription + " — click markers to drill down"}
        className="mt-6"
      >
        <GeoMap
          markers={mapMarkers}
          province={province}
          city={city}
          suburb={suburb}
          valueLabel="median (R thousands)"
        />
      </ChartPanel>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        {province === "All Provinces" ? (
          <ChartPanel
            title="Median price by province (R thousands)"
            description="Click a bar or map marker to drill into province metros"
          >
            <DrillableSimpleBarChart
              data={medians}
              xKey="province"
              yKey="median_k"
              color="#2563eb"
              province={province}
              city={city}
              drillLevel="province"
            />
          </ChartPanel>
        ) : city === "All areas" ? (
          <ChartPanel
            title={`Median price by metro — ${province}`}
            description="Click to drill into suburb-level medians"
          >
            <DrillableSimpleBarChart
              data={metroMedians}
              xKey="metro"
              yKey="median_k"
              layout="vertical"
              color="#2563eb"
              province={province}
              city={city}
              drillLevel="district"
            />
          </ChartPanel>
        ) : (
          <ChartPanel
            title={`Suburb medians — ${city}`}
            description="Neighbourhood-level price spread"
          >
            <DrillableSimpleBarChart
              data={suburbMedians}
              xKey="suburb"
              yKey="median_k"
              layout="vertical"
              color="#2563eb"
              province={province}
              city={city}
              drillLevel="district"
            />
          </ChartPanel>
        )}

        <ChartPanel
          title="Rental yield by area"
          description="Gross yield — click bars to drill when at national or provincial view"
        >
          <DrillableSimpleBarChart
            data={yieldCompare}
            xKey="area"
            yKey="yield"
            layout="vertical"
            color="#059669"
            province={province}
            city={city}
            drillLevel={
              province === "All Provinces" ? "province" : "district"
            }
          />
        </ChartPanel>

        <ChartPanel
          title="Yield vs growth by province"
          description="Higher yield often trades off with slower capital growth"
        >
          <MultiBarChart
            data={scatter}
            xKey="province"
            keys={[
              { key: "yield", color: "#059669", name: "Yield %" },
              { key: "growth", color: "#d97706", name: "YoY growth %" },
            ]}
          />
        </ChartPanel>

        <ChartPanel title="Price index trend (R thousands)">
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
        source={
          d?.source ??
          "FNB · Lightstone · PayProp · Inside Airbnb · Stats SA · municipal open data"
        }
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
