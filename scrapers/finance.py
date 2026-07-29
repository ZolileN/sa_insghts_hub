"""
Finance Scraper — SARB Repo Rate + Stats SA CPI
-------------------------------------------------
Source 1 : SARB MPC statements (HTML/PDF)
Source 2 : Stats SA CPI releases (P0141 PDF)
Cadence  : SARB MPC ~6x/year · Stats SA CPI monthly
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
    find_first_percent,
    load_topic_json,
    parse_sa_decimal,
    save_topic_json,
    utc_now_iso,
)
from scrapers.sources.vulekamali import fetch_budget_summary

log = logging.getLogger(__name__)

SARB_MPC_URL = "https://www.resbank.co.za/en/home/what-we-do/monetary-policy"
SARB_MPC_PDF = (
    "https://www.resbank.co.za/content/dam/sarb/publications/statements/"
    "monetary-policy-statements/2026/july/july-statement.pdf"
)
STATSSA_CPI = "https://www.statssa.gov.za/?page_id=1854&PPN=P0141"

CPI_PDF_CANDIDATES = [
    "P0141June2026.pdf",
    "P0141July2026.pdf",
    "P0141May2026.pdf",
]


def _fetch_sarb_repo_rate() -> dict | None:
    """Resolve current repo rate from SARB MPC PDF or monetary policy pages."""
    pdf_bytes = requests.get(SARB_MPC_PDF, headers=HEADERS, timeout=30).content
    if pdf_bytes.startswith(b"%PDF"):
        text = extract_pdf_text(pdf_bytes, max_pages=5)
        match = re.search(
            r"policy rate unchanged,\s*at\s*(\d+(?:[\.,]\d+)?)\s*%",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if match:
            rate = parse_sa_decimal(match.group(1))
            log.info("Repo rate from SARB July 2026 MPC PDF: %s%%", rate)
            return {"repo_rate_pct": rate, "source": "SARB MPC July 2026"}

    pages = [
        SARB_MPC_URL,
        "https://www.resbank.co.za/en/home/what-we-do/monetary-policy/key-repo-rate",
    ]
    for url in pages:
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(response.text, "lxml")
            text = soup.get_text()
            match = re.search(
                r"repo rate[^\d]*(\d+[\.,]\d+)\s*(?:%|per cent)",
                text,
                re.IGNORECASE,
            )
            if match:
                rate = parse_sa_decimal(match.group(1))
                log.info("Repo rate scraped from HTML %s: %s%%", url, rate)
                return {"repo_rate_pct": rate, "source": f"SARB HTML ({url})"}
        except Exception as exc:
            log.debug("SARB HTML scrape %s failed: %s", url, exc)

    return None


def _fetch_statssa_cpi_pdf() -> dict | None:
    for filename in CPI_PDF_CANDIDATES:
        pdf_bytes = fetch_statssa_pdf("P0141", filename)
        if not pdf_bytes or not pdf_bytes.startswith(b"%PDF"):
            continue
        text = extract_pdf_text(pdf_bytes, max_pages=8)
        match = re.search(
            r"Annual consumer price inflation was (\d+[\.,]\d+)\s*%",
            text,
            re.IGNORECASE,
        )
        if match:
            cpi = parse_sa_decimal(match.group(1))
            period_match = re.search(r"Consumer Price Index,\s*(\w+\s+\d{4})", text)
            period = period_match.group(1) if period_match else "2026"
            log.info("CPI %s%% from %s", cpi, filename)
            return {
                "headline_cpi_pct": cpi,
                "period": period,
                "source": f"Stats SA {filename}",
            }
    return None


def _fetch_statssa_cpi_html() -> dict | None:
    try:
        response = requests.get(STATSSA_CPI, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "lxml")
        text = soup.get_text()
        cpi = find_first_percent(
            text,
            r"(?:headline|overall|annual)[^\d%]*(\d+[\.,]\d+)\s*%",
        )
        if cpi:
            return {"headline_cpi_pct": cpi, "source": "Stats SA HTML"}
    except Exception as exc:
        log.error("Stats SA CPI HTML scrape failed: %s", exc)
    return None


def fetch(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    cached = load_topic_json(output_dir, "finance")

    sarb = _fetch_sarb_repo_rate()
    cpi = _fetch_statssa_cpi_pdf() or _fetch_statssa_cpi_html()

    repo_rate = sarb.get("repo_rate_pct") if sarb else cached.get("repo_rate_pct")
    prime_rate = round(repo_rate + 3.5, 2) if repo_rate else cached.get("prime_rate_pct")
    cpi_headline = (cpi or {}).get("headline_cpi_pct") or cached.get("cpi_headline_pct")
    cpi_period = (cpi or {}).get("period") or cached.get("cpi_period")

    if not repo_rate and not cpi_headline and not cached:
        raise RuntimeError("Finance: SARB/CPI scrape failed and no cached finance.json")

    result = dict(cached)
    result.update({
        "source": "SARB + Stats SA",
        "scraped_at": utc_now_iso(),
        "is_live": bool(sarb or cpi),
        "repo_rate_pct": repo_rate,
        "prime_rate_pct": prime_rate,
        "cpi_headline_pct": cpi_headline,
        "cpi_period": cpi_period,
        "sarb_raw": sarb,
        "cpi_raw": cpi,
        "ingestion": {
            "sarb_mpc": bool(sarb),
            "stats_sa_cpi": bool(cpi),
            "vulekamali": cached.get("ingestion", {}).get("vulekamali", False),
            "etenders": cached.get("ingestion", {}).get("etenders", False),
        },
        "data_sources": cached.get(
            "data_sources",
            {
                "sarb": "https://www.resbank.co.za",
                "stats_sa_cpi": "https://www.statssa.gov.za/?page_id=1854&PPN=P0141",
                "vulekamali": "https://vulekamali.gov.za",
                "etenders": "https://www.etenders.gov.za",
            },
        ),
    })

    if cpi and result.get("cpi_period") and cpi_headline is not None:
        period_key = result["cpi_period"].replace(" ", "-").lower()
        history = dict(result.get("cpi_history", {}))
        history[period_key] = cpi_headline
        result["cpi_history"] = history

    if sarb and repo_rate is not None:
        from datetime import datetime

        now = datetime.now()
        history = dict(result.get("repo_history", {}))
        history_key = f"{now.year}-Q{(now.month - 1) // 3 + 1}"
        history[history_key] = repo_rate
        result["repo_history"] = history

    budget_live = fetch_budget_summary()
    if budget_live:
        result["budget"] = budget_live
        result["ingestion"]["vulekamali"] = True
        result["is_live"] = True

    save_topic_json(output_dir, "finance", result)
    log.info(
        "Finance data saved → finance.json | repo=%s%% CPI=%s%%",
        result.get("repo_rate_pct"),
        result.get("cpi_headline_pct"),
    )
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = fetch(Path("data"))
    print(f"Repo rate : {data['repo_rate_pct']}%")
    print(f"Prime rate: {data['prime_rate_pct']}%")
    print(f"CPI       : {data['cpi_headline_pct']}%")
    print(f"Live      : {data['is_live']}")
