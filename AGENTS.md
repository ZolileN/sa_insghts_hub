# AGENTS.md

## Cursor Cloud specific instructions

Libo Insights is a Next.js dashboard (`apps/web`) backed by cached JSON in
`data/*.json`, plus optional data scrapers (`run_scrapers.py` + `scrapers/`).

### Running the app (main service)
- `cd apps/web && npm install && npm run dev` — serves on `http://localhost:3000`.
- The dashboard renders fully from committed `data/*.json`, so it works with no
  network access, no API keys, and without running any scraper first.
- `npm run dev` syncs `data/*.json` into `apps/web/data` via the `predev` hook.

### Scrapers (optional)
- `python3 run_scrapers.py` fetches live South African public data; `--dry-run`,
  `--topics <name...>`, and `--parallel` are supported (see `README.md`).
- **Production schedule:** [cron-job.org](https://cron-job.org) HTTP calls
  `webhook_server.py` on your VPS (see `CRON_SETUP.md`). Not GitHub Actions.
- Running scrapers overwrites `data/*.json` and `data/manifest.json` (these files ARE
  committed). Revert scraper-caused edits with `git checkout -- data/` unless you
  intend to commit refreshed data.
- Scrapers hit external gov/finance sites; individual topics may fail if a source is
  down or blocked. The app still works from cached data.

### Notes
- Python scrapers use `requirements.txt` (pandas, requests, etc.); Python 3.11+ works.
- Deploy the web app from `apps/web` on Vercel (see `README.md`).
