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
    parse_sa_decimal,
    utc_now_iso,
)

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

    existing_path = output_dir / "finance.json"
    existing: dict = {}
    if existing_path.exists():
        try:
            existing = json.loads(existing_path.read_text())
        except json.JSONDecodeError:
            existing = {}

    sarb = _fetch_sarb_repo_rate()
    cpi = _fetch_statssa_cpi_pdf() or _fetch_statssa_cpi_html()

    repo_rate = sarb.get("repo_rate_pct") if sarb else None
    prime_rate = round(repo_rate + 3.5, 2) if repo_rate else None

    result = {
        "source": "SARB + Stats SA",
        "scraped_at": utc_now_iso(),
        "is_live": bool(repo_rate or cpi),
        "repo_rate_pct": repo_rate or 7.0,
        "prime_rate_pct": prime_rate or 10.5,
        "cpi_headline_pct": (cpi or {}).get("headline_cpi_pct", 5.0),
        "cpi_period": (cpi or {}).get("period", "June 2026"),
        "sarb_raw": sarb,
        "cpi_raw": cpi,
        "repo_history": {
            "2020-Q1": 6.25, "2020-Q2": 3.75, "2020-Q3": 3.5,  "2020-Q4": 3.5,
            "2021-Q1": 3.5,  "2021-Q2": 3.5,  "2021-Q3": 3.5,  "2021-Q4": 3.75,
            "2022-Q1": 4.0,  "2022-Q2": 4.75, "2022-Q3": 5.5,  "2022-Q4": 7.0,
            "2023-Q1": 7.25, "2023-Q2": 8.25, "2023-Q3": 8.25, "2023-Q4": 8.25,
            "2024-Q1": 8.25, "2024-Q2": 8.25, "2024-Q3": 8.0,  "2024-Q4": 7.75,
            "2025-Q1": 7.5,  "2025-Q2": 7.25, "2025-Q3": 7.0,  "2025-Q4": 6.75,
            "2026-Q1": 6.75, "2026-Q2": 7.0,  "2026-Q3": 7.0,
        },
        "cpi_history": existing.get(
            "cpi_history",
            {
                "2023-01": 6.9, "2023-04": 6.8, "2023-07": 4.7, "2023-10": 5.5,
                "2024-01": 5.3, "2024-04": 5.3, "2024-07": 4.6, "2024-10": 2.9,
                "2025-01": 3.5, "2025-04": 3.3, "2025-07": 3.4, "2025-10": 3.6,
                "2026-01": 3.5, "2026-04": 4.5, "2026-06": 5.0,
            },
        ),
        "cpi_basket": existing.get(
            "cpi_basket",
            {
                "Food & non-alcoholic beverages": 6.8,
                "Housing & utilities": 4.2,
                "Transport": 3.1,
                "Medical care": 5.4,
                "Education": 4.8,
                "Miscellaneous": 3.9,
            },
        ),
        "ingestion": {
            "sarb_mpc": bool(sarb),
            "stats_sa_cpi": bool(cpi),
            "vulekamali": False,
            "etenders": False,
        },
        "data_sources": {
            "sarb": "https://www.resbank.co.za",
            "stats_sa_cpi": "https://www.statssa.gov.za/?page_id=1854&PPN=P0141",
            "vulekamali": "https://vulekamali.gov.za",
            "etenders": "https://www.etenders.gov.za",
        },
    }

    if cpi and result["cpi_period"]:
        period_key = result["cpi_period"].replace(" ", "-").lower()
        if "june" in period_key or "2026" in period_key:
            result["cpi_history"]["2026-06"] = result["cpi_headline_pct"]

    out = output_dir / "finance.json"
    out.write_text(json.dumps(result, indent=2))
    log.info(
        "Finance data saved → %s | repo=%s%% CPI=%s%%",
        out,
        result["repo_rate_pct"],
        result["cpi_headline_pct"],
    )
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = fetch(Path("data"))
    print(f"Repo rate : {data['repo_rate_pct']}%")
    print(f"Prime rate: {data['prime_rate_pct']}%")
    print(f"CPI       : {data['cpi_headline_pct']}%")
    print(f"Live      : {data['is_live']}")
