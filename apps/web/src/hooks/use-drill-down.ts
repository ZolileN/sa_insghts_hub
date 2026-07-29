"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";

/** PowerBI-style URL drill-down for province → city/metro pages. */
export function useDrillDown() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const province = searchParams.get("province") ?? "All Provinces";
  const city = searchParams.get("city") ?? "All areas";

  function pushParams(mutate: (params: URLSearchParams) => void) {
    const params = new URLSearchParams(searchParams.toString());
    mutate(params);
    const q = params.toString();
    router.push(q ? `${pathname}?${q}` : pathname);
  }

  function drillToProvince(name: string) {
    pushParams((params) => {
      params.set("province", name);
      params.delete("city");
    });
  }

  function drillToCity(name: string) {
    pushParams((params) => {
      params.set("city", name);
    });
  }

  function drillUp() {
    if (city !== "All areas") {
      pushParams((params) => params.delete("city"));
      return;
    }
    if (province !== "All Provinces") {
      pushParams((params) => {
        params.delete("province");
        params.delete("city");
      });
    }
  }

  return {
    province,
    city,
    drillToProvince,
    drillToCity,
    drillUp,
    canDrillUp: city !== "All areas" || province !== "All Provinces",
  };
}
