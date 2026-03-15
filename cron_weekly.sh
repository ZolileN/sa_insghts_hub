#!/bin/bash
# SA Insight Hub - Weekly Scrapers (Water + Finance + Property)
# Replaces GitHub Actions scrape_weekly.yml
# Schedule: Every Monday at 06:00 UTC (08:00 SAST)

# Set the project directory
PROJECT_DIR="/home/zolile/Documents/insights_hub"
cd "$PROJECT_DIR" || exit 1

# Activate virtual environment
source .venv/bin/activate || exit 1

# Create directories if they don't exist
mkdir -p data logs

# Run the scrapers
echo "$(date): Starting weekly scrapers (water + finance + property)"
python run_scrapers.py --topics water finance property >> logs/weekly_cron.log 2>&1

# Commit changes if any
if git diff --quiet data/; then
    echo "$(date): No changes to commit"
else
    echo "$(date): Committing changes"
    git add data/water.json data/finance.json data/property.json data/manifest.json
    git commit -m "data: weekly update — water + finance + property [skip ci]"
    git push origin master
fi

echo "$(date): Weekly scrapers completed"
