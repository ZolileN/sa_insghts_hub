import type { Province } from "./constants";

export function resolveCity(
  cityParam: string | undefined,
  allowed: string[],
): string {
  if (!cityParam || cityParam === "All areas") return "All areas";
  if (allowed.includes(cityParam)) return cityParam;
  return "All areas";
}

export function scopeLabel(province: Province, city: string): string {
  if (province === "All Provinces") return "National";
  if (city !== "All areas") return `${city}, ${province}`;
  return province;
}

export type PropertyMetro = {
  median_price_r?: number;
  yoy_growth_pct?: number;
  rental_yield_pct?: number;
  days_on_market?: number;
  estimated_monthly_rent_r?: number;
  airbnb_listings?: number;
  building_plans_yoy_pct?: number;
  suburbs?: Record<string, PropertySuburb>;
};

export type PropertySuburb = {
  median_price_r?: number;
  rental_yield_pct?: number;
  days_on_market?: number;
  estimated_monthly_rent_r?: number;
};

export type PropertyNational = {
  median_price_r?: number;
  yoy_growth_pct?: number;
  avg_rental_yield_pct?: number;
  days_on_market?: number;
  bond_approval_rate_pct?: number;
  prime_rate_pct?: number;
  transfer_duty_threshold_r?: number;
  avg_household_income_r?: number;
};

/** Monthly bond estimate — 20-year at prime, 90% loan */
export function estimateMonthlyBond(
  priceR: number,
  primeRatePct: number,
  loanPct = 0.9,
  years = 20,
): number {
  const loan = priceR * loanPct;
  const monthlyRate = primeRatePct / 100 / 12;
  const months = years * 12;
  if (monthlyRate <= 0) return loan / months;
  return (
    (loan * monthlyRate * Math.pow(1 + monthlyRate, months)) /
    (Math.pow(1 + monthlyRate, months) - 1)
  );
}

export function estimateMonthlyRent(priceR: number, yieldPct: number): number {
  return (priceR * (yieldPct / 100)) / 12;
}

export function rentVsBuyRatio(monthlyRent: number, monthlyBond: number): number {
  if (monthlyBond <= 0) return 0;
  return monthlyRent / monthlyBond;
}

export function affordabilityVsNational(
  localMedian: number,
  nationalMedian: number,
): number {
  if (nationalMedian <= 0) return 100;
  return Math.round((localMedian / nationalMedian) * 100);
}
