#!/bin/bash
# SA Insight Hub - Cron Jobs Setup Script
# This script helps you install, view, and remove the cron jobs

PROJECT_DIR="/home/zolile/Documents/insights_hub"
cd "$PROJECT_DIR" || exit 1

case "$1" in
    install)
        echo "Installing cron jobs..."
        crontab cron_setup.txt
        echo "Cron jobs installed successfully!"
        echo ""
        echo "Current cron jobs:"
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
        echo "Latest quarterly log:"
        tail -20 logs/quarterly_cron.log 2>/dev/null || echo "No quarterly log found"
        ;;
    *)
        echo "Usage: $0 {install|uninstall|status|test-realtime|test-weekly|test-quarterly|logs}"
        echo ""
        echo "Commands:"
        echo "  install       - Install all cron jobs"
        echo "  uninstall     - Remove all cron jobs"
        echo "  status        - Show current cron jobs"
        echo "  test-realtime - Test the realtime scraper"
        echo "  test-weekly   - Test the weekly scraper"
        echo "  test-quarterly- Test the quarterly scraper"
        echo "  logs          - Show recent log files"
        exit 1
        ;;
esac
