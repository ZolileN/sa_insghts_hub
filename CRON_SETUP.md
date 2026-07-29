# Cron Jobs Setup — cron-job.org

Production scraping uses **[cron-job.org](https://cron-job.org)** to HTTP-call a small webhook on your server. The webhook runs `cron_*.sh` (scrapers + git push to `master`). **No GitHub Actions** (no Actions billing). **No server crontab** required.

Vercel redeploys when data commits land on `master`.

---

## Architecture

```
cron-job.org  --HTTP GET-->  your VPS webhook_server.py  -->  cron_realtime.sh  -->  git push
```

---

## 1. Server setup (once)

On a Linux VPS (SA recommended for DWS water):

```bash
git clone https://github.com/ZolileN/sa_insghts_hub.git /opt/libo-insights
cd /opt/libo-insights
git checkout master

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

chmod +x cron_*.sh scripts/*.sh webhook_server.py

# Secrets
cp .env.example .env
# Edit .env — set CRON_WEBHOOK_SECRET to a long random string

# Git push access (deploy key on GitHub)
git remote set-url origin git@github.com:ZolileN/sa_insghts_hub.git

# Test webhook locally
./scripts/start-webhook.sh
curl "http://127.0.0.1:8765/health"
curl "http://127.0.0.1:8765/cron/realtime?token=YOUR_SECRET"
```

### HTTPS (required for cron-job.org)

Expose port `8765` with **HTTPS** using one of:

- **Caddy** or **nginx** reverse proxy → `https://scrapers.yourdomain.com`
- **Cloudflare Tunnel** (free) → public URL without opening ports

cron-job.org must reach your URL over the internet.

### Keep webhook running

```bash
# Option A: systemd (see deploy/cron-webhook.service)
sudo cp deploy/cron-webhook.service /etc/systemd/system/
# Edit User= and paths in the unit file
sudo systemctl enable --now cron-webhook

# Option B: screen/tmux for testing
./scripts/start-webhook.sh
```

---

## 2. cron-job.org jobs

Sign up at [cron-job.org](https://console.cron-job.org/). Create **four** cron jobs:

Replace `BASE` and `TOKEN`:

```
BASE=https://scrapers.yourdomain.com
TOKEN=your-CRON_WEBHOOK_SECRET
```

| Job title | URL | Schedule (cron-job.org) | UTC |
|-----------|-----|-------------------------|-----|
| Libo realtime | `{BASE}/cron/realtime?token={TOKEN}` | `*/30 * * * *` | Every 30 min |
| Libo weekly water | `{BASE}/cron/weekly?token={TOKEN}` | `0 6 * * 1` | Mon 06:00 |
| Libo monthly | `{BASE}/cron/monthly?token={TOKEN}` | `0 5 1 * *` | 1st 05:00 |
| Libo quarterly | `{BASE}/cron/quarterly?token={TOKEN}` | `0 4 1 1,4,7,10 *` | Jan/Apr/Jul/Oct 04:00 |

**Settings for each job:**

- Method: **GET** (or POST)
- Timeout: 30 seconds (webhook returns immediately; scrape runs in background)
- Enabled: yes
- Request failed notifications: optional email from cron-job.org

### Test from cron-job.org

Use **“Perform test run”** on each job. Expect HTTP **202** with JSON:

```json
{"status":"accepted","job":"realtime","script":"cron_realtime.sh"}
```

Check server logs: `logs/webhook_realtime.log`, `logs/realtime_cron.log`

---

## 3. Webhook endpoints

| Path | Script | Topics |
|------|--------|--------|
| `/health` | — | Liveness (no token) |
| `/cron/realtime` | `cron_realtime.sh` | forex, energy |
| `/cron/weekly` | `cron_weekly.sh` | water |
| `/cron/monthly` | `cron_monthly.sh` | finance, property, employment, health |
| `/cron/quarterly` | `cron_quarterly.sh` | all 10 topics |

Auth: `?token=SECRET` or header `X-Cron-Token: SECRET`

---

## 4. Logs

| File | Contents |
|------|----------|
| `logs/webhook_*.log` | Webhook-triggered run output |
| `logs/*_cron.log` | Scraper cron script output |
| `logs/scraper.log` | Orchestrator log |

---

## Alternative: server crontab

If you prefer not to use cron-job.org, `./cron_manager.sh install` still works (local crontab). See `cron_setup.template`.

---

## Security

- Use a long random `CRON_WEBHOOK_SECRET` (32+ chars).
- Do not commit `.env`.
- Prefer HTTPS only; do not expose the webhook without TLS on a public IP.
- GitHub Actions scraping remains **disabled** in this repo.
