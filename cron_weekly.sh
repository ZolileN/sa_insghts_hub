#!/bin/bash
# Libo Insights — Weekly scrapers (DWS dam levels)
# Schedule: every Monday at 06:00 UTC (08:00 SAST)

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR" || exit 1

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

mkdir -p data logs

echo "$(date): Starting weekly scrapers (water)"
python3 run_scrapers.py --topics water >> logs/weekly_cron.log 2>&1

if git diff --quiet data/; then
    echo "$(date): No changes to commit"
else
    echo "$(date): Committing changes"
    git add data/water.json data/manifest.json
    git commit -m "data: weekly update — water [skip ci]"
    git push origin master
fi

echo "$(date): Weekly scrapers completed"
