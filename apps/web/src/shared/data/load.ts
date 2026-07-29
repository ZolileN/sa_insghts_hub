import { existsSync } from "fs";
import { readFile } from "fs/promises";
import path from "path";

function resolveDataDir(): string {
  const candidates = [
    path.join(process.cwd(), "data"),
    path.join(process.cwd(), "../../data"),
  ];
  for (const dir of candidates) {
    if (existsSync(path.join(dir, "manifest.json"))) return dir;
  }
  return candidates[1];
}

const DATA_DIR = resolveDataDir();

export async function loadJson<T>(stem: string): Promise<T | null> {
  try {
    const filePath = path.join(DATA_DIR, `${stem}.json`);
    const raw = await readFile(filePath, "utf-8");
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

export async function loadManifest() {
  return loadJson<{
    last_run?: string;
    topics?: Record<
      string,
      {
        label?: string;
        status?: string;
        is_live?: boolean;
        cadence?: string;
      }
    >;
  }>("manifest");
}

export function safeGet<T>(
  obj: unknown,
  keys: string[],
  fallback: T,
): T {
  let current: unknown = obj;
  for (const key of keys) {
    if (current == null || typeof current !== "object") return fallback;
    current = (current as Record<string, unknown>)[key];
  }
  return (current as T) ?? fallback;
}
