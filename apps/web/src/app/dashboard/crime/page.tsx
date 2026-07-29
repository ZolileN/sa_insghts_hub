import { CrimeMap } from "@/components/maps/crime-map";
import { DrillableMultiBarChart } from "@/components/charts/drillable-multi-bar-chart";
import { DrillableSimpleBarChart } from "@/components/charts/drillable-simple-bar-chart";
import {
  ChartPanel,
  KpiCard,
  PageHeader,
  SourceBadge,
} from "@/components/dashboard/page-parts";
import { PROVINCE_LIST } from "@/shared/data/constants";
import {
  CRIME_CHART_PALETTE,
  CRIME_KPI_KEYS,
  CRIME_TYPE_LABELS,
  resolveCity,
  scopeLabel,
} from "@/shared/data/crime";
import {
  districtCoords,
  provinceCoords,
  type CrimeMapMarker,
} from "@/shared/data/sa-geo";
import { loadJson } from "@/shared/data/load";
import { provinceLabel, resolveProvince } from "@/shared/data/province";
import { formatNumber } from "@/shared/utils";
import { provinceRank } from "@/shared/data/intelligence";

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

function buildMapMarkers(
  province: string,
  city: string,
  provData: Record<string, CrimeCounts>,
  districtMap: Record<string, CrimeCounts>,
  stationRows: StationRow[],
): CrimeMapMarker[] {
  if (province === "All Provinces") {
    return PROVINCE_LIST.map((p) => ({
      id: p,
      label: p,
      longitude: provinceCoords(p)[0],
      latitude: provinceCoords(p)[1],
      value: provData[p]?.Murder ?? 0,
      kind: "province" as const,
    })).filter((m) => m.value > 0);
  }

  if (city === "All areas") {
    return Object.entries(districtMap).map(([district, crimes], i) => {
      const [lng, lat] = districtCoords(district, province, i);
      return {
        id: `${province}-${district}`,
        label: district,
        longitude: lng,
        latitude: lat,
        value: crimes.Murder ?? 0,
        kind: "district" as const,
      };
    }).filter((m) => m.value > 0);
  }

  return stationRows.map((s, i) => {
    const [lng, lat] = districtCoords(s.district, province, i);
    return {
      id: `${s.name}-${i}`,
      label: s.name,
      longitude: lng,
      latitude: lat,
      value: s.murders,
      kind: "station" as const,
    };
  }).filter((m) => m.value > 0);
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

  const violentTotal =
    sumCrimes(counts, "Murder") +
    sumCrimes(counts, "Sexual offences") +
    sumCrimes(counts, "Carjacking") +
    sumCrimes(counts, "Attempted murder") +
    sumCrimes(counts, "Assault GBH");

  const propertyTotal =
    sumCrimes(counts, "Residential burglary") +
    sumCrimes(counts, "Non-residential burglary") +
    sumCrimes(counts, "Robbery aggravating");

  const aggravatedRobbery = sumCrimes(counts, "Robbery aggravating");
  const topHotspot = (d?.national_hotspots ?? [])[0];
  const murderByProv = Object.fromEntries(
    PROVINCE_LIST.map((p) => [p, provData[p]?.Murder ?? 0]),
  );
  const murderRank =
    province !== "All Provinces"
      ? provinceRank(murderByProv, province, true)
      : null;

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

  const contactMix =
    province === "All Provinces"
      ? PROVINCE_LIST.map((p) => ({
          province: p,
          "Assault GBH": provData[p]?.["Assault GBH"] ?? 0,
          "Attempted murder": provData[p]?.["Attempted murder"] ?? 0,
          "Common robbery": provData[p]?.["Common robbery"] ?? 0,
        }))
      : districtMurders.map((row) => ({
          province: row.district,
          "Assault GBH": districtMap[row.district]?.["Assault GBH"] ?? 0,
          "Attempted murder":
            districtMap[row.district]?.["Attempted murder"] ?? 0,
          "Common robbery": districtMap[row.district]?.["Common robbery"] ?? 0,
        }));

  const hotspots = (d?.national_hotspots ?? []).slice(0, 15);

  const mapMarkers = buildMapMarkers(
    province,
    city,
    provData,
    districtMap,
    stationRows,
  );

  const mapDescription =
    province === "All Provinces"
      ? "Murder counts by province — blue markers scale with volume"
      : city === "All areas"
        ? `Murder counts by city/metro in ${province} — orange markers`
        : `Police precincts in ${city} — red markers sized by murders`;

  return (
    <div>
      <PageHeader
        title="Crime Statistics"
        description={`SAPS quarterly data — ${period}. Drill down: province → city/metro → police precinct.`}
      />

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

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Violent crime total"
          value={formatNumber(violentTotal)}
          hint={`Murder, sexual offences, carjacking, assault GBH — ${label}`}
        />
        <KpiCard
          label="Property crime total"
          value={formatNumber(propertyTotal)}
          hint="Burglary and aggravated robbery volumes"
        />
        <KpiCard
          label="Aggravated robbery"
          value={formatNumber(aggravatedRobbery)}
          hint="High concern for buyers & retailers"
          trendPositive={aggravatedRobbery < 5000}
        />
        <KpiCard
          label={
            murderRank != null
              ? `Murder rank (${province})`
              : "National hotspot #1"
          }
          value={
            murderRank != null
              ? `#${murderRank} of 9`
              : topHotspot?.station ?? "—"
          }
          hint={
            murderRank != null
              ? "Among provinces this quarter"
              : topHotspot
                ? `${formatNumber(topHotspot.serious_crime)} serious crimes`
                : "SAPS TOP 30"
          }
        />
      </div>

      <ChartPanel
        title="Crime map"
        description={mapDescription + " — click markers to drill down"}
        className="mt-6"
      >
        <CrimeMap
          markers={mapMarkers}
          province={province}
          city={city}
        />
      </ChartPanel>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        {province === "All Provinces" ? (
          <ChartPanel
            title="Murders by province"
            description="Absolute murder counts — click a bar or map marker to drill down"
          >
            <DrillableSimpleBarChart
              data={provinceMurders}
              xKey="province"
              yKey="murders"
              layout="vertical"
              color="#dc2626"
              province={province}
              city={city}
              drillLevel="province"
            />
          </ChartPanel>
        ) : city === "All areas" ? (
          <ChartPanel
            title={`Murders by area — ${province}`}
            description="City and metro districts — click to drill into precinct view"
          >
            <DrillableSimpleBarChart
              data={districtMurders}
              xKey="district"
              yKey="murders"
              layout="vertical"
              color="#dc2626"
              province={province}
              city={city}
              drillLevel="district"
            />
          </ChartPanel>
        ) : (
          <ChartPanel
            title={`Top precincts — ${city}`}
            description="Police station murder counts in the selected area"
          >
            <DrillableSimpleBarChart
              data={stationRows.map((s) => ({
                station: s.name,
                murders: s.murders,
              }))}
              xKey="station"
              yKey="murders"
              layout="vertical"
              color="#dc2626"
              province={province}
              city={city}
              drillLevel="district"
            />
          </ChartPanel>
        )}

        <ChartPanel
          title="Violent crime mix"
          description={
            province === "All Provinces"
              ? "Murder, sexual offences, and carjacking — click to drill down"
              : "Violent crime by city/metro district"
          }
        >
          <DrillableMultiBarChart
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
            province={province}
            city={city}
            drillLevel={
              province === "All Provinces" ? "province" : "district"
            }
          />
        </ChartPanel>

        <ChartPanel
          title="Property & aggravated crime"
          description="Burglary and aggravated robbery volumes"
        >
          <DrillableMultiBarChart
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
            province={province}
            city={city}
            drillLevel={
              province === "All Provinces" ? "province" : "district"
            }
          />
        </ChartPanel>

        <ChartPanel
          title="Contact & street crime"
          description={
            province === "All Provinces"
              ? "Assault GBH, attempted murder, and street robbery — click to drill down"
              : "Street-level contact crime by city/metro district"
          }
        >
          <DrillableMultiBarChart
            data={contactMix}
            xKey="province"
            keys={[
              {
                key: "Assault GBH",
                color: CRIME_CHART_PALETTE[5],
                name: "Assault GBH",
              },
              {
                key: "Attempted murder",
                color: CRIME_CHART_PALETTE[6],
                name: "Attempted murder",
              },
              {
                key: "Common robbery",
                color: CRIME_CHART_PALETTE[7],
                name: "Common robbery",
              },
            ]}
            province={province}
            city={city}
            drillLevel={
              province === "All Provinces" ? "province" : "district"
            }
          />
        </ChartPanel>
      </div>

      {hotspots.length > 0 && (
        <ChartPanel
          title="National serious-crime hotspots"
          description="SAPS TOP 30 precincts — community-reported serious crime (all categories)"
          className="mt-6"
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

      <SourceBadge
        source={`${d?.source ?? "SAPS"} · Lightstone/ISS insights listed in DATA_SOURCES.md`}
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
