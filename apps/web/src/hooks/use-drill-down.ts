"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";

/** PowerBI-style URL drill-down for province → city/metro → suburb. */
export function useDrillDown() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const province = searchParams.get("province") ?? "All Provinces";
  const city = searchParams.get("city") ?? "All areas";
  const suburb = searchParams.get("suburb") ?? "All suburbs";

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
      params.delete("suburb");
    });
  }

  function drillToCity(name: string) {
    pushParams((params) => {
      params.set("city", name);
      params.delete("suburb");
    });
  }

  function drillToSuburb(name: string) {
    pushParams((params) => {
      params.set("suburb", name);
    });
  }

  function drillUp() {
    if (suburb !== "All suburbs") {
      pushParams((params) => params.delete("suburb"));
      return;
    }
    if (city !== "All areas") {
      pushParams((params) => params.delete("city"));
      return;
    }
    if (province !== "All Provinces") {
      pushParams((params) => {
        params.delete("province");
        params.delete("city");
        params.delete("suburb");
      });
    }
  }

  return {
    province,
    city,
    suburb,
    drillToProvince,
    drillToCity,
    drillToSuburb,
    drillUp,
    canDrillUp:
      suburb !== "All suburbs" ||
      city !== "All areas" ||
      province !== "All Provinces",
  };
}
