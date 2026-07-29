#!/bin/bash
# Entry point for Cursor Cloud Automations — runs scrapers and pushes data to master.
# Usage: ./scripts/cursor_agent_refresh.sh <realtime|weekly|monthly|quarterly>
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MODE="${1:?usage: $0 <realtime|weekly|monthly|quarterly>}"

case "$MODE" in
  realtime)  exec "$ROOT/cron_realtime.sh" ;;
  weekly)    exec "$ROOT/cron_weekly.sh" ;;
  monthly)   exec "$ROOT/cron_monthly.sh" ;;
  quarterly) exec "$ROOT/cron_quarterly.sh" ;;
  *)
    echo "Unknown mode: $MODE"
    echo "Valid modes: realtime, weekly, monthly, quarterly"
    exit 1
    ;;
esac
