import { PROVINCE_LIST } from "./constants";
import { provinceCoords, type CrimeMapMarker } from "./sa-geo";

/** Province-level markers for topic maps (dam %, unemployment %, etc.). */
export function buildProvinceMarkers(
  values: Record<string, number>,
  kind: CrimeMapMarker["kind"] = "province",
): CrimeMapMarker[] {
  return PROVINCE_LIST.map((p) => ({
    id: p,
    label: p,
    longitude: provinceCoords(p)[0],
    latitude: provinceCoords(p)[1],
    value: values[p] ?? 0,
    kind,
  })).filter((m) => m.value > 0);
}
