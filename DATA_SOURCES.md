# Libo Insights — Public Data Sources

Free and publicly published sources used (or planned) to power each dashboard topic.
Commercial APIs (Lightstone deeds, suburb-level crime scores, etc.) are noted where they
would unlock deeper drill-down than SAPS precinct data.

## Crime

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| SAPS Crime Statistics | South African Police Service | Province totals, precinct (station), district/metro drill-down, TOP 30 hotspots | Quarterly | [crimestats.php](https://www.saps.gov.za/services/crimestats.php) — Excel workbooks |
| ISS Crime Hub | Institute for Security Studies | Context briefings, trend analysis (future enrichment) | Ad hoc | [issafrica.org](https://issafrica.org/iss-today) |
| SABRIC crime stats | Banking sector | Digital/banking crime crossover | Annual | [sabric.co.za](https://www.sabric.co.za) |

**Drill-down today:** Province → city/metro district (SAPS district field) → police precinct (station).
**With Mapbox:** geocode precincts or use metro boundaries for map shading.

## Property

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| FNB Property Barometer | FNB / FirstRand | House price trends, regional commentary | Monthly | [fnb.co.za property research](https://www.fnb.co.za/downloads/property/property-barometer.html) |
| PayProp Rental Index | PayProp | National rental growth (press releases) | Quarterly | [payprop.com/rental-index](https://payprop.com/rental-index) |
| Stats SA building stats | Stats SA | Building plans passed (structural demand) | Monthly | [P0142](https://www.statssa.gov.za) |
| Lightstone / deeds | Lightstone | Suburb median prices | Commercial | License required for API |
| Inside Airbnb | Community | Short-stay listing counts by city (CSV) | Periodic | [insideairbnb.com/get-the-data](https://insideairbnb.com/get-the-data/) — CSV on S3 (may block datacenter IPs) |
| AirROI data portal | AirROI | Airbnb performance benchmarks | Ad hoc | [airroi.com/data-portal](https://airroi.com/data-portal) |
| CSG DLRRD | Dept Rural Development & Land Reform | Cadastral / spatial layers | Ad hoc | [csg.dlrrd.gov.za](https://csg.dlrrd.gov.za) |
| GeoLayers | GeoLayers | Boundary datasets | Ad hoc | [geolayers.co.za/datasets](https://geolayers.co.za/datasets.html) |
| Cape Town Open Data | City of Cape Town | Property valuations, building stats | Monthly | [opendata.capetown.gov.za](https://opendata.capetown.gov.za) |
| valuations.org.za | Municipal valuations | Guideline property values | Annual | [valuations.org.za](https://valuations.org.za) |
| City of Joburg | Johannesburg | Municipal property & planning data | Ad hoc | [joburg.org.za](https://www.joburg.org.za) |
| Housing Finance Africa | CAHF | Rental affordability, mortgage access | Annual | [housingfinanceafrica.org](https://housingfinanceafrica.org) |
| Wazimap | OpenUp / Media Monitoring Africa | Census & community income/housing context | Census | [wazimap.co.za](https://wazimap.co.za) |

**Drill-down today:** Province → metro/district → suburb (where curated in `property.json`).
**Intelligence cards:** bond estimate, rent estimate, rent-vs-bond ratio, affordability index, price-to-income, Airbnb supply proxy, building-plans growth.

## Finance

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| SARB MPC statements | South African Reserve Bank | Repo rate, prime, policy outlook | ~6× per year | [resbank.co.za](https://www.resbank.co.za) PDF/HTML |
| Stats SA CPI | Stats SA | Headline inflation | Monthly | P0141 PDF |
| BankservAfrica Economic Transactions Index | BankservAfrica | Payment activity pulse | Monthly | Public press releases |

## Employment

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| Stats SA QLFS | Stats SA | Unemployment, youth unemployment, provinces | Quarterly | P0211 PDF |
| Adcorp Employment Index | Adcorp | Near-term hiring sentiment (future) | Monthly | Press releases |

## Energy

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| Eskom loadshedding API | Eskom | Current stage, schedules | Real-time | Public endpoints (scraped in `scrapers/energy.py`) |
| CSIR / Eskom statistics | Eskom | Generation mix (future) | Monthly | Eskom weekly system reports |

## Water

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| DWS Weekly State of Reservoirs | Dept of Water & Sanitation | Provincial dam % | Weekly | [dws.gov.za Hydrology](https://www.dws.gov.za/Hydrology/Weekly/Province.aspx) — often blocked outside SA |

## Health

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| SANAC / UNAIDS | Govt + UN | HIV prevalence, ART coverage | Annual | Public reports |
| NICD communiqués | NICD | Outbreak & TB updates (future scrape) | Weekly | [nicd.ac.za](https://www.nicd.ac.za) |
| NDOH DHIS2 | National Dept of Health | Facility indicators | Quarterly | `dhis.gov.za` — partial public read |

## Education

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| DBE NSC results | Dept of Basic Education | Matric pass rates by province | Annual (January) | DBE / [gov.za speeches](https://www.gov.za) |
| IEB / SACAI | Private assessment bodies | Independent school outcomes | Annual | Press releases |

## Fraud

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| SABRIC annual report | South African Banking Risk Information Centre | Banking fraud losses by category | Annual | PDF on [sabric.co.za](https://www.sabric.co.za/media-and-news/annual-reports/) |

## Forex

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| Exchange rate API | SARB-linked / market feeds | USD/ZAR and major pairs | Real-time | Public FX endpoints in `scrapers/forex.py` |

## Implementation notes

- Scrapers live in `scrapers/`; schedules in `cron_*.sh` and `CRON_SETUP.md`.
- `data/*.json` is the canonical cache; Next.js syncs via `apps/web/scripts/sync-data.mjs`.
- When a government site blocks cloud IPs, run the relevant cron job on a South African host and commit refreshed JSON.
