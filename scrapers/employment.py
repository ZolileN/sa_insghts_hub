"""
Employment Scraper — Stats SA QLFS + provincial table parsing
Source : https://www.statssa.gov.za/?page_id=1854&PPN=P0211
         Wazimap / labour.gov.za (context — ward income via future ingest)
"""
import json
import logging
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from scrapers._common import (
    HEADERS,
    extract_pdf_text,
    fetch_statssa_pdf,
    parse_sa_decimal,
    utc_now_iso,
)
from scrapers.sources.qlfs_provinces import parse_provincial_qlfs_table

log = logging.getLogger(__name__)

STATSSA_QLFS = "https://www.statssa.gov.za/?page_id=1854&PPN=P0211"

QLFS_PDF_CANDIDATES = [
    "P02111stQuarter2026.pdf",
    "P0211Media Release QLFS Q1 2026.pdf",
    "P0211June2026.pdf",
]

MEDIAN_INCOME_FALLBACK = {
    "Western Cape": 14800,
    "Gauteng": 11200,
    "KwaZulu-Natal": 9800,
    "Eastern Cape": 6400,
    "Limpopo": 5200,
    "Mpumalanga": 5800,
    "North West": 5400,
    "Free State": 6100,
    "Northern Cape": 8900,
}


def _parse_qlfs_pdf(text: str) -> dict:
    result: dict = {}

    headline = re.search(
        r"unemployment rate to (\d+[\.,]\d+)\s*% in the first quarter of 2026",
        text,
        re.IGNORECASE,
    )
    if headline:
        result["unemployment_rate_pct"] = parse_sa_decimal(headline.group(1))
    else:
        match = re.search(
            r"LU1- Unemployment rate\s+[\d,\.]+[\s\d,\.]+[\s\d,\.]+[\s\d,\.]+[\s\d,\.]+[\s\d,\.]+",
            text,
        )
        if match:
            nums = re.findall(r"\d+[\.,]\d+", match.group(0))
            if len(nums) >= 3:
                result["unemployment_rate_pct"] = parse_sa_decimal(nums[2])

    expanded = re.search(
        r"potential labour force \(LU3\) stood at (\d+[\.,]\d+)\s*% in the first quarter of 2026",
        text,
        re.IGNORECASE,
    )
    if expanded:
        result["expanded_unemployment_pct"] = parse_sa_decimal(expanded.group(1))

    youth = re.search(
        r"labour underutilisation\s+[\d,\.]+[\s\d,\.]+[\s\d,\.]+[\s\d,\.]+[\s\d,\.]+[\s\d,\.]+",
        text,
    )
    if youth:
        nums = re.findall(r"\d+[\.,]\d+", youth.group(0))
        if len(nums) >= 3:
            result["youth_unemployment_pct"] = parse_sa_decimal(nums[2])

    employed = re.search(
        r"decreased by \d+[\s\d,]+ to (\d+[\.,]\d)\s*million",
        text,
        re.IGNORECASE,
    )
    if employed:
        result["employed_millions"] = parse_sa_decimal(employed.group(1))

    provincial = parse_provincial_qlfs_table(text)
    if provincial:
        result["provinces_parsed"] = provincial

    result["period"] = "Q1 2026"
    return result


def _scrape_statssa_qlfs_html() -> dict | None:
    try:
        response = requests.get(STATSSA_QLFS, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "lxml")
        text = soup.get_text()
        result: dict = {}

        match = re.search(
            r"unemployment\s+rate[^\d]*(\d+[\.,]\d+)\s*%",
            text,
            re.IGNORECASE,
        )
        if match:
            result["unemployment_rate_pct"] = parse_sa_decimal(match.group(1))

        youth = re.search(
            r"youth\s+unemployment[^\d]*(\d+[\.,]\d+)\s*%",
            text,
            re.IGNORECASE,
        )
        if youth:
            result["youth_unemployment_pct"] = parse_sa_decimal(youth.group(1))

        return result if result else None
    except Exception as exc:
        log.error("Stats SA QLFS HTML scrape failed: %s", exc)
        return None


def _fetch_qlfs_pdf() -> dict | None:
    for filename in QLFS_PDF_CANDIDATES:
        pdf_bytes = fetch_statssa_pdf("P0211", filename)
        if not pdf_bytes or not pdf_bytes.startswith(b"%PDF"):
            continue
        text = extract_pdf_text(pdf_bytes, max_pages=25)
        if "2026" not in text and "Quarter 1" not in text:
            continue
        parsed = _parse_qlfs_pdf(text)
        if parsed.get("unemployment_rate_pct"):
            parsed["source_pdf"] = filename
            log.info("QLFS parsed from %s", filename)
            return parsed
    return None


def fetch(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    live = _fetch_qlfs_pdf() or _scrape_statssa_qlfs_html()
    is_live = bool(live)
    ingestion: dict[str, bool | str] = {
        "qlfs_pdf": bool(live and live.get("source_pdf")),
        "qlfs_html": bool(live and not live.get("source_pdf")),
        "wazimap": False,
        "labour_gov": False,
    }

    unemployment = (live or {}).get("unemployment_rate_pct", 32.7)
    youth = (live or {}).get("youth_unemployment_pct", 45.8)
    expanded = (live or {}).get("expanded_unemployment_pct", 43.7)
    employed = (live or {}).get("employed_millions", 16.8)
    parsed_provinces = (live or {}).get("provinces_parsed", {})

    youth_ratio = youth / unemployment if unemployment else 1.4

    fallback_provinces = {
        "Western Cape": {"unemployment": 19.6, "expanded_unemployment": 24.8},
        "Eastern Cape": {"unemployment": 44.6, "expanded_unemployment": 54.4},
        "Northern Cape": {"unemployment": 30.4, "expanded_unemployment": 47.0},
        "Free State": {"unemployment": 37.8, "expanded_unemployment": 44.3},
        "KwaZulu-Natal": {"unemployment": 31.2, "expanded_unemployment": 47.2},
        "North West": {"unemployment": 35.3, "expanded_unemployment": 54.8},
        "Gauteng": {"unemployment": 34.1, "expanded_unemployment": 40.6},
        "Mpumalanga": {"unemployment": 36.3, "expanded_unemployment": 49.6},
        "Limpopo": {"unemployment": 31.7, "expanded_unemployment": 47.0},
    }

    merged_provincial: dict[str, dict[str, float]] = {
        name: dict(figures) for name, figures in fallback_provinces.items()
    }
    for name, figures in parsed_provinces.items():
        if name not in merged_provincial:
            merged_provincial[name] = dict(figures)
            continue
        if figures.get("unemployment", 0) > 0:
            merged_provincial[name]["unemployment"] = figures["unemployment"]
        if figures.get("expanded_unemployment", 0) > 0:
            merged_provincial[name]["expanded_unemployment"] = figures[
                "expanded_unemployment"
            ]

    provinces: dict[str, dict] = {}
    for name, figures in merged_provincial.items():
        unemp = figures["unemployment"]
        provinces[name] = {
            "unemployment": unemp,
            "youth_unemployment": round(unemp * youth_ratio, 1),
            "median_income_r": MEDIAN_INCOME_FALLBACK.get(name, 8000),
            "expanded_unemployment": figures["expanded_unemployment"],
        }

    if parsed_provinces:
        ingestion["qlfs_provincial_table"] = True

    result = {
        "source": "Stats SA QLFS Q1 2026 · Wazimap (planned) · labour.gov.za",
        "scraped_at": utc_now_iso(),
        "is_live": is_live,
        "period": (live or {}).get("period", "Q1 2026"),
        "unemployment_rate_pct": unemployment,
        "youth_unemployment_pct": youth,
        "expanded_unemployment_pct": expanded,
        "employed_millions": employed,
        "gini_coefficient": 0.63,
        "national_min_wage_hourly_r": 28.79,
        "provinces": provinces,
        "trend": {
            "Q1-2022": 34.5, "Q2-2022": 33.9, "Q3-2022": 32.9, "Q4-2022": 32.7,
            "Q1-2023": 32.9, "Q2-2023": 33.5, "Q3-2023": 31.9, "Q4-2023": 32.1,
            "Q1-2024": 33.5, "Q2-2024": 33.5, "Q3-2024": 32.9, "Q4-2024": 31.4,
            "Q1-2025": 32.9, "Q1-2026": unemployment,
        },
        "ingestion": ingestion,
        "data_sources": {
            "qlfs": "https://www.statssa.gov.za/?page_id=1854&PPN=P0211",
            "datafirst": "https://www.datafirst.uct.ac.za",
            "wazimap": "https://wazimap.co.za",
            "labour": "https://www.labour.gov.za",
        },
    }

    (output_dir / "employment.json").write_text(json.dumps(result, indent=2))
    log.info(
        "Employment saved | unemployment=%s%% live=%s provinces=%d",
        result["unemployment_rate_pct"],
        is_live,
        len(provinces),
    )
    return result
