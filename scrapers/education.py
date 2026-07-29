"""
Education Scraper — DBE Matric Results
Source : https://www.gov.za (NSC releases) · DBE media pages
Cadence: Annual (January results release)
"""
import logging
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from scrapers._common import (
    HEADERS,
    load_topic_json,
    parse_sa_decimal,
    save_topic_json,
    utc_now_iso,
)

log = logging.getLogger(__name__)

DBE_URL = "https://www.education.gov.za/Informationfor/MediaRelations.aspx"
GOV_ZA_NSC_2025 = (
    "https://www.gov.za/news/speeches/"
    "minister-siviwe-gwarube-release-2025-national-senior-certificate-results-12-jan-2026"
)


def _scrape_dbe() -> dict | None:
    try:
        response = requests.get(DBE_URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "lxml")
        text = soup.get_text()
        result = {}

        match = re.search(r"pass\s+rate[^\d]*(\d+[\.,]\d+)\s*%", text, re.IGNORECASE)
        if match:
            result["national_pass_rate_pct"] = parse_sa_decimal(match.group(1))

        bachelor = re.search(r"bachelor[^\d]*(\d+[\.,]\d+)\s*%", text, re.IGNORECASE)
        if bachelor:
            result["bachelor_pass_pct"] = parse_sa_decimal(bachelor.group(1))

        return result if result else None
    except Exception as exc:
        log.error("DBE scrape failed: %s", exc)
        return None


def _scrape_gov_za_nsc_2025() -> dict | None:
    try:
        response = requests.get(GOV_ZA_NSC_2025, headers=HEADERS, timeout=20)
        if response.status_code != 200:
            return None
        text = response.text
        result: dict = {"exam_year": 2025, "source": "gov.za"}

        national = re.search(r"NSC pass rate is (\d+[\.,]?\d*)\s*%", text, re.IGNORECASE)
        if national:
            result["national_pass_rate_pct"] = parse_sa_decimal(national.group(1))

        bachelor = re.search(
            r"Bachelor passes.*?declined.*?from (\d+[\.,]?\d*)\s*% in 2024 to (\d+[\.,]?\d*)\s*% in 2025",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if bachelor:
            result["bachelor_pass_pct"] = parse_sa_decimal(bachelor.group(2))

        wrote = re.search(r"over (\d[\d,]+)\s+learners passed", text, re.IGNORECASE)
        if wrote:
            result["total_passed"] = int(wrote.group(1).replace(",", ""))

        return result if result.get("national_pass_rate_pct") else None
    except Exception as exc:
        log.error("gov.za NSC scrape failed: %s", exc)
        return None


def fetch(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    cached = load_topic_json(output_dir, "education")

    live = _scrape_dbe() or _scrape_gov_za_nsc_2025()
    if not live and not cached:
        raise RuntimeError("Education: NSC scrape failed and no cached education.json")

    exam_year = (live or {}).get("exam_year") or cached.get("exam_year", 2025)
    pass_rate = (live or {}).get("national_pass_rate_pct") or cached.get("national_pass_rate_pct")
    bachelor = (live or {}).get("bachelor_pass_pct") or cached.get("bachelor_pass_pct")
    total_passed = (live or {}).get("total_passed") or cached.get("total_passed")

    trend = dict(cached.get("trend", {}))
    if pass_rate and bachelor:
        trend[str(exam_year)] = {
            "pass_rate": pass_rate,
            "bachelor": bachelor,
        }

    result = dict(cached)
    result.update({
        "source": "Department of Basic Education — NSC",
        "scraped_at": utc_now_iso(),
        "is_live": bool(live),
        "exam_year": exam_year,
        "national_pass_rate_pct": pass_rate,
        "bachelor_pass_pct": bachelor,
        "total_passed": total_passed,
        "trend": trend,
    })

    save_topic_json(output_dir, "education", result)
    log.info(
        "Education saved | pass_rate=%s%% live=%s",
        result.get("national_pass_rate_pct"),
        bool(live),
    )
    return result
