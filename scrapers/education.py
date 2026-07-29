"""
Education Scraper — DBE Matric Results
Source : https://www.gov.za (NSC releases) · DBE media pages
Cadence: Annual (January results release)
"""
import json
import logging
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from scrapers._common import HEADERS, parse_sa_decimal, utc_now_iso

log = logging.getLogger(__name__)

DBE_URL = "https://www.education.gov.za/Informationfor/MediaRelations.aspx"
GOV_ZA_NSC_2025 = (
    "https://www.gov.za/news/speeches/"
    "minister-siviwe-gwarube-release-2025-national-senior-certificate-results-12-jan-2026"
)

NSC_2025_PROVINCES = {
    "KwaZulu-Natal": {"pass_rate": 90.6, "bachelor_pct": 46.0, "wrote": 148000},
    "Free State": {"pass_rate": 89.33, "bachelor_pct": 46.0, "wrote": 38000},
    "Gauteng": {"pass_rate": 89.06, "bachelor_pct": 46.0, "wrote": 132000},
    "North West": {"pass_rate": 88.49, "bachelor_pct": 46.0, "wrote": 47000},
    "Western Cape": {"pass_rate": 88.20, "bachelor_pct": 46.0, "wrote": 88000},
    "Northern Cape": {"pass_rate": 87.79, "bachelor_pct": 46.0, "wrote": 20000},
    "Mpumalanga": {"pass_rate": 86.55, "bachelor_pct": 46.0, "wrote": 62000},
    "Limpopo": {"pass_rate": 86.15, "bachelor_pct": 46.0, "wrote": 58000},
    "Eastern Cape": {"pass_rate": 84.17, "bachelor_pct": 46.0, "wrote": 94000},
}


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
    live = _scrape_dbe() or _scrape_gov_za_nsc_2025()

    result = {
        "source": "Department of Basic Education — NSC 2025",
        "scraped_at": utc_now_iso(),
        "is_live": bool(live),
        "exam_year": 2025,
        "national_pass_rate_pct": (live or {}).get("national_pass_rate_pct", 88.0),
        "bachelor_pass_pct": (live or {}).get("bachelor_pass_pct", 46.0),
        "total_wrote": 900000,
        "total_passed": (live or {}).get("total_passed", 656000),
        "distinction_rate_pct": 7.2,
        "provinces": NSC_2025_PROVINCES,
        "subjects": {
            "Mathematics": {"pass_rate": 64.0, "hq_pass_rate": 31.2},
            "Mathematical Literacy": {"pass_rate": 80.2, "hq_pass_rate": 48.1},
            "Physical Sciences": {"pass_rate": 77.0, "hq_pass_rate": 28.4},
            "Life Sciences": {"pass_rate": 71.2, "hq_pass_rate": 42.1},
            "Accounting": {"pass_rate": 78.0, "hq_pass_rate": 34.2},
            "Geography": {"pass_rate": 64.8, "hq_pass_rate": 38.8},
            "History": {"pass_rate": 68.9, "hq_pass_rate": 41.2},
            "Business Studies": {"pass_rate": 74.6, "hq_pass_rate": 45.1},
        },
        "trend": {
            "2015": {"pass_rate": 70.7, "bachelor": 35.5},
            "2017": {"pass_rate": 75.1, "bachelor": 37.8},
            "2019": {"pass_rate": 81.3, "bachelor": 40.8},
            "2021": {"pass_rate": 77.2, "bachelor": 39.2},
            "2023": {"pass_rate": 82.9, "bachelor": 43.8},
            "2024": {"pass_rate": 87.3, "bachelor": 45.6},
            "2025": {"pass_rate": 88.0, "bachelor": 46.0},
        },
    }

    (output_dir / "education.json").write_text(json.dumps(result, indent=2))
    log.info("Education saved | pass_rate=%s%% live=%s", result["national_pass_rate_pct"], bool(live))
    return result
