/**
 * Canonical site URL for metadata and absolute links.
 * Vercel sets VERCEL_URL (no protocol). Override with NEXT_PUBLIC_SITE_URL in production.
 */
export function getSiteUrl(): string {
  const explicit = process.env.NEXT_PUBLIC_SITE_URL?.replace(/\/$/, "");
  if (explicit) return explicit;
  if (process.env.VERCEL_URL) return `https://${process.env.VERCEL_URL}`;
  return "http://localhost:3000";
}
