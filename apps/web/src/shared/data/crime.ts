import type { Province } from "./constants";

export function resolveCity(
  cityParam: string | undefined,
  allowed: string[],
): string {
  if (!cityParam || cityParam === "All areas") return "All areas";
  if (allowed.includes(cityParam)) return cityParam;
  return "All areas";
}

export function scopeLabel(
  province: Province,
  city: string,
): string {
  if (province === "All Provinces") return "National";
  if (city !== "All areas") return `${city}, ${province}`;
  return province;
}

export const CRIME_TYPE_LABELS: Record<string, string> = {
  Murder: "Murder",
  "Sexual offences": "Sexual offences",
  "Attempted murder": "Attempted murder",
  "Assault GBH": "Assault GBH",
  Carjacking: "Carjacking",
  "Robbery aggravating": "Aggravated robbery",
  "Residential burglary": "Residential burglary",
  "Common robbery": "Common robbery",
};

export const CRIME_KPI_KEYS = [
  "Murder",
  "Sexual offences",
  "Carjacking",
  "Residential burglary",
] as const;

export const CRIME_CHART_PALETTE = [
  "#dc2626",
  "#7c3aed",
  "#d97706",
  "#2563eb",
  "#059669",
  "#be185d",
  "#0891b2",
  "#4f46e5",
];
