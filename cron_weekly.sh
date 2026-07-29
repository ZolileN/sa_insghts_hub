#!/bin/bash
# Libo Insights — Weekly scrapers (DWS water)
# Schedule: every Monday 06:00 UTC

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT" || exit 1

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

mkdir -p data logs

echo "$(date): Starting weekly scrapers (water)"
python3 run_scrapers.py --topics water >> logs/weekly_cron.log 2>&1

./scripts/cron_git_push.sh \
    "data: weekly update — water" \
    "data/water.json data/manifest.json"

echo "$(date): Weekly scrapers completed"
