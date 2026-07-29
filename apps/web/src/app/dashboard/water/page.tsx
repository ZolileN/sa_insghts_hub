import {
  ChartPanel,
  KpiCard,
  PageHeader,
  SourceBadge,
} from "@/components/dashboard/page-parts";
import {
  ColoredBarChart,
  MultiBarChart,
} from "@/components/charts/recharts";
import { PROVINCE_LIST } from "@/shared/data/constants";
import { loadJson } from "@/shared/data/load";
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

  return (
    <div>
      <PageHeader
        title="Water & Service Delivery"
        description="Dam and reservoir levels — water security for metros and agriculture. Sources: DWS NIWIS, OpenUp, Cape Town open data."
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
          label="Report freshness"
          value={d?.is_live ? "Live DWS feed" : "Cached snapshot"}
          hint={d?.report_date ?? "Weekly state of reservoirs"}
          trendPositive={d?.is_live ?? false}
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartPanel title="Major dam levels (%)">
          <ColoredBarChart data={dams} xKey="name" yKey="level" />
        </ChartPanel>
        <ChartPanel title="Province dam levels — week on week">
          <MultiBarChart
            data={provinceLevels}
            xKey="province"
            keys={[
              { key: "thisWeek", color: "#2563eb", name: "This week" },
              { key: "lastWeek", color: "#94a3b8", name: "Last week" },
            ]}
          />
        </ChartPanel>
      </div>

      <div className="mt-6">
        <ChartPanel title="Province dam levels — vs last year">
          <MultiBarChart
            data={provinceLevels}
            xKey="province"
            keys={[
              { key: "thisWeek", color: "#2563eb", name: "This week" },
              { key: "lastYear", color: "#d97706", name: "Last year" },
            ]}
          />
        </ChartPanel>
      </div>

      <SourceBadge
        source={`${d?.source ?? "DWS NIWIS"} · OpenUp · Cape Town open data`}
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
