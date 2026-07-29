#!/usr/bin/env node
/**
 * Verifies committed dashboard data files exist and sync-data runs cleanly.
 */
import { existsSync, readFileSync } from "fs";
import { execSync } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dataDir = path.join(root, "..", "..", "data");
const topics = [
  "crime",
  "property",
  "fraud",
  "employment",
  "energy",
  "finance",
  "health",
  "education",
  "forex",
  "water",
];

let failed = false;

for (const topic of topics) {
  const file = path.join(dataDir, `${topic}.json`);
  if (!existsSync(file)) {
    console.error(`missing: data/${topic}.json`);
    failed = true;
    continue;
  }
  try {
    JSON.parse(readFileSync(file, "utf8"));
  } catch {
    console.error(`invalid JSON: data/${topic}.json`);
    failed = true;
  }
}

if (!existsSync(path.join(dataDir, "manifest.json"))) {
  console.error("missing: data/manifest.json");
  failed = true;
}

try {
  execSync("node scripts/sync-data.mjs", { cwd: root, stdio: "pipe" });
} catch {
  console.error("sync-data.mjs failed");
  failed = true;
}

if (failed) {
  process.exit(1);
}

console.log(`verify-data: OK (${topics.length} topic files + manifest)`);
