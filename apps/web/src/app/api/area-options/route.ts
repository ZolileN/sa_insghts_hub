import { NextResponse } from "next/server";
import { readFile } from "fs/promises";
import path from "path";
import { resolveProvince } from "@/shared/data/province";

type CrimeJson = {
  districts?: Record<string, Record<string, unknown>>;
};

type PropertyJson = {
  metros?: Record<
    string,
    Record<string, { suburbs?: Record<string, unknown> }>
  >;
};

async function loadDataFile(name: string) {
  const filePath = path.join(process.cwd(), "data", `${name}.json`);
  const raw = await readFile(filePath, "utf8");
  return JSON.parse(raw) as CrimeJson | PropertyJson;
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const topic = searchParams.get("topic") ?? "crime";
  const province = resolveProvince(searchParams.get("province") ?? undefined);
  const city = searchParams.get("city");

  if (province === "All Provinces") {
    return NextResponse.json({ areas: [], suburbs: [] });
  }

  try {
    if (topic === "property") {
      const data = (await loadDataFile("property")) as PropertyJson;
      const metros = data.metros?.[province] ?? {};

      if (city && city !== "All areas") {
        const suburbs = Object.keys(metros[city]?.suburbs ?? {}).sort((a, b) =>
          a.localeCompare(b),
        );
        return NextResponse.json({ areas: [], suburbs });
      }

      const areas = Object.keys(metros).sort((a, b) => a.localeCompare(b));
      return NextResponse.json({ areas, suburbs: [] });
    }

    const data = (await loadDataFile("crime")) as CrimeJson;
    const districts = data.districts?.[province] ?? {};
    const areas = Object.keys(districts).sort((a, b) => a.localeCompare(b));
    return NextResponse.json({ areas, suburbs: [] });
  } catch {
    return NextResponse.json({ areas: [], suburbs: [] });
  }
}
