#!/bin/bash
# SA Insight Hub - Quarterly Scrapers (All 10 topics)
# Replaces GitHub Actions scrape_quarterly.yml
# Schedule: 1st of January, April, July, October at 04:00 UTC

# Set the project directory
PROJECT_DIR="/home/zolile/Documents/insights_hub"
cd "$PROJECT_DIR" || exit 1

# Activate virtual environment
source .venv/bin/activate || exit 1

# Create directories if they don't exist
mkdir -p data logs

# Run all scrapers in parallel
echo "$(date): Starting quarterly scrapers (all 10 topics)"
timeout 1800 python run_scrapers.py --parallel >> logs/quarterly_cron.log 2>&1

# Check if the command timed out
if [ $? -eq 124 ]; then
    echo "$(date): Quarterly scrapers timed out after 30 minutes"
    exit 1
fi

# Commit changes if any
if git diff --quiet data/; then
    echo "$(date): No changes to commit"
else
    echo "$(date): Committing changes"
    git add data/*.json
    git commit -m "data: quarterly full refresh — all 10 topics [skip ci]"
    git push origin master
fi

echo "$(date): Quarterly scrapers completed"
