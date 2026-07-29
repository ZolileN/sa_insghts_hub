import { cpSync, existsSync, mkdirSync } from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const src = path.join(root, "../../data");
const dest = path.join(root, "data");

if (!existsSync(src)) {
  console.warn("sync-data: source data folder not found at", src);
  process.exit(0);
}

mkdirSync(dest, { recursive: true });
cpSync(src, dest, { recursive: true });
console.log("sync-data: copied data to apps/web/data");
