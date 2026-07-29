"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function CityFilter({ districts }: { districts: string[] }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const current = searchParams.get("city") ?? "All areas";

  if (districts.length === 0) {
    return null;
  }

  return (
    <Select
      value={current}
      onValueChange={(value) => {
        const params = new URLSearchParams(searchParams.toString());
        if (value === "All areas") params.delete("city");
        else params.set("city", value);
        const q = params.toString();
        router.push(q ? `${pathname}?${q}` : pathname);
      }}
    >
      <SelectTrigger className="w-[220px]">
        <SelectValue placeholder="City / metro" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="All areas">All areas</SelectItem>
        {districts.map((d) => (
          <SelectItem key={d} value={d}>{d}</SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
