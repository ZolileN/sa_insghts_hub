#!/bin/bash
# Libo Insights — Monthly scrapers
# Schedule: 1st of each month at 05:00 UTC

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT" || exit 1

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

mkdir -p data logs

echo "$(date): Starting monthly scrapers (finance, property, employment, health)"
python3 run_scrapers.py --topics finance property employment health >> logs/monthly_cron.log 2>&1

./scripts/cron_git_push.sh \
    "data: monthly update — finance, property, employment, health" \
    "data/finance.json data/property.json data/employment.json data/health.json data/manifest.json"

echo "$(date): Monthly scrapers completed"
