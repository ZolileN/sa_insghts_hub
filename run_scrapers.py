#!/usr/bin/env python3
"""
SA Insight Hub — Master Data Scraper
=======================================
Runs all 10 topic scrapers in sequence (or parallel) and saves
results to data/  as JSON files that app.py reads at startup.

Usage:
    python run_scrapers.py                 # run all scrapers
    python run_scrapers.py --topics crime forex water   # specific topics
    python run_scrapers.py --parallel      # run concurrently (faster)
    python run_scrapers.py --dry-run       # report status without saving

Schedule via GitHub Actions or cron:
    # crontab entry — runs every Monday at 06:00 SAST
    0 6 * * 1 cd /app && python run_scrapers.py >> logs/scraper.log 2>&1

    # Or quarterly for slow-changing data (crime, education)
    0 6 1 */3 * cd /app && python run_scrapers.py --topics crime education employment health
"""

import argparse
import json
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# ── Ensure directories exist ────────────────────────────────────────────────────
DATA_DIR = Path("data")
LOG_DIR  = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/scraper.log", mode="a"),
    ],
)
log = logging.getLogger("orchestrator")

# ── Import all scrapers ───────────────────────────────────────────────────────
from scrapers.crime              import fetch as fetch_crime
from scrapers.forex              import fetch as fetch_forex
from scrapers.water              import fetch as fetch_water
from scrapers.finance            import fetch as fetch_finance
from scrapers.energy             import fetch as fetch_energy
from scrapers.employment         import fetch as fetch_employment
from scrapers.health             import fetch as fetch_health
from scrapers.education          import fetch as fetch_education
from scrapers.property_and_fraud import fetch as fetch_property
from scrapers.property_and_fraud import fetch_fraud

# ── Scraper registry ──────────────────────────────────────────────────────────
SCRAPERS = {
    "crime":      {"fn": fetch_crime,      "cadence": "quarterly", "label": "🔴 SAPS Crime Stats"},
    "forex":      {"fn": fetch_forex,      "cadence": "realtime",  "label": "💱 ZAR Exchange Rate"},
    "water":      {"fn": fetch_water,      "cadence": "weekly",    "label": "💧 DWS Dam Levels"},
    "finance":    {"fn": fetch_finance,    "cadence": "monthly",   "label": "💰 SARB Repo + CPI"},
    "energy":     {"fn": fetch_energy,     "cadence": "realtime",  "label": "⚡ Eskom Load Shedding"},
    "employment": {"fn": fetch_employment, "cadence": "quarterly", "label": "📉 Stats SA QLFS"},
    "health":     {"fn": fetch_health,     "cadence": "quarterly", "label": "🏥 NDOH Health Data"},
    "education":  {"fn": fetch_education,  "cadence": "annual",    "label": "🎓 DBE Matric Results"},
    "property":   {"fn": fetch_property,   "cadence": "monthly",   "label": "🏠 Property Prices"},
    "fraud":      {"fn": fetch_fraud,      "cadence": "annual",    "label": "🔐 SABRIC Fraud Data"},
}

# ── Recommended run frequency ─────────────────────────────────────────────────
CADENCE_SCHEDULE = {
    "realtime":  "Every 15 min (forex) / hourly (energy stage)",
    "weekly":    "Every Monday 06:00 SAST",
    "monthly":   "1st of each month",
    "quarterly": "Jan, Apr, Jul, Oct (Stats SA release schedule)",
    "annual":    "January (matric) / June (SABRIC)",
}


def run_scraper(key: str, dry_run: bool = False) -> dict:
    """Run a single scraper and return a result summary."""
    meta   = SCRAPERS[key]
    label  = meta["label"]
    fn     = meta["fn"]
    start  = time.time()

    if dry_run:
        log.info(f"[DRY RUN] Would run: {label}")
        return {"topic": key, "label": label, "status": "skipped", "elapsed_s": 0}

    try:
        log.info(f"▶ Starting: {label}")
        data = fn(DATA_DIR)
        elapsed = round(time.time() - start, 2)
        is_live = data.get("is_live", False)
        log.info(f"✅ Done: {label}  ({elapsed}s)  live={is_live}")
        return {
            "topic": key, "label": label, "status": "success",
            "is_live": is_live, "elapsed_s": elapsed,
        }
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        log.error(f"❌ Failed: {label} — {e}")
        return {
            "topic": key, "label": label, "status": "error",
            "error": str(e), "elapsed_s": elapsed,
        }


def run_all(topics: list[str], parallel: bool = False, dry_run: bool = False) -> list[dict]:
    """Run the selected scrapers and return summary."""
    results = []

    if parallel:
        log.info(f"Running {len(topics)} scrapers in parallel...")
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {pool.submit(run_scraper, t, dry_run): t for t in topics}
            for future in as_completed(futures):
                results.append(future.result())
    else:
        log.info(f"Running {len(topics)} scrapers sequentially...")
        for topic in topics:
            results.append(run_scraper(topic, dry_run))

    return results


def write_manifest(results: list[dict]):
    """Write a data/manifest.json with scrape timestamps and statuses."""
    manifest = {
        "last_run": datetime.utcnow().isoformat(),
        "topics": {
            r["topic"]: {
                "label":     r["label"],
                "status":    r["status"],
                "is_live":   r.get("is_live", False),
                "elapsed_s": r.get("elapsed_s", 0),
                "cadence":   SCRAPERS[r["topic"]]["cadence"],
                "schedule":  CADENCE_SCHEDULE[SCRAPERS[r["topic"]]["cadence"]],
            }
            for r in results
        },
    }
    (DATA_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))
    log.info(f"Manifest written → {DATA_DIR}/manifest.json")
    return manifest


def print_summary(results: list[dict]):
    """Print a formatted summary table."""
    print("\n" + "─" * 68)
    print(f"{'TOPIC':<30} {'STATUS':<10} {'LIVE':<6} {'TIME':>6}")
    print("─" * 68)
    for r in sorted(results, key=lambda x: x["topic"]):
        status_icon = "✅" if r["status"] == "success" else ("⏭️" if r["status"] == "skipped" else "❌")
        live   = "🟢" if r.get("is_live") else ("⚪" if r["status"] == "skipped" else "🟡")
        elapsed = f"{r['elapsed_s']:.1f}s" if r["elapsed_s"] else "—"
        print(f"{status_icon} {r['label']:<28} {r['status']:<10} {live}     {elapsed:>6}")
    print("─" * 68)

    ok  = sum(1 for r in results if r["status"] == "success")
    err = sum(1 for r in results if r["status"] == "error")
    skp = sum(1 for r in results if r["status"] == "skipped")
    live_count = sum(1 for r in results if r.get("is_live"))
    print(f"  ✅ {ok} succeeded   ❌ {err} failed   ⏭️ {skp} skipped")
    print(f"  🟢 {live_count}/{ok} topics returned live data")
    print("─" * 68 + "\n")


def print_schedule():
    """Print the recommended scraping schedule."""
    print("\n📅 Recommended scraping schedule:")
    for key, meta in SCRAPERS.items():
        print(f"  {meta['label']:<35} {meta['cadence']:<12}  {CADENCE_SCHEDULE[meta['cadence']]}")
    print()


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="SA Insight Hub — run data scrapers for all 10 topics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_scrapers.py                        # run all 10 scrapers
  python run_scrapers.py --topics crime forex   # run 2 specific scrapers
  python run_scrapers.py --parallel             # run all concurrently
  python run_scrapers.py --dry-run              # test without fetching
  python run_scrapers.py --schedule             # show cadence schedule
        """
    )
    parser.add_argument("--topics",   nargs="+", choices=list(SCRAPERS), metavar="TOPIC",
                        help="which scrapers to run (default: all)")
    parser.add_argument("--parallel", action="store_true",
                        help="run scrapers concurrently")
    parser.add_argument("--dry-run",  action="store_true",
                        help="show what would run without fetching")
    parser.add_argument("--schedule", action="store_true",
                        help="print recommended schedule and exit")
    args = parser.parse_args()

    if args.schedule:
        print_schedule()
        return

    topics = args.topics or list(SCRAPERS.keys())
    invalid = [t for t in topics if t not in SCRAPERS]
    if invalid:
        log.error(f"Unknown topics: {invalid}. Choose from: {list(SCRAPERS.keys())}")
        sys.exit(1)

    log.info(f"SA Insight Hub scraper started — topics: {topics}")
    total_start = time.time()

    results  = run_all(topics, parallel=args.parallel, dry_run=args.dry_run)
    manifest = write_manifest(results)
    print_summary(results)

    total = round(time.time() - total_start, 1)
    log.info(f"All done in {total}s. Data saved to {DATA_DIR}/")


if __name__ == "__main__":
    main()
