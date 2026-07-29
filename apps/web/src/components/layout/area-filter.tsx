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

const DRILL_TOPICS = new Set(["crime", "property"]);

function topicFromPath(pathname: string): string | null {
  const match = pathname.match(/\/dashboard\/([^/]+)/);
  const slug = match?.[1];
  if (!slug || !DRILL_TOPICS.has(slug)) return null;
  return slug;
}

export function AreaFilter() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const topic = topicFromPath(pathname);
  const province = searchParams.get("province");
  const current = searchParams.get("city") ?? "All areas";

  const [areas, setAreas] = useState<string[]>([]);

  useEffect(() => {
    if (!topic || !province) {
      setAreas([]);
      return;
    }

    const params = new URLSearchParams({ topic, province });
    fetch(`/api/area-options?${params}`)
      .then((r) => r.json())
      .then((data: { areas?: string[] }) => setAreas(data.areas ?? []))
      .catch(() => setAreas([]));
  }, [topic, province]);

  if (!topic || !province || areas.length === 0) {
    return null;
  }

  return (
    <Select
      value={areas.includes(current) || current === "All areas" ? current : "All areas"}
      onValueChange={(value) => {
        const params = new URLSearchParams(searchParams.toString());
        if (value === "All areas") params.delete("city");
        else params.set("city", value);
        params.delete("suburb");
        const q = params.toString();
        router.push(q ? `${pathname}?${q}` : pathname);
      }}
    >
      <SelectTrigger className="w-[220px]">
        <SelectValue placeholder="All areas" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="All areas">All areas</SelectItem>
        {areas.map((area) => (
          <SelectItem key={area} value={area}>{area}</SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
