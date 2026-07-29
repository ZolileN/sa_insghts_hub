# AGENTS.md

## Cursor Cloud specific instructions

Libo Insights is a Next.js dashboard (`apps/web`) backed by cached JSON in
`data/*.json`, plus optional data scrapers (`run_scrapers.py` + `scrapers/`).

### Running the app (main service)
- `cd apps/web && npm install && npm run dev` — serves on `http://localhost:3000`.
- The dashboard renders fully from committed `data/*.json`, so it works with no
  network access, no API keys, and without running any scraper first.
- `npm run dev` syncs `data/*.json` into `apps/web/data` via the `predev` hook.

### Production data refresh (Cursor Automations)
- **Scheduled runs:** See `CURSOR_AUTOMATIONS.md`. Automations should run
  `./scripts/cursor_agent_refresh.sh <realtime|weekly|monthly|quarterly>` only.
- **Do not edit source code** during automation runs — only `data/` and `logs/`.
- **Push to `master`** (not a PR) so Vercel deploys. PR creation should be disabled.
- Prompt templates live in `automations/*.prompt.txt`.

### Scrapers (manual)
- `./scripts/refresh-data.sh` then `git push` — see `CRON_SETUP.md`.
- `python3 run_scrapers.py` — `--topics`, `--parallel`, `--dry-run` supported.
- Running scrapers overwrites `data/*.json` and `data/manifest.json` (committed).
  Revert with `git checkout -- data/` unless you intend to commit refreshed data.

### Notes
- Python scrapers use `requirements.txt`; Python 3.11+ works.
- Deploy the web app from `apps/web` on Vercel (see `README.md`).
