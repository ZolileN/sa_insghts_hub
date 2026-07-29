"""
SAPS Crime Statistics Scraper
-------------------------------
Source : https://www.saps.gov.za/services/crimestats.php
Data   : Quarterly Excel files published to /services/downloads/
Format : .xlsx  ~10 MB per file
Cadence: Quarterly (Aug, Nov, Feb, May)
"""

import io
import json
import logging
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

from scrapers._common import HEADERS, download_bytes, utc_now_iso

log = logging.getLogger(__name__)

BASE = "https://www.saps.gov.za"
INDEX_URL = f"{BASE}/services/crimestats.php"

PROVINCES = [
    "Western Cape", "Gauteng", "KwaZulu-Natal", "Eastern Cape",
    "Limpopo", "Mpumalanga", "North West", "Free State", "Northern Cape",
]

# SAPS sheet labels → dashboard keys used across the app
CATEGORY_ALIASES = {
    "Murder": "Murder",
    "Sexual offences": "Sexual offences",
    "Attempted murder": "Attempted murder",
    "Assault with the intent to inflict grievous bodily harm": "Assault GBH",
    "Common assault": "Common assault",
    "Common robbery": "Common robbery",
    "Robbery with aggravating circumstances": "Robbery aggravating",
    "Carjacking": "Carjacking",
    "Burglary at residential premises": "Residential burglary",
    "Burglary at non-residential premises": "Non-residential burglary",
    "Stock-theft": "Stock-theft",
    "Malicious damage to property": "Malicious damage to property",
}

SUMMARY_PROVINCE_ORDER = [
    "Eastern Cape", "Free State", "Gauteng", "KwaZulu-Natal",
    "Limpopo", "Mpumalanga", "North West", "Northern Cape", "Western Cape",
]

KNOWN_XLSX_FALLBACKS = [
    "/services/downloads/2025/2025-2026_-_4th_Quarter_WEB.xlsx",
    "/services/downloads/2025/2025-2026_-_3rd_Quarter_WEB.xlsx",
    "/services/downloads/2024-2025_-_3rd_Quarter_WEB.xlsx",
]

# RAW Data sheet category labels → dashboard keys
RAW_CATEGORY_MAP = {
    "Murder": "Murder",
    "Sexual offences": "Sexual offences",
    "Attempted murder": "Attempted murder",
    "Assault with the intent to inflict grievous bodily harm": "Assault GBH",
    "Common assault": "Common assault",
    "Common robbery": "Common robbery",
    "Robbery with aggravating circumstances": "Robbery aggravating",
    "Carjacking": "Carjacking",
    "Burglary at residential premises": "Residential burglary",
    "Burglary at non-residential premises": "Non-residential burglary",
    "Stock-theft": "Stock-theft",
    "Malicious damage to property": "Malicious damage to property",
}

DASHBOARD_CRIME_TYPES = [
    "Murder",
    "Sexual offences",
    "Attempted murder",
    "Assault GBH",
    "Carjacking",
    "Robbery aggravating",
    "Residential burglary",
    "Common robbery",
]

RAW_CURRENT_QUARTER_COL = 27
STATIONS_PER_PROVINCE = 30


def _find_latest_xlsx_url(html: str) -> str | None:
    """Parse the SAPS crime stats page and return the most recent .xlsx link."""
    soup = BeautifulSoup(html, "lxml")
    candidates: list[str] = []

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        lower = href.lower()
        if lower.endswith(".xlsx") and (
            "quarter" in lower or "annual" in lower or "downloads" in lower
        ):
            candidates.append(href)

    if not candidates:
        candidates = KNOWN_XLSX_FALLBACKS.copy()

    def sort_key(href: str) -> tuple[int, int, int]:
        match = re.search(r"(\d{4})-(\d{4}).*?(\d)(?:st|nd|rd|th)", href, re.IGNORECASE)
        if match:
            return (int(match.group(1)), int(match.group(3)), len(href))
        year_match = re.search(r"(\d{4})-(\d{4})", href)
        if year_match:
            return (int(year_match.group(1)), 0, len(href))
        return (0, 0, 0)

    candidates.sort(key=sort_key, reverse=True)
    href = candidates[0]
    if href.startswith("http"):
        return href
    if not href.startswith("/"):
        if href.startswith("downloads/"):
            href = "/services/" + href
        else:
            href = "/" + href
    return BASE + href


def _download_xlsx(url: str) -> bytes | None:
    log.info("Downloading SAPS Excel: %s", url)
    # SAPS cert chain often fails outside SA; stream large files with retries
    return download_bytes(url, timeout=180, verify=False, retries=4)


def _parse_summary_sheet(raw_bytes: bytes) -> dict:
    """
    Parse the modern SAPS workbook layout (2025+).
    Uses 'Crime stats RSA & PHO summary' with province columns 8–16.
    """
    xls = pd.ExcelFile(io.BytesIO(raw_bytes))
    sheet = "Crime stats RSA & PHO summary"
    if sheet not in xls.sheet_names:
        log.warning("Summary sheet missing; falling back to legacy parser")
        return _parse_legacy_sheets(xls)

    df = pd.read_excel(xls, sheet_name=sheet, header=None)
    result = {province: {} for province in PROVINCES}

    for _, row in df.iterrows():
        raw_label = str(row.iloc[2]).strip()
        if raw_label not in CATEGORY_ALIASES:
            continue

        key = CATEGORY_ALIASES[raw_label]
        try:
            national = int(float(row.iloc[4]))
        except (TypeError, ValueError):
            continue

        for idx, province in enumerate(SUMMARY_PROVINCE_ORDER):
            col = 8 + idx
            if col >= len(row):
                continue
            value = row.iloc[col]
            if pd.isna(value):
                continue
            try:
                result[province][key] = int(float(value))
            except (TypeError, ValueError):
                continue

        # Sanity check: national total should be positive
        if national <= 0:
            continue

    populated = sum(1 for p in result.values() if p)
    log.info("Parsed SAPS summary sheet for %s provinces with data", populated)
    return result


def _parse_legacy_sheets(xls: pd.ExcelFile) -> dict:
    """Original per-category sheet parser for older SAPS workbooks."""
    legacy_categories = list(CATEGORY_ALIASES.keys())
    result = {province: {} for province in PROVINCES}

    for sheet in xls.sheet_names:
        cat = sheet.strip()
        if cat not in legacy_categories:
            continue
        key = CATEGORY_ALIASES.get(cat, cat)
        try:
            df = pd.read_excel(xls, sheet_name=sheet, header=None)
            for _, row in df.iterrows():
                cell = str(row.iloc[0]).strip()
                for prov in PROVINCES:
                    if prov.lower() in cell.lower():
                        nums = [
                            v for v in row
                            if isinstance(v, (int, float)) and not pd.isna(v)
                        ]
                        if nums:
                            result[prov][key] = int(nums[-1])
                        break
        except Exception as exc:
            log.warning("Skipping legacy sheet '%s': %s", sheet, exc)

    return result


def _parse_province_totals(raw_bytes: bytes) -> dict:
    return _parse_summary_sheet(raw_bytes)


def _district_label(raw: str) -> str:
    """Turn SAPS district names into city/metro labels for drill-down."""
    label = str(raw).strip()
    for suffix in (" District", " Metropolitan Municipality"):
        if label.endswith(suffix):
            label = label[:-len(suffix)]
    return label.strip() or "Unknown"


def _parse_station_drilldown(xls: pd.ExcelFile) -> dict:
    """
    Parse SAPS RAW Data for station and district (city/metro) breakdown.
    Uses the latest quarter column (Jan–Mar 2026 in current workbook).
    """
    if "RAW Data" not in xls.sheet_names:
        return {"stations": {}, "districts": {}, "national_hotspots": []}

    df = pd.read_excel(xls, sheet_name="RAW Data", header=None, skiprows=3)
    stations_by_province: dict[str, list[dict]] = {p: [] for p in PROVINCES}
    districts_by_province: dict[str, dict[str, dict[str, int]]] = {
        p: {} for p in PROVINCES
    }
    station_index: dict[tuple[str, str, str], dict[str, int]] = {}

    for _, row in df.iterrows():
        province = str(row.iloc[6]).strip()
        if province not in PROVINCES:
            continue

        raw_cat = str(row.iloc[7]).strip()
        key = RAW_CATEGORY_MAP.get(raw_cat)
        if not key:
            continue

        try:
            count = int(float(row.iloc[RAW_CURRENT_QUARTER_COL]))
        except (TypeError, ValueError):
            continue

        station = str(row.iloc[4]).strip()
        district_raw = str(row.iloc[5]).strip()
        district = _district_label(district_raw)
        if not station or station == "Station":
            continue

        station_key = (province, district, station)
        if station_key not in station_index:
            station_index[station_key] = {}
        station_index[station_key][key] = count

        district_bucket = districts_by_province[province].setdefault(district, {})
        district_bucket[key] = district_bucket.get(key, 0) + count

    for (province, district, station), crimes in station_index.items():
        stations_by_province[province].append({
            "name": station,
            "district": district,
            "crimes": crimes,
            "murders": crimes.get("Murder", 0),
        })

    for province in PROVINCES:
        stations_by_province[province].sort(
            key=lambda s: s.get("murders", 0),
            reverse=True,
        )
        stations_by_province[province] = stations_by_province[province][:STATIONS_PER_PROVINCE]

    national_hotspots = _parse_national_hotspots(xls)

    log.info(
        "Parsed station drill-down: %s provinces, %s national hotspots",
        sum(1 for p in stations_by_province if stations_by_province[p]),
        len(national_hotspots),
    )

    return {
        "stations": stations_by_province,
        "districts": districts_by_province,
        "national_hotspots": national_hotspots,
    }


def _parse_national_hotspots(xls: pd.ExcelFile) -> list[dict]:
    """Top 30 police precincts by community-reported serious crime (SAPS TOP30 sheet)."""
    sheet = "TOP30 stations"
    if sheet not in xls.sheet_names:
        return []

    df = pd.read_excel(xls, sheet_name=sheet, header=None)
    hotspots: list[dict] = []

    for _, row in df.iterrows():
        try:
            rank = int(float(row.iloc[3]))
        except (TypeError, ValueError):
            continue
        if rank < 1 or rank > 30:
            continue

        station = str(row.iloc[5]).strip()
        district_raw = str(row.iloc[6]).strip()
        province = str(row.iloc[7]).strip()
        if province not in PROVINCES:
            continue
        if not station or station == "Station":
            continue

        try:
            serious_crime = int(float(row.iloc[11]))
        except (TypeError, ValueError):
            serious_crime = 0

        hotspots.append({
            "rank": rank,
            "station": station,
            "district": _district_label(district_raw),
            "province": province,
            "serious_crime": serious_crime,
        })

    hotspots.sort(key=lambda h: h["rank"])
    return hotspots


def _parse_workbook(raw_bytes: bytes) -> tuple[dict, dict, bool]:
    """Parse province totals and station drill-down from one SAPS workbook."""
    xls = pd.ExcelFile(io.BytesIO(raw_bytes))
    province_data = _parse_summary_sheet(raw_bytes)
    drilldown = _parse_station_drilldown(xls)
    is_live = any(province_data.values())
    return province_data, drilldown, is_live


def fetch(output_dir: Path) -> dict:
    """Download and parse SAPS crime data; save JSON to output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)

    xlsx_url: str | None = None
    try:
        response = requests.get(INDEX_URL, headers=HEADERS, timeout=20, verify=False)
        xlsx_url = _find_latest_xlsx_url(response.text)
    except Exception as exc:
        log.error("SAPS index fetch failed: %s", exc)

    if not xlsx_url:
        xlsx_url = BASE + KNOWN_XLSX_FALLBACKS[0]

    log.info("Latest SAPS xlsx URL: %s", xlsx_url)

    raw = _download_xlsx(xlsx_url)
    is_live = False
    province_data: dict

    if raw:
        province_data, drilldown, parsed_live = _parse_workbook(raw)
        is_live = parsed_live
        if not is_live:
            log.warning("SAPS download succeeded but parsing returned no rows")
            province_data = _fallback_data()
            drilldown = {"stations": {}, "districts": {}, "national_hotspots": []}
    else:
        log.warning("Using cached/fallback crime data")
        province_data = _fallback_data()
        drilldown = {"stations": {}, "districts": {}, "national_hotspots": []}

    result = {
        "source": "SAPS",
        "url": xlsx_url,
        "scraped_at": utc_now_iso(),
        "is_live": is_live,
        "period": _extract_period(xlsx_url),
        "provinces": province_data,
        "national_totals": _national_totals(province_data),
        "crime_types": DASHBOARD_CRIME_TYPES,
        "stations": drilldown.get("stations", {}),
        "districts": drilldown.get("districts", {}),
        "national_hotspots": drilldown.get("national_hotspots", []),
    }

    out = output_dir / "crime.json"
    out.write_text(json.dumps(result, indent=2))
    log.info("Crime data saved → %s (live=%s)", out, is_live)
    return result


def _extract_period(url: str) -> str:
    match = re.search(r"(\d{4}-\d{4}.*?)(?:_WEB)?\.xlsx", url, re.IGNORECASE)
    if match:
        return match.group(1).replace("_", " ")
    quarter = re.search(r"(\d)(?:st|nd|rd|th)_Quarter", url, re.IGNORECASE)
    year_span = re.search(r"(\d{4}-\d{4})", url)
    if quarter and year_span:
        return f"{year_span.group(1)} Q{quarter.group(1)}"
    return "Unknown"


def _national_totals(provinces: dict) -> dict:
    totals: dict[str, int] = {}
    for prov_data in provinces.values():
        for cat, val in prov_data.items():
            totals[cat] = totals.get(cat, 0) + val
    return totals


def _fallback_data() -> dict:
    """Q4 2025/26 (Jan–Mar 2026) figures from published SAPS workbook."""
    return {
        "Gauteng": {
            "Murder": 1223, "Carjacking": 2062, "Residential burglary": 6499,
            "Sexual offences": 2369, "Robbery aggravating": 8625,
        },
        "KwaZulu-Natal": {
            "Murder": 1058, "Carjacking": 446, "Residential burglary": 5986,
            "Sexual offences": 2589, "Robbery aggravating": 8013,
        },
        "Western Cape": {
            "Murder": 983, "Carjacking": 498, "Residential burglary": 4909,
            "Sexual offences": 1663, "Robbery aggravating": 5994,
        },
        "Eastern Cape": {
            "Murder": 949, "Carjacking": 189, "Residential burglary": 3724,
            "Sexual offences": 1853, "Robbery aggravating": 6026,
        },
        "Limpopo": {
            "Murder": 175, "Carjacking": 58, "Residential burglary": 2620,
            "Sexual offences": 1185, "Robbery aggravating": 2823,
        },
        "Mpumalanga": {
            "Murder": 253, "Carjacking": 212, "Residential burglary": 2260,
            "Sexual offences": 900, "Robbery aggravating": 2850,
        },
        "North West": {
            "Murder": 271, "Carjacking": 106, "Residential burglary": 2633,
            "Sexual offences": 887, "Robbery aggravating": 4048,
        },
        "Free State": {
            "Murder": 192, "Carjacking": 32, "Residential burglary": 2408,
            "Sexual offences": 837, "Robbery aggravating": 3203,
        },
        "Northern Cape": {
            "Murder": 77, "Carjacking": 6, "Residential burglary": 1348,
            "Sexual offences": 307, "Robbery aggravating": 1994,
        },
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = fetch(Path("data"))
    print(json.dumps(data["national_totals"], indent=2))
