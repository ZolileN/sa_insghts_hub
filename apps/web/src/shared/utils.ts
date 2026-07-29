import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(n: number, decimals = 0): string {
  return n.toLocaleString("en-ZA", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function formatCurrency(n: number): string {
  if (n >= 1_000_000) return `R${(n / 1_000_000).toFixed(2)}M`;
  if (n >= 1_000) return `R${(n / 1_000).toFixed(0)}k`;
  return `R${formatNumber(n)}`;
}
