/** Approximate map centers for South Africa drill-down (lng, lat). */

export const SA_CENTER: [number, number] = [25.5, -29.0];

export const PROVINCE_CENTERS: Record<string, [number, number]> = {
  "Western Cape": [18.4241, -33.9249],
  Gauteng: [28.0473, -26.2041],
  "KwaZulu-Natal": [31.0218, -29.8587],
  "Eastern Cape": [27.4144, -32.997],
  Limpopo: [29.9038, -23.9045],
  Mpumalanga: [30.98, -25.4753],
  "North West": [25.6569, -25.8601],
  "Free State": [26.214, -29.1211],
  "Northern Cape": [21.6158, -28.738],
};

/** City / metro district labels from SAPS → coordinates */
export const DISTRICT_CENTERS: Record<string, [number, number]> = {
  "City of Cape Town": [18.4241, -33.9249],
  Johannesburg: [28.0473, -26.2041],
  eThekwini: [31.0218, -29.8587],
  Ekurhuleni: [28.2719, -26.1783],
  Tshwane: [28.1881, -25.7461],
  "Cape Winelands": [19.4485, -33.9321],
  "Garden Route": [22.4617, -33.9608],
  "West Coast": [18.4911, -32.8975],
  Mangaung: [26.214, -29.1211],
  Bojanala: [25.6569, -25.8601],
  Capricorn: [29.9038, -23.9045],
  Vhembe: [30.4538, -22.9756],
  Umgungundlovu: [30.3756, -29.6006],
  Ilembe: [31.1197, -29.5289],
  "King Cetshwayo": [31.8938, -28.7807],
  Sedibeng: [27.8544, -26.6299],
  "West Rand": [27.2429, -26.3194],
};

export function districtCoords(
  district: string,
  province: string,
  index = 0,
): [number, number] {
  const direct = DISTRICT_CENTERS[district];
  if (direct) return jitter(direct, index);

  const fuzzy = Object.entries(DISTRICT_CENTERS).find(([name]) =>
    district.toLowerCase().includes(name.toLowerCase()) ||
    name.toLowerCase().includes(district.toLowerCase()),
  );
  if (fuzzy) return jitter(fuzzy[1], index);

  const prov = PROVINCE_CENTERS[province] ?? SA_CENTER;
  return jitter(prov, index + 3);
}

export function provinceCoords(province: string): [number, number] {
  return PROVINCE_CENTERS[province] ?? SA_CENTER;
}

function jitter([lng, lat]: [number, number], index: number): [number, number] {
  const angle = (index * 137.5 * Math.PI) / 180;
  const radius = 0.04 + (index % 4) * 0.015;
  return [lng + radius * Math.cos(angle), lat + radius * Math.sin(angle)];
}

export type CrimeMapMarker = {
  id: string;
  label: string;
  longitude: number;
  latitude: number;
  value: number;
  kind: "province" | "district" | "station";
};
