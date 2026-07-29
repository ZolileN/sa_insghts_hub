"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";
import { ChevronUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useDrillDown } from "@/hooks/use-drill-down";
import type { CrimeMapMarker } from "@/shared/data/sa-geo";

const LeafletMapView = dynamic(() => import("./leaflet-map-view"), {
  ssr: false,
  loading: () => (
    <div
      className="flex items-center justify-center rounded-lg border border-[var(--border)] bg-slate-50 text-sm text-[var(--muted-foreground)]"
      style={{ height: 420 }}
    >
      Loading map…
    </div>
  ),
});

type GeoMapProps = {
  markers: CrimeMapMarker[];
  province: string;
  city: string;
  suburb?: string;
  height?: number;
  valueLabel?: string;
};

function displayLabel(label: string) {
  if (label === "City of Cape Town") return "Cape Town";
  return label;
}

function MapDrillBar({
  province,
  city,
  suburb = "All suburbs",
}: {
  province: string;
  city: string;
  suburb?: string;
}) {
  const { drillUp, canDrillUp } = useDrillDown();

  const crumbs = [
    province === "All Provinces" ? "South Africa" : province,
    city !== "All areas" ? displayLabel(city) : null,
    suburb !== "All suburbs" ? suburb : null,
  ].filter(Boolean);

  return (
    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--border)] bg-white/90 px-3 py-2 text-xs">
      <p className="text-[var(--muted-foreground)]">
        <span className="font-medium text-[var(--foreground)]">
          {crumbs.join(" → ")}
        </span>
        <span className="ml-2 hidden sm:inline">
          · Click markers or chart bars to drill down
        </span>
      </p>
      {canDrillUp && (
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="h-7 gap-1 px-2 text-xs"
          onClick={drillUp}
        >
          <ChevronUp className="size-3.5" />
          Drill up
        </Button>
      )}
    </div>
  );
}

export function GeoMap({
  markers,
  province,
  city,
  suburb = "All suburbs",
  height = 420,
  valueLabel = "value",
}: GeoMapProps) {
  const maxValue = useMemo(
    () => Math.max(...markers.map((m) => m.value), 1),
    [markers],
  );

  if (markers.length === 0) {
    return (
      <div
        className="flex flex-col items-center justify-center rounded-lg border border-dashed border-[var(--border)] bg-[var(--accent)]/30 p-8 text-center"
        style={{ height }}
      >
        <p className="text-sm font-medium">No map data for this selection</p>
        <p className="mt-2 max-w-md text-xs text-[var(--muted-foreground)]">
          Try another province or area filter, or drill up to national view.
        </p>
      </div>
    );
  }

  return (
    <div
      className="overflow-hidden rounded-lg border border-[var(--border)] bg-white"
      style={{ height }}
    >
      <MapDrillBar province={province} city={city} suburb={suburb} />
      <div style={{ height: height - 36 }}>
        <LeafletMapView
          markers={markers}
          province={province}
          city={city}
          suburb={suburb}
          height={height - 36}
          valueLabel={valueLabel}
        />
      </div>
      <p className="absolute bottom-2 left-3 hidden text-[10px] text-[var(--muted-foreground)]">
        Marker size ∝ {valueLabel} (max {maxValue})
      </p>
    </div>
  );
}

/** Crime dashboard map — murder counts by geography */
export function CrimeMap(props: Omit<GeoMapProps, "valueLabel">) {
  return <GeoMap {...props} valueLabel="murders" />;
}
