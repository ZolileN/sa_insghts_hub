#!/bin/bash
# Libo Insights — Quarterly scrapers (all 10 topics)
# Schedule: 1st of Jan, Apr, Jul, Oct at 04:00 UTC

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT" || exit 1

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

mkdir -p data logs

echo "$(date): Starting quarterly scrapers (all 10 topics)"
timeout 1800 python3 run_scrapers.py --parallel >> logs/quarterly_cron.log 2>&1

if [ $? -eq 124 ]; then
    echo "$(date): Quarterly scrapers timed out after 30 minutes"
    exit 1
fi

./scripts/cron_git_push.sh \
    "data: quarterly full refresh — all 10 topics" \
    data/

echo "$(date): Quarterly scrapers completed"
