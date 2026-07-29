import {
  ChartPanel,
  KpiCard,
  PageHeader,
  SourceBadge,
} from "@/components/dashboard/page-parts";
import { DrillableMultiBarChart } from "@/components/charts/drillable-multi-bar-chart";
import { DrillableSimpleBarChart } from "@/components/charts/drillable-simple-bar-chart";
import { GeoMap } from "@/components/maps/crime-map";
import {
  ColoredBarChart,
  MultiBarChart,
} from "@/components/charts/recharts";
import { PROVINCE_LIST } from "@/shared/data/constants";
import { loadJson } from "@/shared/data/load";
import { buildProvinceMarkers } from "@/shared/data/province-map";
import { provinceLabel, resolveProvince } from "@/shared/data/province";
import { formatNumber } from "@/shared/utils";

type WaterData = {
  source?: string;
  scraped_at?: string;
  is_live?: boolean;
  report_date?: string;
  national_avg_pct?: number;
  provinces?: Record<
    string,
    {
      this_week_pct?: number;
      last_week_pct?: number;
      last_year_pct?: number;
    }
  >;
  dams?: Array<{
    name: string;
    this_week_pct?: number;
    last_week_pct?: number;
    capacity_mm3?: number;
  }>;
};

export default async function WaterPage({
  searchParams,
}: {
  searchParams: Promise<{ province?: string }>;
}) {
  const { province: provinceParam } = await searchParams;
  const province = resolveProvince(provinceParam);
  const d = await loadJson<WaterData>("water");
  const national = d?.national_avg_pct ?? 76.2;
  const prov = province !== "All Provinces" ? d?.provinces?.[province] : null;
  const level = prov?.this_week_pct ?? national;
  const wowDelta =
    prov?.this_week_pct != null && prov?.last_week_pct != null
      ? prov.this_week_pct - prov.last_week_pct
      : null;
  const yoyDelta =
    prov?.this_week_pct != null && prov?.last_year_pct != null
      ? prov.this_week_pct - prov.last_year_pct
      : null;

  const totalCapacity = (d?.dams ?? []).reduce(
    (a, dam) => a + (dam.capacity_mm3 ?? 0),
    0,
  );

  const lowestProv = PROVINCE_LIST.reduce(
    (min, p) => {
      const v = d?.provinces?.[p]?.this_week_pct ?? 100;
      return v < min.val ? { name: p, val: v } : min;
    },
    { name: "—", val: 100 },
  );

  const provinceLevels = PROVINCE_LIST.map((p) => ({
    province: p,
    thisWeek: d?.provinces?.[p]?.this_week_pct ?? 0,
    lastWeek: d?.provinces?.[p]?.last_week_pct ?? 0,
    lastYear: d?.provinces?.[p]?.last_year_pct ?? 0,
  }));

  const dams = (d?.dams ?? []).map((dam) => ({
    name: dam.name,
    level: dam.this_week_pct ?? 0,
  }));

  const droughtStress = PROVINCE_LIST.filter(
    (p) => (d?.provinces?.[p]?.this_week_pct ?? 100) < 60,
  ).length;

  const lowestDam = (d?.dams ?? []).reduce<{ name: string; level: number }>(
    (min, dam) => {
      const level = dam.this_week_pct ?? 100;
      return level < min.level ? { name: dam.name, level } : min;
    },
    { name: "—", level: 100 },
  );

  const damByProv = Object.fromEntries(
    PROVINCE_LIST.map((p) => [p, d?.provinces?.[p]?.this_week_pct ?? 0]),
  );
  const mapMarkers = buildProvinceMarkers(damByProv);

  return (
    <div>
      <PageHeader
        title="Water & Service Delivery"
        description="Dam and reservoir levels — water security for metros and agriculture."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label={`Dam level (${provinceLabel(province)})`}
          value={`${level}%`}
          hint="This week average"
          trend={
            wowDelta != null
              ? `${wowDelta >= 0 ? "+" : ""}${wowDelta.toFixed(1)}pp vs last week`
              : undefined
          }
          trendPositive={wowDelta != null ? wowDelta >= 0 : undefined}
        />
        <KpiCard
          label="National dam average"
          value={`${national}%`}
          hint="All provinces weighted"
        />
        <KpiCard
          label="Major dams tracked"
          value={`${d?.dams?.length ?? 0}`}
          hint="Including Vaal, Theewaterskloof, Gariep"
        />
        <KpiCard
          label="Lowest province"
          value={lowestProv.name}
          hint={`${lowestProv.val}% storage — watch stressed regions`}
        />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label={`YoY storage change (${provinceLabel(province)})`}
          value={
            yoyDelta != null
              ? `${yoyDelta >= 0 ? "+" : ""}${yoyDelta.toFixed(1)}pp`
              : "—"
          }
          hint="Versus same week last year"
          trendPositive={yoyDelta != null ? yoyDelta >= 0 : undefined}
        />
        <KpiCard
          label="Total capacity tracked"
          value={`${totalCapacity.toFixed(0)} km³`}
          hint="Major dam combined capacity"
        />
        <KpiCard
          label="Drought-stress provinces"
          value={formatNumber(droughtStress)}
          hint="Provinces below 60% storage"
          trendPositive={droughtStress === 0}
        />
        <KpiCard
          label="Most stressed major dam"
          value={lowestDam.name}
          hint={`${lowestDam.level}% full this week`}
          trendPositive={lowestDam.level >= 60}
          trend={lowestDam.level < 60 ? "Below comfort threshold" : "Adequate storage"}
        />
      </div>

      <ChartPanel
        title="Water map"
        description="Dam storage % by province — click to compare regions"
        className="mt-6"
      >
        <GeoMap
          markers={mapMarkers}
          province={province}
          city="All areas"
          valueLabel="dam level %"
        />
      </ChartPanel>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartPanel title="Major dam levels (%)">
          <ColoredBarChart data={dams} xKey="name" yKey="level" />
        </ChartPanel>
        <ChartPanel
          title="Province dam levels — week on week"
          description="Click a province group to drill down"
        >
          <DrillableMultiBarChart
            data={provinceLevels}
            xKey="province"
            keys={[
              { key: "thisWeek", color: "#2563eb", name: "This week" },
              { key: "lastWeek", color: "#94a3b8", name: "Last week" },
            ]}
            province={province}
            city="All areas"
            drillLevel="province"
          />
        </ChartPanel>
      </div>

      <div className="mt-6">
        <ChartPanel
          title="Province dam levels — vs last year"
          description="Year-on-year storage comparison by province"
        >
          <DrillableMultiBarChart
            data={provinceLevels}
            xKey="province"
            keys={[
              { key: "thisWeek", color: "#2563eb", name: "This week" },
              { key: "lastYear", color: "#d97706", name: "Last year" },
            ]}
            province={province}
            city="All areas"
            drillLevel="province"
          />
        </ChartPanel>
      </div>

      <SourceBadge
        source="Department of Water & Sanitation · OpenUp · Cape Town open data"
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
