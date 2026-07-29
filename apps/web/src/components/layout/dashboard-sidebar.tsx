"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import {
  Banknote,
  CircleDollarSign,
  Droplets,
  GraduationCap,
  HeartPulse,
  Home,
  Lock,
  ShieldAlert,
  TrendingDown,
  Zap,
  type LucideIcon,
} from "lucide-react";
import { TOPICS } from "@/shared/data/constants";
import { LiboLogo } from "@/components/brand/libo-logo";
import { cn } from "@/shared/utils";
import { Separator } from "@/components/ui/separator";

const ICONS: Record<string, LucideIcon> = {
  ShieldAlert,
  Home,
  Lock,
  TrendingDown,
  Zap,
  Banknote,
  HeartPulse,
  GraduationCap,
  CircleDollarSign,
  Droplets,
};

export function DashboardSidebar() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const province = searchParams.get("province");
  const qs = province ? `?province=${encodeURIComponent(province)}` : "";

  return (
    <aside
      className="glass-panel flex h-full w-[var(--sidebar-width)] flex-col border-r border-[var(--border)] bg-white/60 dark:bg-slate-900/40"
      style={{ width: "var(--sidebar-width)" }}
    >
      <div className="chrome-bar px-5 py-5">
        <LiboLogo href="/" size="sm" className="px-1" />
      </div>

      <nav className="flex-1 overflow-y-auto p-3">
        <p className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
          Topics
        </p>
        <ul className="space-y-0.5">
          {TOPICS.map((topic) => {
            const href = `/dashboard/${topic.id}${qs}`;
            const active = pathname === `/dashboard/${topic.id}`;
            const Icon = ICONS[topic.icon] ?? ShieldAlert;
            return (
              <li key={topic.id}>
                <Link
                  href={href}
                  className={cn(
                    "flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm transition-colors",
                    active
                      ? "bg-[var(--primary)] text-white"
                      : "text-[var(--foreground)] hover:bg-[var(--accent)]",
                  )}
                >
                  <Icon className="h-4 w-4 shrink-0 opacity-80" />
                  <span className="truncate">{topic.shortLabel}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="p-4">
        <Separator className="mb-3" />
        <p className="text-[10px] text-[var(--muted-foreground)]">
          Data refreshed via cron scrapers. Live badges reflect source availability.
        </p>
      </div>
    </aside>
  );
}
