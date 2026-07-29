#!/bin/bash
# Libo Insights — Cron Jobs Setup Script

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR" || exit 1

install_crontab() {
    if [ ! -f "cron_setup.template" ]; then
        echo "cron_setup.template not found in $PROJECT_DIR"
        exit 1
    fi
    TMP="$(mktemp)"
    sed "s|__LIBO_INSIGHTS_ROOT__|$PROJECT_DIR|g" cron_setup.template > "$TMP"
    crontab "$TMP"
    rm -f "$TMP"
    # Keep a copy for reference (gitignored path optional)
    sed "s|__LIBO_INSIGHTS_ROOT__|$PROJECT_DIR|g" cron_setup.template > cron_setup.txt
    echo "Installed crontab for: $PROJECT_DIR"
}

case "$1" in
    install)
        echo "Installing cron jobs for $PROJECT_DIR ..."
        install_crontab
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
        echo "Project directory: $PROJECT_DIR"
        echo ""
        echo "Current cron jobs:"
        crontab -l 2>/dev/null || echo "(no crontab)"
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
        ls -la logs/ 2>/dev/null || echo "No logs directory yet"
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
