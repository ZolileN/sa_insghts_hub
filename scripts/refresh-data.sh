#!/bin/bash
# Run scrapers manually and print next steps to publish data.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

if [ $# -eq 0 ]; then
  python3 run_scrapers.py
else
  python3 run_scrapers.py --topics "$@"
fi

echo ""
echo "Scrapers finished. To update production:"
echo "  git add data/"
echo "  git commit -m \"data: manual refresh\""
echo "  git push origin master"
echo ""
echo "Vercel will redeploy when the push lands on master."
