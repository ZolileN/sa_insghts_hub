# Libo Insights — Public Data Sources & API Targets

Canonical catalog of free, open, and publicly published sources powering each dashboard topic.
Commercial APIs (Lightstone deeds, precinct risk scores, etc.) are noted where they unlock deeper drill-down.

---

## 1. Crime

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| SAPS Crime Statistics | South African Police Service | Station-level quarterly crime, province & district drill-down, TOP 30 hotspots | Quarterly | [saps.gov.za/services/crimestats.php](https://www.saps.gov.za/services/crimestats.php) |
| DataFirst UCT | University of Cape Town | Historical SAPS microdata CSVs by precinct | Ad hoc | [datafirst.uct.ac.za](https://www.datafirst.uct.ac.za/dataportal/index.php/catalog/SAPS) |
| ISS Crime Hub | Institute for Security Studies | Spatial analysis, maps, trend briefings | Ad hoc | [crimehub.issafrica.org](https://crimehub.issafrica.org) |
| Crime Stats SA | Independent aggregator | Cleaned station breakdown (contact, property, violent) | Quarterly | [crimestatssa.com](https://crimestatssa.com) |

**Drill-down:** Province → city/metro district (SAPS district) → police precinct (station).  
**Intelligence cards:** violent vs property totals, aggravated robbery, national hotspot leader, provincial murder rank.

---

## 2. Property

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| City of Cape Town Open Data | CoCT | GV rolls, zoning, building footprints, land use (CSV/GeoJSON/REST) | Annual / monthly | [opendata.capetown.gov.za](https://opendata.capetown.gov.za) |
| Chief Surveyor-General (CSG) | DLRRD | Cadastral parcels, erven, farm portions | Ad hoc | [csg.dlrrd.gov.za](https://csg.dlrrd.gov.za) |
| CAHF Citymark | Centre for Affordable Housing Finance Africa | Deeds market data, valuations, mortgage trends by subplace | Annual | [housingfinanceafrica.org](https://housingfinanceafrica.org) |
| Inside Airbnb | Community | Cape Town listing data, calendars, host density | Periodic | [insideairbnb.com/get-the-data](https://insideairbnb.com/get-the-data) |
| FNB Property Barometer | FNB / Lightstone | National & regional price trends | Monthly | [fnb.co.za/downloads/property](https://www.fnb.co.za/downloads/property/property-barometer.html) |
| PayProp Rental Index | PayProp | Rental growth press releases | Quarterly | [payprop.com/rental-index](https://payprop.com/rental-index) |
| Stats SA P0142 | Stats SA | Building plans passed | Monthly | [statssa.gov.za](https://www.statssa.gov.za) |
| Wazimap | OpenUp | Census income & housing context | Census | [wazimap.co.za](https://wazimap.co.za) |
| valuations.org.za | Municipal valuations | Guideline property values | Annual | [valuations.org.za](https://valuations.org.za) |
| GeoLayers | GeoLayers | Boundary datasets | Ad hoc | [geolayers.co.za/datasets.html](https://geolayers.co.za/datasets.html) |

**Drill-down:** Province → metro → suburb (curated in `property.json`).  
**Intelligence cards:** bond & rent estimates, rent-vs-bond, affordability, price-to-income, Airbnb supply, building-plans growth.

---

## 3. Fraud

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| SABRIC | Banking sector | Annual/quarterly fraud losses & threat matrices | Annual | [sabric.co.za](https://www.sabric.co.za) |
| FSCA Public Warnings | Financial Sector Conduct Authority | Unauthorized FSP lists, enforcement actions | Weekly | [fsca.co.za](https://www.fsca.co.za) |
| SIU Reports | Special Investigating Unit | Public sector corruption & tender fraud outcomes | Ad hoc | [siu.org.za](https://www.siu.org.za) |

**Intelligence cards:** YoY loss momentum, digital fraud share, loss per incident, SIM-swap severity.

---

## 4. Employment

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| Stats SA QLFS | Stats SA | Employment, unemployment, sectors, informal labour | Quarterly | P0211 via [statssa.gov.za](https://www.statssa.gov.za) & DataFirst |
| Wazimap | OpenUp | Ward/subplace employment, income, LFPR | Census | [wazimap.co.za](https://wazimap.co.za) |
| Dept of Employment & Labour | Govt | Labour market intelligence, sectoral determinations | Ad hoc | [labour.gov.za](https://www.labour.gov.za) |

**Intelligence cards:** Gini inequality, expanded unemployment, youth gap, provincial unemployment rank, wage floor context.

---

## 5. Energy

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| EskomSePush (ESP) | Community API | Loadshedding stage, schedules, grid alerts | Real-time | [sepush.co.za](https://sepush.co.za) |
| CSIR Energy Centre | CSIR | Grid mix, REIPPPP, storage modelling | Ad hoc | [csir.co.za](https://www.csir.co.za) |
| DMRE Fuel Prices | Dept Mineral Resources & Energy | Petrol, diesel, paraffin official prices | Monthly | [energy.gov.za](https://www.energy.gov.za) / Stats SA |

**Intelligence cards:** outage reduction vs prior year, upcoming schedules, est. monthly bill, renewable share.

---

## 6. Finance

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| Vulekamali | National Treasury / IMALI Yethu | Budget allocations, MTEF, department transfers | Annual | [vulekamali.gov.za](https://vulekamali.gov.za) |
| SARB Statistical Tables | South African Reserve Bank | Repo rate, money supply, Quarterly Bulletin CSV | Daily / quarterly | [resbank.co.za](https://www.resbank.co.za) |
| National Treasury eTenders | Treasury | Procurement, awarded tenders, supplier spend | Daily | [etenders.gov.za](https://www.etenders.gov.za) |
| Stats SA CPI | Stats SA | Headline & category inflation | Monthly | P0141 PDF |

**Intelligence cards:** prime–repo spread, real rate (prime − CPI), CPI vs target band, category inflation pressure.

---

## 7. Health

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| SAMRC | SA Medical Research Council | Excess mortality, wastewater surveillance | Weekly / monthly | [samrc.ac.za](https://www.samrc.ac.za) |
| NICD Surveillance | National Institute for Communicable Diseases | Epidemiological bulletins, outbreak stats | Weekly | [nicd.ac.za](https://www.nicd.ac.za) |
| Healthsites.io | OpenStreetMap community | Clinic & hospital spatial API | Continuous | [healthsites.io](https://healthsites.io) |
| SANAC / UNAIDS | Govt + UN | HIV prevalence, ART coverage | Annual | Public reports |
| NDOH DHIS2 | National Dept of Health | Facility indicators | Quarterly | dhis.gov.za |

**Intelligence cards:** new infections, AIDS deaths, maternal & child mortality, TB treatment success, TB–HIV co-infection.

---

## 8. Education

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| DBE EMIS Master Lists | Dept of Basic Education | Schools, GPS, quintile, pass rates | Annual | [education.gov.za](https://www.education.gov.za) |
| NSC Matric Results | DBE + provinces | School-by-school performance | Annual (January) | DBE releases |
| DHET Statistics | Dept Higher Education | TVET & university enrollments, graduations | Annual | [dhet.gov.za](https://www.dhet.gov.za) |

**Intelligence cards:** candidates passed, distinction rate, maths higher-grade pass, bachelor readiness gap.

---

## 9. Forex

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| SARB Historical Rates | SARB | Official ZAR daily CSV/XML vs majors | Daily | [resbank.co.za statistics](https://www.resbank.co.za) |
| Frankfurter API | ECB-linked open API | Real-time & historical ZAR pairs | Daily | [api.frankfurter.app](https://api.frankfurter.app) |
| Open Exchange Rates | Community | REST FX feeds | Daily | open.er-api.com (used in scraper) |
| Yahoo Finance (`yfinance`) | Market data | USDZAR=X tick scraping target | Real-time | Python package |

**Intelligence cards:** ZAR momentum vs prior month, import cost proxy, regional USD crosses, live feed status.

---

## 10. Water

| Source | Publisher | What we use | Cadence | Access |
|--------|-----------|-------------|---------|--------|
| DWS NIWIS | Dept Water & Sanitation | Dam storage, river flow, catchments | Weekly | [dws.gov.za](https://www.dws.gov.za) |
| OpenUp SA Dam Levels | OpenUp | Cleaned historical dam time-series | Weekly | [openup.org.za](https://openup.org.za) |
| City of Cape Town Open Data | CoCT | Dam levels & consumption metrics | Weekly | [opendata.capetown.gov.za](https://opendata.capetown.gov.za) |

**Intelligence cards:** week-on-week delta, year-on-year storage, total capacity tracked, drought-stress provinces.

---

## Implementation

- Scrapers: `scrapers/` — schedules in `cron_*.sh` and `CRON_SETUP.md`.
- Cache: `data/*.json` synced to `apps/web/data` via `apps/web/scripts/sync-data.mjs`.
- When government sites block cloud IPs, run scrapers on a South African host and commit refreshed JSON.
- Intelligence KPIs are derived in dashboard pages from cached JSON; deeper ingestion (CSV/API) is staged per source above.
