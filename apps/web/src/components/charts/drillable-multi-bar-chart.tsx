"use client";

import { MultiBarChart } from "@/components/charts/recharts";
import { useDrillDown } from "@/hooks/use-drill-down";
import { provinceAxisLabel } from "@/shared/data/province";

type DrillableMultiBarChartProps = {
  data: Record<string, unknown>[];
  xKey: string;
  keys: { key: string; color: string; name?: string }[];
  height?: number;
  province: string;
  city: string;
  drillLevel: "province" | "district";
};

export function DrillableMultiBarChart({
  data,
  xKey,
  keys,
  height,
  province,
  city,
  drillLevel,
}: DrillableMultiBarChartProps) {
  const { drillToProvince, drillToCity } = useDrillDown();

  const interactive =
    (drillLevel === "province" && province === "All Provinces") ||
    (drillLevel === "district" &&
      province !== "All Provinces" &&
      city === "All areas");

  function onCategoryClick(label: string) {
    if (drillLevel === "province") drillToProvince(label);
    else drillToCity(label);
  }

  const categoryFormatter =
    drillLevel === "province" ? provinceAxisLabel : undefined;

  return (
    <div>
      <MultiBarChart
        data={data}
        xKey={xKey}
        keys={keys}
        height={height}
        onCategoryClick={interactive ? onCategoryClick : undefined}
        categoryFormatter={categoryFormatter}
      />
      {interactive && (
        <p className="mt-2 text-[11px] text-[var(--muted-foreground)]">
          Click a bar group to drill down
        </p>
      )}
    </div>
  );
}
