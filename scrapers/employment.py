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
    load_topic_json,
    parse_sa_decimal,
    save_topic_json,
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
    cached = load_topic_json(output_dir, "employment")

    live = _fetch_qlfs_pdf() or _scrape_statssa_qlfs_html()
    is_live = bool(live)
    ingestion: dict[str, bool | str] = {
        "qlfs_pdf": bool(live and live.get("source_pdf")),
        "qlfs_html": bool(live and not live.get("source_pdf")),
        "wazimap": False,
        "labour_gov": False,
    }

    unemployment = (live or {}).get("unemployment_rate_pct") or cached.get("unemployment_rate_pct")
    youth = (live or {}).get("youth_unemployment_pct") or cached.get("youth_unemployment_pct")
    expanded = (live or {}).get("expanded_unemployment_pct") or cached.get("expanded_unemployment_pct")
    employed = (live or {}).get("employed_millions") or cached.get("employed_millions")
    parsed_provinces = (live or {}).get("provinces_parsed", {})

    if not unemployment and not cached:
        raise RuntimeError("Employment: QLFS scrape failed and no cached employment.json")

    youth_ratio = (
        youth / unemployment
        if unemployment and youth
        else (
            cached.get("youth_unemployment_pct") / cached.get("unemployment_rate_pct")
            if cached.get("youth_unemployment_pct") and cached.get("unemployment_rate_pct")
            else None
        )
    )

    provinces: dict[str, dict] = dict(cached.get("provinces", {}))
    for name, figures in parsed_provinces.items():
        unemp = figures.get("unemployment", 0)
        if unemp <= 0:
            continue
        entry = provinces.get(name, {})
        entry["unemployment"] = unemp
        if youth_ratio is not None:
            entry["youth_unemployment"] = round(unemp * youth_ratio, 1)
        if figures.get("expanded_unemployment"):
            entry["expanded_unemployment"] = figures["expanded_unemployment"]
        provinces[name] = entry

    if parsed_provinces:
        ingestion["qlfs_provincial_table"] = True

    period = (live or {}).get("period") or cached.get("period")
    trend = dict(cached.get("trend", {}))
    if live and unemployment:
        trend[period.replace(" ", "-")] = unemployment

    result = dict(cached)
    result.update({
        "source": "Stats SA QLFS · Wazimap (planned) · labour.gov.za",
        "scraped_at": utc_now_iso(),
        "is_live": is_live,
        "period": period,
        "unemployment_rate_pct": unemployment,
        "youth_unemployment_pct": youth,
        "expanded_unemployment_pct": expanded,
        "employed_millions": employed,
        "provinces": provinces,
        "trend": trend,
        "ingestion": ingestion,
        "data_sources": cached.get(
            "data_sources",
            {
                "qlfs": "https://www.statssa.gov.za/?page_id=1854&PPN=P0211",
                "datafirst": "https://www.datafirst.uct.ac.za",
                "wazimap": "https://wazimap.co.za",
                "labour": "https://www.labour.gov.za",
            },
        ),
    })

    save_topic_json(output_dir, "employment", result)
    log.info(
        "Employment saved | unemployment=%s%% live=%s provinces=%d",
        result["unemployment_rate_pct"],
        is_live,
        len(provinces),
    )
    return result
