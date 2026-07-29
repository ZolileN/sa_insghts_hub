"use client";

import { SimpleBarChart } from "@/components/charts/recharts";
import { useDrillDown } from "@/hooks/use-drill-down";

type DrillableSimpleBarChartProps = {
  data: Record<string, unknown>[];
  xKey: string;
  yKey: string;
  color?: string;
  layout?: "vertical" | "horizontal";
  height?: number;
  province: string;
  city: string;
  /** Drill into province when national; into city/metro when provincial */
  drillLevel: "province" | "district";
};

export function DrillableSimpleBarChart({
  data,
  xKey,
  yKey,
  color,
  layout,
  height,
  province,
  city,
  drillLevel,
}: DrillableSimpleBarChartProps) {
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

  return (
    <div>
      <SimpleBarChart
        data={data}
        xKey={xKey}
        yKey={yKey}
        color={color}
        layout={layout}
        height={height}
        onCategoryClick={interactive ? onCategoryClick : undefined}
      />
      {interactive && (
        <p className="mt-2 text-[11px] text-[var(--muted-foreground)]">
          Click a bar to drill down into that{" "}
          {drillLevel === "province" ? "province" : "metro / district"}
        </p>
      )}
    </div>
  );
}
