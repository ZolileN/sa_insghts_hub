#!/bin/bash
# Start the cron-job.org webhook server (production scraper trigger)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [ -z "${CRON_WEBHOOK_SECRET:-}" ]; then
  echo "Set CRON_WEBHOOK_SECRET in .env (see .env.example)"
  exit 1
fi

if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi

exec python3 webhook_server.py
