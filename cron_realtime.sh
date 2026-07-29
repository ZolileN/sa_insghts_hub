#!/bin/bash
# Libo Insights — Realtime scrapers (forex + energy)
# Schedule: every 30 minutes

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR" || exit 1

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

mkdir -p data logs

echo "$(date): Starting realtime scrapers (forex + energy)"
python3 run_scrapers.py --topics forex energy >> logs/realtime_cron.log 2>&1

if git diff --quiet data/; then
    echo "$(date): No changes to commit"
else
    echo "$(date): Committing changes"
    git add data/forex.json data/energy.json data/manifest.json
    git commit -m "data: realtime update — forex + energy [skip ci]"
    git push origin master
fi

echo "$(date): Realtime scrapers completed"
