# Data refresh guide

How dashboard figures get updated on production (Vercel).

**Recommended:** [Cursor Automations](CURSOR_AUTOMATIONS.md) — scheduled Cloud Agents run scrapers and push `data/` to `master`.

---

## Cursor Automations (recommended)

Four schedules match the repo cron scripts (realtime / weekly / monthly / quarterly).

**Setup:** [CURSOR_AUTOMATIONS.md](CURSOR_AUTOMATIONS.md) — copy prompts from `automations/*.prompt.txt` into [cursor.com/automations/new](https://cursor.com/automations/new).

**Entry script:** `./scripts/cursor_agent_refresh.sh <realtime|weekly|monthly|quarterly>`

---

## Manual (your machine)

### One-time setup

```bash
git clone https://github.com/ZolileN/sa_insghts_hub.git
cd sa_insghts_hub
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Refresh

```bash
./scripts/refresh-data.sh              # all topics
./scripts/refresh-data.sh forex energy # quick realtime
```

### Publish

```bash
git add data/
git commit -m "data: manual refresh"
git push origin master
```

Vercel redeploys automatically (Root Directory: `apps/web`).

---

## Cadence reference

| When | Mode / command |
|------|----------------|
| Daily 07:00 UTC | `cursor_agent_refresh.sh realtime` |
| Weekly (Mon) | `cursor_agent_refresh.sh weekly` |
| Monthly (1st) | `cursor_agent_refresh.sh monthly` |
| Quarterly | `cursor_agent_refresh.sh quarterly` |

---

## Notes

- Scrapers merge live data with last `data/*.json` on failure (no hardcoded fallbacks).
- **DWS water** may fail outside South Africa.
- GitHub Actions scraping is **disabled**.

---

## Other automation (optional)

| Method | Doc |
|--------|-----|
| Local crontab | `./cron_manager.sh install` |
| cron-job.org webhook | `webhook_server.py` + `deploy/` |
