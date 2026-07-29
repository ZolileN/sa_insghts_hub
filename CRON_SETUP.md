# Data refresh guide

How to update dashboard figures. **Default: run scrapers on your machine**, commit, push. No VPS, GitHub Actions, or cron-job.org required.

Vercel rebuilds the site when `data/*.json` changes land on `master`.

---

## One-time setup (your machine)

```bash
git clone https://github.com/ZolileN/sa_insghts_hub.git
cd sa_insghts_hub

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Refresh data (manual)

**All 10 topics** (~2 minutes, some sources may be slow):

```bash
source .venv/bin/activate
./scripts/refresh-data.sh
```

**Specific topics only:**

```bash
./scripts/refresh-data.sh forex energy
./scripts/refresh-data.sh crime
./scripts/refresh-data.sh water
```

Or without the helper script:

```bash
python3 run_scrapers.py                    # all topics
python3 run_scrapers.py --topics crime forex
python3 run_scrapers.py --parallel         # faster full run
python3 run_scrapers.py --schedule         # show recommended cadence
```

---

## Publish to production

After scrapers finish:

```bash
git add data/
git commit -m "data: manual refresh"
git push origin master
```

Vercel deploys automatically (Root Directory: `apps/web`). New figures appear after the deploy completes (~1–2 min).

**You do not need `git pull` on your laptop for Vercel** — push from the same machine you ran scrapers on, or pull elsewhere only if you use multiple clones.

---

## Suggested cadence (when you choose to run)

| When | Command |
|------|---------|
| Often | `./scripts/refresh-data.sh forex energy` |
| Weekly | `./scripts/refresh-data.sh water` |
| Monthly | `./scripts/refresh-data.sh finance property employment health` |
| Quarterly | `./scripts/refresh-data.sh` (all topics) |

---

## Notes

- Scrapers merge **live API/PDF data** with the last `data/*.json` if a source fails (no fake hardcoded numbers).
- **DWS water** may fail outside South Africa; last successful water file stays until you run from an SA network or VPN.
- **Local dashboard dev:** `cd apps/web && npm run dev` syncs `data/` automatically.

---

## Optional automation (not required)

If you later want schedules without GitHub Actions:

| Method | Doc |
|--------|-----|
| Local crontab | `./cron_manager.sh install` |
| cron-job.org + webhook | `webhook_server.py` + `.env` — see repo history / `deploy/` |

GitHub Actions scraping is **disabled** in this repo.
