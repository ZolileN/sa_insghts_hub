#!/bin/bash
# Shared git commit + push for cron scraper runs.
# Usage: ./scripts/cron_git_push.sh "commit message" [paths...]
# Requires: repo cloned with push access (deploy key or credential helper).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1

COMMIT_MSG="${1:?commit message required}"
shift
PATHS=("${@:-data/}")

if ! git diff --quiet -- "${PATHS[@]}" 2>/dev/null; then
    git add -- "${PATHS[@]}"
    git commit -m "$COMMIT_MSG"
    for attempt in 1 2 3 4; do
        if git pull --rebase origin master && git push origin master; then
            echo "$(date): Pushed data update to origin/master"
            exit 0
        fi
        echo "$(date): git push failed (attempt $attempt), retrying..."
        sleep $((attempt * 4))
    done
    echo "$(date): ERROR: git push failed after retries"
    exit 1
else
    echo "$(date): No changes to commit"
fi
