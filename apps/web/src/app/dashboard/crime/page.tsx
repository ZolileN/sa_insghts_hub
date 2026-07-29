import { Suspense } from "react";
import { CityFilter } from "@/components/layout/city-filter";
import {
  ChartPanel,
  KpiCard,
  PageHeader,
  SourceBadge,
} from "@/components/dashboard/page-parts";
import {
  MultiBarChart,
  SimpleBarChart,
} from "@/components/charts/recharts";
import { PROVINCE_LIST } from "@/shared/data/constants";
import {
  CRIME_CHART_PALETTE,
  CRIME_KPI_KEYS,
  CRIME_TYPE_LABELS,
  resolveCity,
  scopeLabel,
} from "@/shared/data/crime";
import { loadJson } from "@/shared/data/load";
import { provinceLabel, resolveProvince } from "@/shared/data/province";
import { formatNumber } from "@/shared/utils";

type CrimeCounts = Record<string, number>;

type StationRow = {
  name: string;
  district: string;
  murders: number;
  crimes: CrimeCounts;
};

type Hotspot = {
  rank: number;
  station: string;
  district: string;
  province: string;
  serious_crime: number;
};

type CrimeData = {
  source?: string;
  scraped_at?: string;
  period?: string;
  is_live?: boolean;
  national_totals?: CrimeCounts;
  provinces?: Record<string, CrimeCounts>;
  districts?: Record<string, Record<string, CrimeCounts>>;
  stations?: Record<string, StationRow[]>;
  national_hotspots?: Hotspot[];
  crime_types?: string[];
};

function sumCrimes(rows: CrimeCounts | undefined, key: string): number {
  return rows?.[key] ?? 0;
}

function scopeCounts(
  d: CrimeData,
  province: string,
  city: string,
): CrimeCounts {
  const nat = d.national_totals ?? {};
  if (province === "All Provinces") return nat;

  if (city !== "All areas" && d.districts?.[province]?.[city]) {
    return d.districts[province][city];
  }

  return d.provinces?.[province] ?? nat;
}

export default async function CrimePage({
  searchParams,
}: {
  searchParams: Promise<{ province?: string; city?: string }>;
}) {
  const { province: provinceParam, city: cityParam } = await searchParams;
  const province = resolveProvince(provinceParam);
  const d = await loadJson<CrimeData>("crime");
  const period = d?.period ?? "Latest period";
  const provData = d?.provinces ?? {};

  const districtMap = d?.districts?.[province] ?? {};
  const districtNames =
    province !== "All Provinces"
      ? Object.keys(districtMap).sort((a, b) => a.localeCompare(b))
      : [];
  const city = resolveCity(cityParam, districtNames);

  const counts = scopeCounts(d ?? {}, province, city);
  const label = scopeLabel(province, city);

  const provinceMurders = PROVINCE_LIST.map((p) => ({
    province: p,
    murders: provData[p]?.Murder ?? 0,
  }));

  const districtMurders =
    province !== "All Provinces"
      ? districtNames.map((district) => ({
          district,
          murders: districtMap[district]?.Murder ?? 0,
        }))
      : [];

  const stationRows: StationRow[] = (() => {
    if (province === "All Provinces") return [];
    const all = d?.stations?.[province] ?? [];
    if (city === "All areas") return all.slice(0, 15);
    return all
      .filter((s) => s.district === city)
      .slice(0, 15);
  })();

  const violentMix =
    province === "All Provinces"
      ? PROVINCE_LIST.map((p) => ({
          province: p,
          Murder: provData[p]?.Murder ?? 0,
          "Sexual offences": provData[p]?.["Sexual offences"] ?? 0,
          Carjacking: provData[p]?.Carjacking ?? 0,
        }))
      : districtMurders.map((row) => ({
          province: row.district,
          Murder: districtMap[row.district]?.Murder ?? 0,
          "Sexual offences":
            districtMap[row.district]?.["Sexual offences"] ?? 0,
          Carjacking: districtMap[row.district]?.Carjacking ?? 0,
        }));

  const propertyMix =
    province === "All Provinces"
      ? PROVINCE_LIST.map((p) => ({
          province: p,
          "Residential burglary":
            provData[p]?.["Residential burglary"] ?? 0,
          "Robbery aggravating":
            provData[p]?.["Robbery aggravating"] ?? 0,
        }))
      : districtMurders.map((row) => ({
          province: row.district,
          "Residential burglary":
            districtMap[row.district]?.["Residential burglary"] ?? 0,
          "Robbery aggravating":
            districtMap[row.district]?.["Robbery aggravating"] ?? 0,
        }));

  const hotspots = (d?.national_hotspots ?? []).slice(0, 15);

  return (
    <div>
      <PageHeader
        title="Crime Statistics"
        description={`SAPS quarterly data — ${period}. Drill down: province → city/metro → police precinct.`}
      >
        {province !== "All Provinces" && districtNames.length > 0 && (
          <Suspense fallback={null}>
            <CityFilter districts={districtNames} />
          </Suspense>
        )}
      </PageHeader>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {CRIME_KPI_KEYS.map((key) => (
          <KpiCard
            key={key}
            label={CRIME_TYPE_LABELS[key] ?? key}
            value={formatNumber(sumCrimes(counts, key))}
            hint={label}
          />
        ))}
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        {province === "All Provinces" ? (
          <ChartPanel
            title="Murders by province"
            description="Absolute murder counts for the reporting quarter"
          >
            <SimpleBarChart
              data={provinceMurders}
              xKey="province"
              yKey="murders"
              layout="vertical"
              color="#dc2626"
            />
          </ChartPanel>
        ) : city === "All areas" ? (
          <ChartPanel
            title={`Murders by area — ${province}`}
            description="City and metro districts within the province"
          >
            <SimpleBarChart
              data={districtMurders}
              xKey="district"
              yKey="murders"
              layout="vertical"
              color="#dc2626"
            />
          </ChartPanel>
        ) : (
          <ChartPanel
            title={`Top precincts — ${city}`}
            description="Police station murder counts in the selected area"
          >
            <SimpleBarChart
              data={stationRows.map((s) => ({
                station: s.name,
                murders: s.murders,
              }))}
              xKey="station"
              yKey="murders"
              layout="vertical"
              color="#dc2626"
            />
          </ChartPanel>
        )}

        <ChartPanel
          title="Violent crime mix"
          description={
            province === "All Provinces"
              ? "Murder, sexual offences, and carjacking by province"
              : "Violent crime by city/metro district"
          }
        >
          <MultiBarChart
            data={violentMix}
            xKey="province"
            keys={[
              { key: "Murder", color: CRIME_CHART_PALETTE[0], name: "Murder" },
              {
                key: "Sexual offences",
                color: CRIME_CHART_PALETTE[1],
                name: "Sexual offences",
              },
              {
                key: "Carjacking",
                color: CRIME_CHART_PALETTE[2],
                name: "Carjacking",
              },
            ]}
          />
        </ChartPanel>

        <ChartPanel
          title="Property & aggravated crime"
          description="Burglary and aggravated robbery volumes"
        >
          <MultiBarChart
            data={propertyMix}
            xKey="province"
            keys={[
              {
                key: "Residential burglary",
                color: CRIME_CHART_PALETTE[3],
                name: "Residential burglary",
              },
              {
                key: "Robbery aggravating",
                color: CRIME_CHART_PALETTE[4],
                name: "Aggravated robbery",
              },
            ]}
          />
        </ChartPanel>

        {hotspots.length > 0 && (
          <ChartPanel
            title="National serious-crime hotspots"
            description="SAPS TOP 30 precincts — community-reported serious crime (all categories)"
            className="lg:col-span-2"
          >
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[var(--border)] text-left text-xs uppercase tracking-wide text-[var(--muted-foreground)]">
                    <th className="py-2 pr-4">#</th>
                    <th className="py-2 pr-4">Precinct</th>
                    <th className="py-2 pr-4">Area</th>
                    <th className="py-2 pr-4">Province</th>
                    <th className="py-2 text-right">Serious crime</th>
                  </tr>
                </thead>
                <tbody>
                  {hotspots.map((h) => (
                    <tr
                      key={`${h.rank}-${h.station}`}
                      className="border-b border-[var(--border)]/60"
                    >
                      <td className="py-2 pr-4 tabular-nums">{h.rank}</td>
                      <td className="py-2 pr-4 font-medium">{h.station}</td>
                      <td className="py-2 pr-4 text-[var(--muted-foreground)]">
                        {h.district}
                      </td>
                      <td className="py-2 pr-4">{h.province}</td>
                      <td className="py-2 text-right tabular-nums">
                        {formatNumber(h.serious_crime)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </ChartPanel>
        )}
      </div>

      <p className="mt-4 text-xs text-[var(--muted-foreground)]">
        Map drill-down (province → city boundaries) is planned with Mapbox. Precinct
        coordinates can be layered once a Mapbox token is configured.
      </p>

      <SourceBadge
        source={`${d?.source ?? "SAPS"} · Lightstone/ISS insights listed in DATA_SOURCES.md`}
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
