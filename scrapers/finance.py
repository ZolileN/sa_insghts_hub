"""
Finance Scraper — SARB Repo Rate + Stats SA CPI
-------------------------------------------------
Source 1 : https://custom.resbank.co.za/SarbWebApi/  (SARB public Web API)
Source 2 : https://www.statssa.gov.za/               (Stats SA CPI releases)
Source 3 : https://www.resbank.co.za (HTML fallback)
Cadence  : SARB MPC meets 6x/year · Stats SA CPI monthly
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (SA-Insight-Hub/1.0; public-data-research)"}

SARB_API_BASE  = "https://custom.resbank.co.za/SarbWebApi"
SARB_MPC_URL   = "https://www.resbank.co.za/en/home/what-we-do/monetary-policy"
STATSSA_CPI    = "https://www.statssa.gov.za/?page_id=1854&PPN=P0141"


def _fetch_sarb_repo_rate() -> dict | None:
    """Try the SARB Web API for current repo rate series."""
    endpoints = [
        f"{SARB_API_BASE}/WebIndicators/CurrentGroupData/Rates",
        f"{SARB_API_BASE}/WebIndicators/CurrentGroupData/MonetaryPolicy",
        f"{SARB_API_BASE}/Home/Overview",
    ]
    for url in endpoints:
        try:
            r = requests.get(url, headers={**HEADERS, "Accept": "application/json"}, timeout=10)
            if r.status_code == 200 and r.headers.get("content-type", "").startswith("application/json"):
                data = r.json()
                log.info(f"SARB API OK at {url}")
                return data
        except Exception as e:
            log.debug(f"SARB endpoint {url} failed: {e}")

    # HTML scrape fallback: SARB monetary policy page
    try:
        r = requests.get(SARB_MPC_URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")
        text = soup.get_text()
        # Look for repo rate mentions like "repo rate of 7.75%" or "8.00 per cent"
        m = re.search(r"repo rate[^\d]*(\d+[\.,]\d+)\s*(?:%|per cent)", text, re.IGNORECASE)
        if m:
            rate = float(m.group(1).replace(",", "."))
            log.info(f"Repo rate scraped from HTML: {rate}%")
            return {"repo_rate_pct": rate, "source": "SARB HTML scrape"}
    except Exception as e:
        log.error(f"SARB HTML scrape failed: {e}")

    return None


def _fetch_statssa_cpi() -> dict | None:
    """Scrape Stats SA for latest CPI headline figure."""
    try:
        r = requests.get(STATSSA_CPI, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")
        text = soup.get_text()

        # Look for patterns like "4.4%" or "Consumer price index: 4.4%"
        m = re.search(
            r"(?:headline|overall|annual)[^\d%]*(\d+[\.,]\d+)\s*%",
            text, re.IGNORECASE
        )
        if m:
            cpi = float(m.group(1).replace(",", "."))
            log.info(f"CPI scraped: {cpi}%")
            return {"headline_cpi_pct": cpi, "source": "Stats SA"}

        # Broader search
        m2 = re.search(r"(\d+[\.,]\d+)\s*(?:per cent|%)", text)
        if m2:
            return {"headline_cpi_pct": float(m2.group(1).replace(",", ".")),
                    "source": "Stats SA (broad match)"}
    except Exception as e:
        log.error(f"Stats SA CPI scrape failed: {e}")
    return None


def _fetch_tradingeconomics_rates() -> dict | None:
    """
    TradingEconomics hosts SA interest rate and CPI data.
    We use their public embed endpoints (no key required for basic reads).
    """
    url = "https://tradingeconomics.com/south-africa/interest-rate"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")

        result = {}

        # Scrape the large rate display
        for span in soup.find_all(["span", "div", "td"], class_=re.compile(r"value|rate|number", re.I)):
            txt = span.get_text(strip=True)
            m = re.match(r"^(\d+[\.,]\d+)\s*%?$", txt)
            if m:
                val = float(m.group(1).replace(",", "."))
                if 3 < val < 25:   # plausible interest rate range
                    result.setdefault("repo_candidate", val)
                break

        return result if result else None
    except Exception as e:
        log.debug(f"TradingEconomics scrape: {e}")
        return None


def fetch(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    sarb = _fetch_sarb_repo_rate()
    cpi  = _fetch_statssa_cpi()
    te   = _fetch_tradingeconomics_rates()

    # Best-effort repo rate
    repo_rate = None
    prime_rate = None
    if sarb and isinstance(sarb, dict):
        repo_rate = sarb.get("repo_rate_pct") or sarb.get("repo_candidate")
    if te and not repo_rate:
        repo_rate = te.get("repo_candidate")
    if repo_rate:
        prime_rate = round(repo_rate + 3.5, 2)

    result = {
        "source": "SARB + Stats SA",
        "scraped_at": datetime.utcnow().isoformat(),
        "is_live": bool(repo_rate or cpi),
        "repo_rate_pct": repo_rate or 6.75,          # fallback: Nov 2025 actual
        "prime_rate_pct": prime_rate or 10.25,
        "cpi_headline_pct": (cpi or {}).get("headline_cpi_pct", 3.5),
        "sarb_raw": sarb,
        "cpi_raw": cpi,
        # Historical series (hardcoded from SARB published data — update quarterly)
        "repo_history": {
            "2020-Q1": 6.25, "2020-Q2": 3.75, "2020-Q3": 3.5,  "2020-Q4": 3.5,
            "2021-Q1": 3.5,  "2021-Q2": 3.5,  "2021-Q3": 3.5,  "2021-Q4": 3.75,
            "2022-Q1": 4.0,  "2022-Q2": 4.75, "2022-Q3": 5.5,  "2022-Q4": 7.0,
            "2023-Q1": 7.25, "2023-Q2": 8.25, "2023-Q3": 8.25, "2023-Q4": 8.25,
            "2024-Q1": 8.25, "2024-Q2": 8.25, "2024-Q3": 8.0,  "2024-Q4": 7.75,
            "2025-Q1": 7.5,  "2025-Q2": 7.25, "2025-Q3": 7.0,  "2025-Q4": 6.75,
        },
        "cpi_history": {
            "2023-01": 6.9, "2023-04": 6.8, "2023-07": 4.7, "2023-10": 5.5,
            "2024-01": 5.3, "2024-04": 5.3, "2024-07": 4.6, "2024-10": 2.9,
            "2025-01": 3.5, "2025-04": 3.3, "2025-07": 3.4, "2025-10": 3.6,
            "2026-01": 3.5,
        },
    }

    out = output_dir / "finance.json"
    out.write_text(json.dumps(result, indent=2))
    log.info(f"Finance data saved → {out}  |  repo={result['repo_rate_pct']}%  CPI={result['cpi_headline_pct']}%")
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = fetch(Path("data"))
    print(f"Repo rate : {data['repo_rate_pct']}%")
    print(f"Prime rate: {data['prime_rate_pct']}%")
    print(f"CPI       : {data['cpi_headline_pct']}%")
    print(f"Live      : {data['is_live']}")
