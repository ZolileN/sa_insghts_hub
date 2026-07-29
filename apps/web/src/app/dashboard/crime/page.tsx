import {
  ChartPanel,
  KpiCard,
  PageHeader,
  SourceBadge,
} from "@/components/dashboard/page-parts";
import {
  ColoredBarChart,
  MultiBarChart,
  SimpleBarChart,
  SimpleLineChart,
} from "@/components/charts/recharts";
import { PROVINCE_LIST } from "@/shared/data/constants";
import { loadJson } from "@/shared/data/load";
import { provinceLabel, resolveProvince } from "@/shared/data/province";
import { formatNumber } from "@/shared/utils";

type CrimeData = {
  source?: string;
  scraped_at?: string;
  period?: string;
  is_live?: boolean;
  national_totals?: Record<string, number>;
  provinces?: Record<
    string,
    Record<string, number>
  >;
};

export default async function CrimePage({
  searchParams,
}: {
  searchParams: Promise<{ province?: string }>;
}) {
  const { province: provinceParam } = await searchParams;
  const province = resolveProvince(provinceParam);
  const d = await loadJson<CrimeData>("crime");
  const nat = d?.national_totals ?? {};
  const period = d?.period ?? "Latest period";
  const provData = d?.provinces ?? {};

  const murdersNat = nat.Murder ?? 17674;
  const burglaryNat = nat["Residential burglary"] ?? 205765;
  const carjackNat = nat.Carjacking ?? 15927;
  const sexualNat = nat["Sexual offences"] ?? 46704;

  let scopeMurders = murdersNat;
  let scopeLabel = "National murders";
  if (province !== "All Provinces" && provData[province]) {
    scopeMurders = provData[province].Murder ?? scopeMurders;
    scopeLabel = `${province} murders`;
  }

  const provinceMurders = PROVINCE_LIST.map((p) => ({
    province: p,
    murders: provData[p]?.Murder ?? 0,
  }));

  const provinceBurglary = PROVINCE_LIST.map((p) => ({
    province: p,
    burglaries: provData[p]?.["Residential burglary"] ?? 0,
  }));

  return (
    <div>
      <PageHeader
        title="Crime Statistics"
        description={`SAPS quarterly data — ${period}. Focus: violent crime and property crime that affect area safety decisions.`}
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label={scopeLabel}
          value={formatNumber(scopeMurders)}
          hint={provinceLabel(province)}
        />
        <KpiCard
          label="National murders"
          value={formatNumber(murdersNat)}
          hint="All provinces combined"
        />
        <KpiCard
          label="Carjackings (national)"
          value={formatNumber(carjackNat)}
          hint="High mobility risk indicator"
        />
        <KpiCard
          label="Residential burglaries"
          value={formatNumber(burglaryNat)}
          hint={`Sexual offences: ${formatNumber(sexualNat)}`}
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartPanel
          title="Murders by province"
          description="Which provinces carry the highest absolute murder counts"
        >
          <SimpleBarChart
            data={provinceMurders}
            xKey="province"
            yKey="murders"
            layout="vertical"
            color="#dc2626"
          />
        </ChartPanel>
        <ChartPanel
          title="Residential burglaries by province"
          description="Property crime volume — key for homeowners and insurers"
        >
          <SimpleBarChart
            data={provinceBurglary}
            xKey="province"
            yKey="burglaries"
            layout="vertical"
            color="#d97706"
          />
        </ChartPanel>
      </div>

      <SourceBadge
        source={d?.source ?? "SAPS"}
        scrapedAt={d?.scraped_at}
        isLive={d?.is_live}
      />
    </div>
  );
}
