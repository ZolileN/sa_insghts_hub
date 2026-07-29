import Link from "next/link";
import { Button } from "@/components/ui/button";
import { LiboLogo } from "@/components/brand/libo-logo";

const NAV = [
  { href: "#topics", label: "Topics" },
  { href: "#audience", label: "Who it's for" },
  { href: "#pricing", label: "Pricing" },
  { href: "#ai", label: "AI Analyst" },
] as const;

export function MarketingNav() {
  return (
    <header className="chrome-bar sticky top-0 z-50 border-b border-[var(--border)]">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-6 py-3 lg:px-10">
        <LiboLogo href="/" size="md" />

        <nav className="hidden items-center gap-8 md:flex">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="text-xs font-medium uppercase tracking-wide text-[var(--muted-foreground)] transition-colors hover:text-[var(--foreground)]"
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <Button asChild size="sm">
          <Link href="/dashboard/crime">Launch Dashboard →</Link>
        </Button>
      </div>
    </header>
  );
}
