"use client";

import { useEffect, useMemo, useState } from "react";
import Map, { Marker, NavigationControl } from "react-map-gl/mapbox";
import type { CrimeMapMarker } from "@/shared/data/sa-geo";
import { SA_CENTER } from "@/shared/data/sa-geo";
import { formatNumber } from "@/shared/utils";
import "mapbox-gl/dist/mapbox-gl.css";

const TOKEN = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN;

/** South Africa bounding box for SVG fallback projection */
const SA_BOUNDS = {
  minLng: 16.5,
  maxLng: 33.0,
  minLat: -35.0,
  maxLat: -22.0,
};

type GeoMapProps = {
  markers: CrimeMapMarker[];
  province: string;
  city: string;
  height?: number;
  valueLabel?: string;
};

function markerColor(
  kind: CrimeMapMarker["kind"],
  value: number,
  max: number,
) {
  const t = max > 0 ? value / max : 0;
  if (kind === "station" || kind === "suburb")
    return `rgba(220, 38, 38, ${0.45 + t * 0.55})`;
  if (kind === "district") return `rgba(217, 119, 6, ${0.45 + t * 0.55})`;
  return `rgba(37, 99, 235, ${0.45 + t * 0.55})`;
}

function useWebGLSupported() {
  const [supported, setSupported] = useState(true);

  useEffect(() => {
    try {
      const canvas = document.createElement("canvas");
      const gl =
        canvas.getContext("webgl") ?? canvas.getContext("experimental-webgl");
      setSupported(Boolean(gl));
    } catch {
      setSupported(false);
    }
  }, []);

  return supported;
}

function projectToSvg(lng: number, lat: number, width: number, height: number) {
  const x =
    ((lng - SA_BOUNDS.minLng) / (SA_BOUNDS.maxLng - SA_BOUNDS.minLng)) * width;
  const y =
    ((SA_BOUNDS.maxLat - lat) / (SA_BOUNDS.maxLat - SA_BOUNDS.minLat)) * height;
  return { x, y };
}

function SvgFallbackMap({
  markers,
  maxValue,
  height,
  valueLabel,
}: {
  markers: CrimeMapMarker[];
  maxValue: number;
  height: number;
  valueLabel: string;
}) {
  const width = 800;
  const pad = 24;

  return (
    <div
      className="relative rounded-lg border border-[var(--border)] bg-gradient-to-b from-slate-50 to-slate-100"
      style={{ height }}
    >
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="h-full w-full"
        role="img"
        aria-label="South Africa map fallback"
      >
        <rect
          x={pad}
          y={pad}
          width={width - pad * 2}
          height={height - pad * 2}
          rx={12}
          fill="rgba(255,255,255,0.6)"
          stroke="rgba(15,23,42,0.08)"
        />
        {markers.map((m) => {
          const { x, y } = projectToSvg(
            m.longitude,
            m.latitude,
            width - pad * 2,
            height - pad * 2,
          );
          const size = 8 + (m.value / maxValue) * 20;
          return (
            <g
              key={m.id}
              transform={`translate(${x + pad}, ${y + pad})`}
            >
              <circle
                r={size}
                fill={markerColor(m.kind, m.value, maxValue)}
                stroke="white"
                strokeWidth={2}
              />
              <title>{`${m.label}: ${formatNumber(m.value)} ${valueLabel}`}</title>
            </g>
          );
        })}
      </svg>
      <p className="absolute bottom-2 left-3 text-[10px] text-[var(--muted-foreground)]">
        Map preview (WebGL unavailable) — markers show relative {valueLabel}
      </p>
    </div>
  );
}

export function GeoMap({
  markers,
  province,
  city,
  height = 420,
  valueLabel = "value",
}: GeoMapProps) {
  const webgl = useWebGLSupported();
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

  if (!TOKEN || !webgl) {
    if (markers.length === 0) {
      return (
        <div
          className="flex flex-col items-center justify-center rounded-lg border border-dashed border-[var(--border)] bg-[var(--accent)]/30 p-8 text-center"
          style={{ height }}
        >
          <p className="text-sm font-medium">No map data for this selection</p>
          {!TOKEN && (
            <p className="mt-2 max-w-md text-xs text-[var(--muted-foreground)]">
              Add{" "}
              <code className="text-[11px]">NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN</code>{" "}
              to enable the interactive map.
            </p>
          )}
          {!webgl && TOKEN && (
            <p className="mt-2 max-w-md text-xs text-[var(--muted-foreground)]">
              WebGL is not available in this browser session. Showing a static
              marker preview instead.
            </p>
          )}
        </div>
      );
    }

    return (
      <SvgFallbackMap
        markers={markers}
        maxValue={maxValue}
        height={height}
        valueLabel={valueLabel}
      />
    );
  }

  return (
    <div
      className="overflow-hidden rounded-lg border border-[var(--border)]"
      style={{ height }}
    >
      <Map
        mapboxAccessToken={TOKEN}
        initialViewState={viewState}
        style={{ width: "100%", height: "100%" }}
        mapStyle="mapbox://styles/mapbox/light-v11"
        attributionControl
        reuseMaps
        failIfMajorPerformanceCaveat={false}
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

/** Crime dashboard map — murder counts by geography */
export function CrimeMap(props: Omit<GeoMapProps, "valueLabel">) {
  return <GeoMap {...props} valueLabel="murders" />;
}
