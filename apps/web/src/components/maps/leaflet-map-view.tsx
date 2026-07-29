"use client";

import { useEffect, useMemo } from "react";
import {
  CircleMarker,
  MapContainer,
  Popup,
  TileLayer,
  useMap,
} from "react-leaflet";
import type { LatLngExpression } from "leaflet";
import { useDrillDown } from "@/hooks/use-drill-down";
import type { CrimeMapMarker } from "@/shared/data/sa-geo";
import { SA_CENTER } from "@/shared/data/sa-geo";
import { formatNumber } from "@/shared/utils";

type LeafletMapViewProps = {
  markers: CrimeMapMarker[];
  province: string;
  city: string;
  suburb?: string;
  height: number;
  valueLabel: string;
};

function markerColor(
  kind: CrimeMapMarker["kind"],
  value: number,
  max: number,
) {
  const t = max > 0 ? value / max : 0;
  if (kind === "station" || kind === "suburb")
    return `rgba(220, 38, 38, ${0.55 + t * 0.45})`;
  if (kind === "district") return `rgba(217, 119, 6, ${0.55 + t * 0.45})`;
  return `rgba(37, 99, 235, ${0.55 + t * 0.45})`;
}

function MapViewport({
  center,
  zoom,
}: {
  center: LatLngExpression;
  zoom: number;
}) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom, { animate: true });
  }, [map, center, zoom]);
  return null;
}

function displayLabel(label: string) {
  if (label === "City of Cape Town") return "Cape Town";
  return label;
}

export default function LeafletMapView({
  markers,
  province,
  city,
  suburb = "All suburbs",
  height,
  valueLabel,
}: LeafletMapViewProps) {
  const { drillToProvince, drillToCity, drillToSuburb } = useDrillDown();

  const maxValue = useMemo(
    () => Math.max(...markers.map((m) => m.value), 1),
    [markers],
  );

  const { center, zoom } = useMemo(() => {
    if (suburb !== "All suburbs" && markers.length > 0) {
      const m = markers[0];
      return {
        center: [m.latitude, m.longitude] as LatLngExpression,
        zoom: 13,
      };
    }
    if (city !== "All areas" && markers.length > 0) {
      const m = markers[0];
      return {
        center: [m.latitude, m.longitude] as LatLngExpression,
        zoom: 11,
      };
    }
    if (province !== "All Provinces") {
      const m = markers.find((x) => x.kind === "district") ?? markers[0];
      if (m) {
        return {
          center: [m.latitude, m.longitude] as LatLngExpression,
          zoom: 8,
        };
      }
    }
    return {
      center: [SA_CENTER[1], SA_CENTER[0]] as LatLngExpression,
      zoom: 5.5,
    };
  }, [markers, province, city, suburb]);

  function handleDrill(marker: CrimeMapMarker) {
    if (marker.kind === "province") {
      drillToProvince(marker.label);
      return;
    }
    if (marker.kind === "district") {
      drillToCity(marker.label);
      return;
    }
    if (marker.kind === "suburb") {
      drillToSuburb(marker.label);
    }
  }

  function canDrill(marker: CrimeMapMarker) {
    if (marker.kind === "province") return true;
    if (marker.kind === "district") return true;
    if (marker.kind === "suburb") return true;
    return false;
  }

  return (
    <MapContainer
      center={center}
      zoom={zoom}
      style={{ width: "100%", height }}
      scrollWheelZoom
      className="z-0"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MapViewport center={center} zoom={zoom} />
      {markers.map((m) => {
        const radius = 10 + (m.value / maxValue) * 22;
        const fill = markerColor(m.kind, m.value, maxValue);
        const drillable = canDrill(m);

        return (
          <CircleMarker
            key={m.id}
            center={[m.latitude, m.longitude]}
            radius={radius}
            pathOptions={{
              fillColor: fill,
              fillOpacity: 0.85,
              color: "#ffffff",
              weight: 2,
            }}
            eventHandlers={
              drillable
                ? {
                    click: () => handleDrill(m),
                  }
                : undefined
            }
            className={drillable ? "cursor-pointer" : undefined}
          >
            <Popup>
              <div className="text-sm">
                <p className="font-semibold">{displayLabel(m.label)}</p>
                <p className="tabular-nums text-slate-600">
                  {formatNumber(m.value)} {valueLabel}
                </p>
                {drillable && (
                  <p className="mt-1 text-xs text-blue-600">
                    Click marker to drill down →
                  </p>
                )}
              </div>
            </Popup>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}
