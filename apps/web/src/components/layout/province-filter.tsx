"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { PROVINCES } from "@/shared/data/constants";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function ProvinceFilter() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const current = searchParams.get("province") ?? "All Provinces";

  return (
    <Select
      value={current}
      onValueChange={(value) => {
        const params = new URLSearchParams(searchParams.toString());
        if (value === "All Provinces") params.delete("province");
        else params.set("province", value);
        const q = params.toString();
        router.push(q ? `${pathname}?${q}` : pathname);
      }}
    >
      <SelectTrigger className="w-[200px]">
        <SelectValue placeholder="Province" />
      </SelectTrigger>
      <SelectContent>
        {PROVINCES.map((p) => (
          <SelectItem key={p} value={p}>{p}</SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
