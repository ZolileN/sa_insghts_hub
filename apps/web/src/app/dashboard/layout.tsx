import Link from "next/link";
import { Suspense } from "react";
import { DashboardSidebar } from "@/components/layout/dashboard-sidebar";
import { AreaFilter } from "@/components/layout/area-filter";
import { SuburbFilter } from "@/components/layout/suburb-filter";
import { ProvinceFilter } from "@/components/layout/province-filter";
import { Button } from "@/components/ui/button";

export const metadata = {
  title: "Dashboard",
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="precision-ops flex min-h-screen">
      <Suspense fallback={<aside className="w-[260px] border-r border-[var(--border)]" />}>
        <DashboardSidebar />
      </Suspense>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="chrome-bar flex items-center justify-between gap-4 px-6 py-3">
          <p className="text-sm text-[var(--muted-foreground)]">
            South African public data — province-aware views
          </p>
          <div className="flex items-center gap-2 sm:gap-3">
            <Suspense fallback={null}>
              <ProvinceFilter />
            </Suspense>
            <Suspense fallback={null}>
              <AreaFilter />
            </Suspense>
            <Suspense fallback={null}>
              <SuburbFilter />
            </Suspense>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/">Marketing site</Link>
            </Button>
            <Button variant="outline" size="sm" asChild>
              <Link href="/dashboard/crime">Dashboard</Link>
            </Button>
          </div>
        </header>
        <main className="flex-1 overflow-auto p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
