# Libo Insights

> South Africa's critical public data — ten topics, live scrapers, province-aware dashboards, and precinct-level crime drill-down.

Formerly **SA Insight Hub**. The UI is a Next.js app (`apps/web`) with a Precision Ops light theme.

![Next.js](https://img.shields.io/badge/Next.js-16-black?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

---

## What It Does

Libo Insights pulls real South African public data across 10 topics, caches it as JSON, and visualises it in interactive dashboards. Crime and Property support **province → city/metro → suburb/precinct** drill-down with Leaflet maps and clickable charts.

| # | Topic | Primary source | Cadence |
|---|-------|----------------|---------|
| 1 | Crime | SAPS quarterly Excel | Quarterly |
| 2 | Property | FNB Barometer · Lightstone press data | Monthly |
| 3 | Bank fraud | SABRIC annual report | Annual |
| 4 | Employment | Stats SA QLFS (PDF) | Quarterly |
| 5 | Energy | Eskom load-shedding status | Real-time |
| 6 | Finance | SARB MPC · Stats SA CPI | Monthly |
| 7 | Health | SANAC / NDOH DHIS2 | Quarterly |
| 8 | Education | DBE NSC / gov.za | Annual |
| 9 | Forex | Live FX API | Real-time |
| 10 | Water | DWS weekly dam levels | Weekly |

Full publisher list (FNB, PayProp, BankservAfrica, NICD, etc.) is in **[DATA_SOURCES.md](DATA_SOURCES.md)**.

---

## Quick Start

### Next.js dashboard

```bash
git clone https://github.com/ZolileN/sa_insghts_hub
cd sa_insghts_hub

# Python scrapers (optional — app works from committed data/*.json)
pip install -r requirements.txt
python3 run_scrapers.py

# Web app
cd apps/web
npm install
cp .env.example .env.local   # optional; maps use OpenStreetMap by default
npm run dev
```

Open **http://localhost:3000** — marketing home at `/`, dashboards at `/dashboard/crime`, etc.

`npm run dev` syncs `data/*.json` into `apps/web/data` automatically (`predev` hook).

### Deploy to Vercel

One Vercel project serves **both** the marketing landing page (`/`) and all dashboard routes (`/dashboard/*`).

1. Import [github.com/ZolileN/sa_insghts_hub](https://github.com/ZolileN/sa_insghts_hub) in the [Vercel dashboard](https://vercel.com/new).
2. Set **Root Directory** to `apps/web` (required — the Next.js app lives in the monorepo subfolder).
3. Framework preset: **Next.js** (detected automatically; `apps/web/vercel.json` is included).
4. **Environment variables** (Project → Settings → Environment Variables):
   - `NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN` — your Mapbox public token (maps)
   - `NEXT_PUBLIC_SITE_URL` — optional canonical URL, e.g. `https://your-project.vercel.app` or your custom domain
5. Deploy. Production URLs:
   - Landing: `https://<your-domain>/`
   - Dashboard: `https://<your-domain>/dashboard/crime` (and `/dashboard/property`, etc.)

**CLI link** (optional, from your machine):

```bash
cd apps/web
npx vercel link          # connect to your existing Vercel project
npx vercel env pull      # pull env vars into .env.local
npx vercel --prod        # production deploy
```

Data is baked in at build time via `prebuild` → `scripts/sync-data.mjs` (copies repo `data/` into the app). Push updated `data/*.json` to refresh production figures.

---

## Environment variables

Create `apps/web/.env.local` (gitignored):

```bash
# Required for Mapbox crime maps (client-side)
NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN=pk.your_token_here
```

You can also set the same values in a repo-root `.env` for local tooling. **Never commit real tokens.**

---

## Data scrapers

```bash
python3 run_scrapers.py                    # all 10 topics
python3 run_scrapers.py --topics crime forex
python3 run_scrapers.py --parallel         # concurrent run
python3 run_scrapers.py --dry-run
python3 run_scrapers.py --schedule         # print cadence table
```

Outputs land in `data/*.json` and `data/manifest.json`. These files are **committed** so the dashboard works without running scrapers first. After a local scrape, commit refreshed JSON if you want to share updated figures.

Scraper modules live in `scrapers/` with shared helpers in `scrapers/_common.py` (PDF parsing, retries, `lxml` for HTML).

---

## Cron automation (production)

Production scraping runs on **your server** via cron — not GitHub Actions. See **[CRON_SETUP.md](CRON_SETUP.md)** for VPS setup and git deploy keys.

| Frequency | Topics | Script |
|-----------|--------|--------|
| Every 30 min | forex, energy | `cron_realtime.sh` |
| Weekly (Mon 06:00 UTC) | water | `cron_weekly.sh` |
| Monthly (1st 05:00 UTC) | finance, property, employment, health | `cron_monthly.sh` |
| Quarterly (Jan/Apr/Jul/Oct) | all 10 | `cron_quarterly.sh` |

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
chmod +x cron_*.sh scripts/cron_git_push.sh cron_manager.sh
./cron_manager.sh install
./cron_manager.sh test-realtime
```

Commits push refreshed `data/*.json` to `master`; Vercel redeploys on push.

---

## Project structure

```
sa_insghts_hub/
├── apps/web/                 # Next.js 16 dashboard + marketing (primary UI)
│   ├── src/app/dashboard/    # Topic pages (crime, property, …)
│   ├── scripts/sync-data.mjs # Copies ../../data → apps/web/data
│   └── .env.local            # Mapbox token (local only)
├── data/                     # Cached scraper output (committed)
├── scrapers/                 # One fetch() per topic
├── run_scrapers.py           # CLI orchestrator
├── cron_*.sh                 # Scheduled scraper wrappers
├── DATA_SOURCES.md           # Public & commercial data catalog
├── CRON_SETUP.md             # Cron install guide
└── requirements.txt          # Python scraper dependencies
```

---

## Crime & property drill-down

On `/dashboard/crime` and `/dashboard/property`:

1. **Province** filter (header) — national or one province
2. **City / metro** filter — SAPS districts or property metros
3. **Suburb** filter (property only) — when a metro is selected
4. Click **map markers** or **chart bars** to drill at the same levels
5. URL reflects state: `?province=Western+Cape&city=City+of+Cape+Town&suburb=Sea+Point`

Crime adds police precinct views when a city/metro is selected.

---

## Key features

- Ten topic dashboards with KPI cards, Recharts visualisations, province filter
- Interactive Leaflet maps with click-to-drill on Crime, Property, Health, Employment, Education, and Water
- Property suburb drill-down via `?suburb=` URL (e.g. Sea Point within Cape Town)
- Source list and update date at the bottom of each page
- Smart fallback when a source is blocked (e.g. DWS from non-SA IPs — run cron on SA host)
- Marketing landing page with live ticker from cached JSON

---

## Roadmap

- [x] Next.js dashboard with Precision Ops theme
- [x] 2026 data refresh (SAPS, QLFS Q1 2026, CPI June 2026, NSC 2025, SARB MPC)
- [x] Cron schedules (realtime / weekly / monthly / quarterly)
- [x] Crime province → city → precinct drill-down
- [x] Property province → metro → suburb drill-down with maps and charts
- [x] Province drill-down maps on Health, Employment, Education, Water
- [x] NICD, Cape Town ArcGIS, Frankfurter forex ingestion
- [x] `DATA_SOURCES.md` publisher catalog
- [ ] Choropleth province boundaries (filled regions vs markers)
- [ ] Vulekamali / eTenders live budget feeds (SA-hosted cron)
- [ ] Inside Airbnb listing enrichment (Cape Town only on source site)
- [ ] Alerts (email/WhatsApp) for dam levels and crime spikes
- [ ] Public read API over `data/*.json`
- [ ] AI Q&A panel in Next.js dashboard

---

## Contributing

1. Add `scrapers/your_topic.py` with `fetch(output_dir: Path) -> dict`
2. Register in `run_scrapers.py` → `SCRAPERS`
3. Add `apps/web/src/app/dashboard/your_topic/page.tsx` and sidebar entry in `constants.ts`
4. Document the source in `DATA_SOURCES.md`

---

## License

MIT — free to use, fork, and build on.

---

Built by **Zolile Nonzapa** | Cape Town, South Africa  
[GitHub](https://github.com/ZolileN/sa_insghts_hub) · [Email](mailto:zolile@mlkcomputer.com)
