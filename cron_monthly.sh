#!/bin/bash
# Libo Insights — Monthly scrapers (SARB + CPI + property + employment QLFS)
# Schedule: 1st of each month at 05:00 UTC (07:00 SAST)

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR" || exit 1

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

mkdir -p data logs

echo "$(date): Starting monthly scrapers (finance, property, employment)"
python3 run_scrapers.py --topics finance property employment >> logs/monthly_cron.log 2>&1

if git diff --quiet data/; then
    echo "$(date): No changes to commit"
else
    echo "$(date): Committing changes"
    git add data/finance.json data/property.json data/employment.json data/manifest.json
    git commit -m "data: monthly update — finance, property, employment [skip ci]"
    git push origin master
fi

echo "$(date): Monthly scrapers completed"
