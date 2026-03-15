# Cron Jobs Setup

The SA Insight Hub now uses local cron jobs instead of GitHub Actions for automated scraping.

## Quick Setup

```bash
# Install all cron jobs
./cron_manager.sh install

# View current cron jobs
./cron_manager.sh status

# Remove all cron jobs
./cron_manager.sh uninstall
```

## Schedule Overview

| Frequency | Topics | Schedule | Script |
|-----------|--------|----------|--------|
| Realtime | forex, energy | Every 30 minutes | `cron_realtime.sh` |
| Weekly | water, finance, property | Mondays 06:00 UTC | `cron_weekly.sh` |
| Quarterly | All 10 topics | 1st of Jan, Apr, Jul, Oct 04:00 UTC | `cron_quarterly.sh` |

## Testing

```bash
# Test individual scrapers
./cron_manager.sh test-realtime
./cron_manager.sh test-weekly
./cron_manager.sh test-quarterly

# View logs
./cron_manager.sh logs
```

## Log Files

- `logs/realtime_cron.log` - Realtime scraper logs
- `logs/weekly_cron.log` - Weekly scraper logs  
- `logs/quarterly_cron.log` - Quarterly scraper logs

## Features

- ✅ Same schedules as GitHub Actions
- ✅ Automatic git commits and pushes
- ✅ Error handling and logging
- ✅ Timeout protection for quarterly runs
- ✅ Automatic log cleanup (30 days)
- ✅ Virtual environment activation
- ✅ Directory creation

## Migration from GitHub Actions

The GitHub Actions workflows have been disabled (renamed to `.yml.disabled`) but preserved for reference if needed. The cron jobs provide identical functionality with local execution.

## Manual Cron Configuration

If you prefer to edit crontab directly:

```bash
crontab -e
```

Then paste the contents of `cron_setup.txt`.
