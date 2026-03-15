#!/bin/bash
# SA Insight Hub - Realtime Scrapers (Forex + Energy)
# Replaces GitHub Actions scrape_realtime.yml
# Schedule: Every 30 minutes

# Set the project directory
PROJECT_DIR="/home/zolile/Documents/insights_hub"
cd "$PROJECT_DIR" || exit 1

# Activate virtual environment
source .venv/bin/activate || exit 1

# Create directories if they don't exist
mkdir -p data logs

# Run the scrapers
echo "$(date): Starting realtime scrapers (forex + energy)"
python run_scrapers.py --topics forex energy >> logs/realtime_cron.log 2>&1

# Commit changes if any
if git diff --quiet data/; then
    echo "$(date): No changes to commit"
else
    echo "$(date): Committing changes"
    git add data/forex.json data/energy.json data/manifest.json
    git commit -m "data: realtime update — forex + energy [skip ci]"
    git push origin master
fi

echo "$(date): Realtime scrapers completed"
