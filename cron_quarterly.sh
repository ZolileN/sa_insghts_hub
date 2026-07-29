#!/bin/bash
# Libo Insights — Quarterly scrapers (all 10 topics)
# Schedule: 1st of January, April, July, October at 04:00 UTC

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR" || exit 1

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

if git diff --quiet data/; then
    echo "$(date): No changes to commit"
else
    echo "$(date): Committing changes"
    git add data/*.json
    git commit -m "data: quarterly full refresh — all 10 topics [skip ci]"
    git push origin master
fi

echo "$(date): Quarterly scrapers completed"
