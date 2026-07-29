#!/bin/bash
# Libo Insights — Cron Jobs Setup Script

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR" || exit 1

case "$1" in
    install)
        echo "Installing cron jobs..."
        echo "Edit LIBO_INSIGHTS_ROOT in cron_setup.txt if needed (currently may point to /workspace)."
        crontab cron_setup.txt
        echo "Cron jobs installed successfully!"
        echo ""
        crontab -l
        ;;
    uninstall)
        echo "Removing cron jobs..."
        crontab -r
        echo "Cron jobs removed successfully!"
        ;;
    status)
        echo "Current cron jobs:"
        crontab -l
        ;;
    test-realtime)
        echo "Testing realtime scraper..."
        ./cron_realtime.sh
        ;;
    test-weekly)
        echo "Testing weekly scraper..."
        ./cron_weekly.sh
        ;;
    test-monthly)
        echo "Testing monthly scraper..."
        ./cron_monthly.sh
        ;;
    test-quarterly)
        echo "Testing quarterly scraper..."
        ./cron_quarterly.sh
        ;;
    logs)
        echo "Recent log files:"
        ls -la logs/
        echo ""
        echo "Latest realtime log:"
        tail -20 logs/realtime_cron.log 2>/dev/null || echo "No realtime log found"
        echo ""
        echo "Latest weekly log:"
        tail -20 logs/weekly_cron.log 2>/dev/null || echo "No weekly log found"
        echo ""
        echo "Latest monthly log:"
        tail -20 logs/monthly_cron.log 2>/dev/null || echo "No monthly log found"
        echo ""
        echo "Latest quarterly log:"
        tail -20 logs/quarterly_cron.log 2>/dev/null || echo "No quarterly log found"
        ;;
    *)
        echo "Usage: $0 {install|uninstall|status|test-realtime|test-weekly|test-monthly|test-quarterly|logs}"
        exit 1
        ;;
esac
