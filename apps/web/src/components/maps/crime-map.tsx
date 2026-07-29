"use client";

import { useMemo } from "react";
import Map, { Marker, NavigationControl } from "react-map-gl/mapbox";
import type { CrimeMapMarker } from "@/shared/data/sa-geo";
import { SA_CENTER } from "@/shared/data/sa-geo";
import { formatNumber } from "@/shared/utils";
import "mapbox-gl/dist/mapbox-gl.css";

const TOKEN = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN;

type CrimeMapProps = {
  markers: CrimeMapMarker[];
  province: string;
  city: string;
  height?: number;
};

function markerColor(kind: CrimeMapMarker["kind"], value: number, max: number) {
  const t = max > 0 ? value / max : 0;
  if (kind === "station") return `rgba(220, 38, 38, ${0.45 + t * 0.55})`;
  if (kind === "district") return `rgba(217, 119, 6, ${0.45 + t * 0.55})`;
  return `rgba(37, 99, 235, ${0.45 + t * 0.55})`;
}

export function CrimeMap({
  markers,
  province,
  city,
  height = 420,
}: CrimeMapProps) {
  const maxValue = useMemo(
    () => Math.max(...markers.map((m) => m.value), 1),
    [markers],
  );

  const viewState = useMemo(() => {
    if (city !== "All areas" && markers.length > 0) {
      const m = markers[0];
      return { longitude: m.longitude, latitude: m.latitude, zoom: 10 };
    }
    if (province !== "All Provinces") {
      const m = markers.find((x) => x.kind === "district") ?? markers[0];
      if (m) return { longitude: m.longitude, latitude: m.latitude, zoom: 7.5 };
    }
    return { longitude: SA_CENTER[0], latitude: SA_CENTER[1], zoom: 5.2 };
  }, [markers, province, city]);

  if (!TOKEN) {
    return (
      <div
        className="flex flex-col items-center justify-center rounded-lg border border-dashed border-[var(--border)] bg-[var(--accent)]/30 p-8 text-center"
        style={{ height }}
      >
        <p className="text-sm font-medium">Mapbox token not configured</p>
        <p className="mt-2 max-w-md text-xs text-[var(--muted-foreground)]">
          Add <code className="text-[11px]">NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN</code> to{" "}
          <code className="text-[11px]">apps/web/.env.local</code> (and Vercel env vars),
          then restart the dev server.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-[var(--border)]" style={{ height }}>
      <Map
        mapboxAccessToken={TOKEN}
        initialViewState={viewState}
        style={{ width: "100%", height: "100%" }}
        mapStyle="mapbox://styles/mapbox/light-v11"
        attributionControl
        reuseMaps
      >
        <NavigationControl position="top-right" showCompass={false} />
        {markers.map((m) => {
          const size = 12 + (m.value / maxValue) * 28;
          return (
            <Marker
              key={m.id}
              longitude={m.longitude}
              latitude={m.latitude}
              anchor="center"
            >
              <div
                className="flex items-center justify-center rounded-full border-2 border-white text-[10px] font-semibold text-white shadow-md"
                style={{
                  width: size,
                  height: size,
                  background: markerColor(m.kind, m.value, maxValue),
                }}
                title={`${m.label}: ${formatNumber(m.value)}`}
              />
            </Marker>
          );
        })}
      </Map>
    </div>
  );
}
