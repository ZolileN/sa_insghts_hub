"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function SuburbFilter() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const topic = pathname.match(/\/dashboard\/([^/]+)/)?.[1];
  const province = searchParams.get("province");
  const city = searchParams.get("city");
  const current = searchParams.get("suburb") ?? "All suburbs";

  const [suburbs, setSuburbs] = useState<string[]>([]);

  useEffect(() => {
    if (topic !== "property" || !province || !city || city === "All areas") {
      setSuburbs([]);
      return;
    }

    const params = new URLSearchParams({ topic: "property", province, city });
    fetch(`/api/area-options?${params}`)
      .then((r) => r.json())
      .then((data: { suburbs?: string[] }) => setSuburbs(data.suburbs ?? []))
      .catch(() => setSuburbs([]));
  }, [topic, province, city]);

  if (topic !== "property" || !city || city === "All areas" || suburbs.length === 0) {
    return null;
  }

  return (
    <Select
      value={
        suburbs.includes(current) || current === "All suburbs"
          ? current
          : "All suburbs"
      }
      onValueChange={(value) => {
        const params = new URLSearchParams(searchParams.toString());
        if (value === "All suburbs") params.delete("suburb");
        else params.set("suburb", value);
        const q = params.toString();
        router.push(q ? `${pathname}?${q}` : pathname);
      }}
    >
      <SelectTrigger className="w-[200px]">
        <SelectValue placeholder="All suburbs" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="All suburbs">All suburbs</SelectItem>
        {suburbs.map((name) => (
          <SelectItem key={name} value={name}>{name}</SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
