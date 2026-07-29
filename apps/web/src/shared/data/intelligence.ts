/** Small derived metrics for intelligence KPI cards across dashboards. */

export function pctChange(current: number, prior: number): number | null {
  if (prior === 0) return null;
  return ((current - prior) / prior) * 100;
}

export function lastTwoFromRecord(
  record: Record<string, number>,
): [string, number, string, number] | null {
  const keys = Object.keys(record).sort();
  if (keys.length < 2) return null;
  const priorKey = keys[keys.length - 2];
  const lastKey = keys[keys.length - 1];
  return [priorKey, record[priorKey], lastKey, record[lastKey]];
}

export function sumRecordValues(
  record: Record<string, number> | undefined,
): number {
  return Object.values(record ?? {}).reduce((a, b) => a + b, 0);
}

export function estimateMonthlyElectricityBill(
  kwh: number,
  tariffCentsPerKwh: number,
): number {
  return Math.round((kwh * tariffCentsPerKwh) / 100);
}

export function digitalFraudSharePct(
  categories: Record<string, { losses_rm?: number }>,
): number {
  const digitalKeys = new Set([
    "Card not present",
    "Online banking",
    "SIM swap/account takeover",
    "Business email compromise",
    "Investment scams",
  ]);
  let digital = 0;
  let total = 0;
  for (const [name, v] of Object.entries(categories)) {
    const loss = v.losses_rm ?? 0;
    total += loss;
    if (digitalKeys.has(name)) digital += loss;
  }
  if (total === 0) return 0;
  return Math.round((digital / total) * 100);
}

export function provinceRank(
  values: Record<string, number>,
  province: string,
  higherIsWorse = true,
): number | null {
  const entries = Object.entries(values).filter(([, v]) => v > 0);
  if (entries.length === 0) return null;
  entries.sort((a, b) => (higherIsWorse ? b[1] - a[1] : a[1] - b[1]));
  const idx = entries.findIndex(([p]) => p === province);
  return idx >= 0 ? idx + 1 : null;
}
