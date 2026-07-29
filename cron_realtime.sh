#!/bin/bash
# Libo Insights — Realtime scrapers (forex + energy)
# Schedule: every 30 minutes (see cron_setup.template)

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT" || exit 1

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

mkdir -p data logs

echo "$(date): Starting realtime scrapers (forex + energy)"
python3 run_scrapers.py --topics forex energy >> logs/realtime_cron.log 2>&1

./scripts/cron_git_push.sh \
    "data: realtime update — forex + energy" \
    "data/forex.json data/energy.json data/manifest.json"

echo "$(date): Realtime scrapers completed"
