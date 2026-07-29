# Cron Jobs Setup

Libo Insights production data pipeline uses **server cron** on your own host (VPS, home server, or SA VM). Scrapers run locally, commit `data/*.json`, and push to GitHub — **no GitHub Actions** (avoids Actions billing).

Vercel redeploys when those commits land on `master` (data is copied at build via `prebuild`).

## One-time server setup

On a Linux host with git push access to this repo (deploy key or PAT):

```bash
# Clone (or pull) the repo
git clone https://github.com/ZolileN/sa_insghts_hub.git
cd sa_insghts_hub
git checkout master

# Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Optional: test a scrape
python3 run_scrapers.py --topics forex energy

# Install cron (auto-detects repo path)
chmod +x cron_*.sh scripts/cron_git_push.sh cron_manager.sh
./cron_manager.sh install
./cron_manager.sh status
```

**South Africa host recommended** for DWS water (`cron_weekly.sh`) — government sites often block foreign datacenter IPs.

### Git credentials on the server

Cron must be able to `git push` without a password prompt:

```bash
# SSH deploy key (recommended)
ssh-keygen -t ed25519 -f ~/.ssh/libo_insights_deploy -N ""
# Add ~/.ssh/libo_insights_deploy.pub as a deploy key on GitHub (write access)

git remote set-url origin git@github.com:ZolileN/sa_insghts_hub.git
```

Or use a fine-scoped PAT with `git credential` store — never commit tokens.

## Schedule

| Frequency | Topics | Schedule (UTC) | Script |
|-----------|--------|----------------|--------|
| Realtime | forex, energy | Every 30 min | `cron_realtime.sh` |
| Weekly | water | Mon 06:00 | `cron_weekly.sh` |
| Monthly | finance, property, employment, health | 1st 05:00 | `cron_monthly.sh` |
| Quarterly | all 10 topics | Jan/Apr/Jul/Oct 04:00 | `cron_quarterly.sh` |

`./cron_manager.sh install` writes `cron_setup.txt` with the correct absolute path (from `cron_setup.template`).

## Testing

```bash
./cron_manager.sh test-realtime
./cron_manager.sh test-weekly
./cron_manager.sh test-monthly
./cron_manager.sh test-quarterly
./cron_manager.sh logs
```

## Logs

- `logs/realtime_cron.log`
- `logs/weekly_cron.log`
- `logs/monthly_cron.log`
- `logs/quarterly_cron.log`
- `logs/scraper.log` (orchestrator)

## Notes

- Cron scripts `git pull --rebase` before push to reduce merge conflicts.
- Partial runs merge into `data/manifest.json` without dropping other topics.
- GitHub Actions workflows are **disabled** in this repo — do not rely on them for scraping.

## Alternative hosts (no GitHub Actions)

| Option | Notes |
|--------|--------|
| **SA VPS** (e.g. Afrihost, Hetzner, Oracle free tier) | Best for DWS + all scrapers |
| **Your Mac/Linux** with cron | Fine for dev; use `cron_manager.sh install` |
| **systemd timers** | Replace cron with `OnCalendar=` units calling the same `cron_*.sh` scripts |

Do **not** use GitHub Actions scheduled workflows for scraping if you want to avoid Actions minutes billing.
