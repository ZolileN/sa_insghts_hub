# Cron Jobs Setup

Libo Insights uses **GitHub Actions** for production scraping (recommended) and optional **server cron** for SA-hosted runs (DWS water).

## Production (GitHub Actions)

Workflows in `.github/workflows/` run automatically and commit refreshed `data/*.json` to `master`:

| Workflow | Schedule | Topics |
|----------|----------|--------|
| `scrape_realtime.yml` | Every 30 min | forex, energy |
| `scrape_weekly.yml` | Mondays 06:00 UTC | water |
| `scrape_monthly.yml` | 1st of month 05:00 UTC | finance, property, employment, health |
| `scrape_quarterly.yml` | Jan/Apr/Jul/Oct 04:00 UTC | all 10 topics |

**Enable:** push these workflows to `master` (already in repo). In GitHub → **Actions**, confirm workflows are enabled for the repository.

Each data commit triggers a Vercel redeploy (data is synced at build via `prebuild`).

**Manual run:** Actions → pick workflow → **Run workflow**.

## Optional: server cron (SA host)

```bash
# Edit LIBO_INSIGHTS_ROOT in cron_setup.txt to your deploy path, then:
./cron_manager.sh install

# View current cron jobs
./cron_manager.sh status
```

## Schedule Overview

| Frequency | Topics | Schedule | Script |
|-----------|--------|----------|--------|
| Realtime | forex, energy | Every 30 minutes | `cron_realtime.sh` |
| Weekly | water | Mondays 06:00 UTC | `cron_weekly.sh` |
| Monthly | finance, property, employment, health | 1st of month 05:00 UTC | `cron_monthly.sh` |
| Quarterly | All 10 topics | 1st of Jan, Apr, Jul, Oct 04:00 UTC | `cron_quarterly.sh` |

Cadence matches each source’s publication schedule:

- **Forex / Eskom** — near real-time APIs
- **Water (DWS)** — weekly reservoir report (often blocked outside SA; run cron on SA-hosted server for live data)
- **Finance** — Stats SA CPI monthly; SARB MPC ~6× per year
- **Property** — FNB barometer, PayProp rental index (press); metros preserved in JSON
- **Employment (QLFS)** — Stats SA quarterly PDF with live provincial table parse

## Testing

```bash
./cron_manager.sh test-realtime
./cron_manager.sh test-weekly
./cron_manager.sh test-monthly
./cron_manager.sh test-quarterly
./cron_manager.sh logs
```

## Log Files

- `logs/realtime_cron.log`
- `logs/weekly_cron.log`
- `logs/monthly_cron.log`
- `logs/quarterly_cron.log`

## Notes

- Cron scripts use `PROJECT_DIR` relative to the script location — no hardcoded home paths.
- Partial runs merge into `data/manifest.json` without dropping other topics.
- DWS and some gov sites may block datacenter IPs; deploy weekly water cron on a South African host for live dam levels.
