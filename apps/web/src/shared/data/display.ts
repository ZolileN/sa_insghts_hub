import { formatCurrency, formatNumber } from "@/shared/utils";

/** User-facing labels — hide scraper/cron/fallback jargon from the UI. */
export function isTechnicalMetadata(text: string): boolean {
  const lower = text.toLowerCase();
  return (
    lower.includes("fallback") ||
    lower.includes("cron") ||
    lower.includes("scraper") ||
    lower.includes("ckan") ||
    lower.includes("dhis2") ||
    lower.includes("niwis") ||
    lower.includes("cached snapshot") ||
    lower.includes("run cron")
  );
}

export function formatDataAsOf(
  scrapedAt?: string | null,
  fallbackLabel = "Latest available figures",
): string {
  if (!scrapedAt || scrapedAt === "fallback") return fallbackLabel;
  try {
    return new Date(scrapedAt).toLocaleDateString("en-ZA", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  } catch {
    return fallbackLabel;
  }
}

export function friendlyReportLabel(
  reportDate?: string | null,
  scrapedAt?: string | null,
): string {
  if (reportDate && !isTechnicalMetadata(reportDate)) return reportDate;
  return formatDataAsOf(scrapedAt, "Weekly reservoir report");
}

/** Dashboard KPI: no invented numbers when JSON field is missing. */
export function dashNum(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) return "—";
  return formatNumber(value);
}

export function dashPct(
  value: number | null | undefined,
  digits = 1,
): string {
  if (value == null || Number.isNaN(value)) return "—";
  return `${value.toFixed(digits)}%`;
}

export function dashFixed(
  value: number | null | undefined,
  digits = 2,
): string {
  if (value == null || Number.isNaN(value)) return "—";
  return value.toFixed(digits);
}

export function formatMoney(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) return "—";
  return formatCurrency(value);
}

export function dashText(value: string | null | undefined): string {
  return value ?? "—";
}
