import type { Province } from "./constants";

export function resolveProvince(
  provinceParam: string | undefined,
): Province {
  const valid: Province[] = [
    "All Provinces",
    "Western Cape",
    "Gauteng",
    "KwaZulu-Natal",
    "Eastern Cape",
    "Limpopo",
    "Mpumalanga",
    "North West",
    "Free State",
    "Northern Cape",
  ];
  if (provinceParam && valid.includes(provinceParam as Province)) {
    return provinceParam as Province;
  }
  return "All Provinces";
}

export function provinceLabel(province: Province): string {
  return province === "All Provinces" ? "National" : province;
}

/** Short labels for cramped chart axes (full name stays in data / tooltips / drill-down). */
export function provinceAxisLabel(name: string): string {
  if (name === "KwaZulu-Natal") return "KZN";
  return name;
}
