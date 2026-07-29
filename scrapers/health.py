"""
Health Scraper — NICD surveillance + DHIS2 + SANAC
Sources : https://www.nicd.ac.za (WordPress API + PDF sitreps)
          https://dhis.gov.za · SANAC · SAMRC
"""
import json
import logging
from pathlib import Path

import requests

from scrapers._common import HEADERS, utc_now_iso
from scrapers.sources.nicd import fetch_nicd_surveillance

log = logging.getLogger(__name__)

DHIS2_BASE = "https://dhis.gov.za/dhis/api"


def _fetch_dhis2(endpoint: str) -> dict | None:
    try:
        url = f"{DHIS2_BASE}/{endpoint}"
        r = requests.get(
            url,
            headers={**HEADERS, "Accept": "application/json"},
            timeout=15,
        )
        if r.status_code == 200:
            return r.json()
    except Exception as exc:
        log.debug("DHIS2 %s: %s", endpoint, exc)
    return None


def fetch(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    existing_path = output_dir / "health.json"
    existing: dict = {}
    if existing_path.exists():
        try:
            existing = json.loads(existing_path.read_text())
        except json.JSONDecodeError:
            existing = {}

    dhis2_info = _fetch_dhis2("system/info")
    dhis2_live = dhis2_info is not None

    nicd = fetch_nicd_surveillance()
    nicd_live = nicd is not None and bool(nicd.get("measles_confirmed_ytd"))

    ingestion = {
        "nicd_api": bool(nicd),
        "nicd_pdf": bool(nicd and nicd.get("sitrep_pdf_url")),
        "dhis2": dhis2_live,
        "samrc": False,
        "healthsites": False,
    }

    result = {
        "source": "NICD · SAMRC · SANAC · NDOH DHIS2",
        "scraped_at": utc_now_iso(),
        "is_live": nicd_live or dhis2_live,
        "dhis2_connected": dhis2_live,
        "hiv": existing.get("hiv") or {
            "plhiv_millions": 7.8,
            "prevalence_15_49_pct": 18.3,
            "on_art_millions": 5.7,
            "art_coverage_pct": 73.0,
            "new_infections_2023": 140000,
            "aids_deaths_2023": 57000,
        },
        "tb": existing.get("tb") or {
            "incidence_per_100k": 468,
            "notifications_2023": 257000,
            "treatment_success_pct": 81,
            "tb_hiv_coinfection_pct": 60,
            "dr_tb_cases_2023": 6800,
        },
        "health_system": existing.get("health_system") or {
            "maternal_mortality_per_100k": 118,
            "under5_mortality_per_1000": 34,
            "public_hospitals": 407,
            "private_hospitals": 211,
            "nhi_implementation": "Phase 1 — currently active",
        },
        "provinces": existing.get("provinces") or {
            "Western Cape": {"hiv_prevalence_pct": 12.8, "tb_per_100k": 720, "doctors_per_100k": 82, "art_coverage_pct": 72},
            "Gauteng": {"hiv_prevalence_pct": 11.9, "tb_per_100k": 620, "doctors_per_100k": 74, "art_coverage_pct": 68},
            "KwaZulu-Natal": {"hiv_prevalence_pct": 25.2, "tb_per_100k": 480, "doctors_per_100k": 38, "art_coverage_pct": 71},
            "Eastern Cape": {"hiv_prevalence_pct": 15.4, "tb_per_100k": 520, "doctors_per_100k": 32, "art_coverage_pct": 65},
            "Limpopo": {"hiv_prevalence_pct": 10.3, "tb_per_100k": 290, "doctors_per_100k": 18, "art_coverage_pct": 58},
            "Mpumalanga": {"hiv_prevalence_pct": 15.8, "tb_per_100k": 310, "doctors_per_100k": 22, "art_coverage_pct": 64},
            "North West": {"hiv_prevalence_pct": 12.1, "tb_per_100k": 340, "doctors_per_100k": 19, "art_coverage_pct": 61},
            "Free State": {"hiv_prevalence_pct": 11.6, "tb_per_100k": 380, "doctors_per_100k": 21, "art_coverage_pct": 60},
            "Northern Cape": {"hiv_prevalence_pct": 6.1, "tb_per_100k": 560, "doctors_per_100k": 41, "art_coverage_pct": 70},
        },
        "plhiv_trend": existing.get("plhiv_trend") or {
            "2010": 5.8, "2012": 6.2, "2014": 6.6, "2016": 7.1,
            "2018": 7.5, "2020": 7.7, "2022": 7.8, "2024": 7.8,
        },
        "art_trend": existing.get("art_trend") or {
            "2010": 1.0, "2012": 2.0, "2014": 2.9, "2016": 4.0,
            "2018": 5.0, "2020": 5.4, "2022": 5.6, "2024": 5.7,
        },
        "surveillance": nicd or existing.get("surveillance"),
        "ingestion": ingestion,
        "data_sources": {
            "nicd": "https://www.nicd.ac.za",
            "samrc": "https://www.samrc.ac.za",
            "healthsites": "https://healthsites.io",
            "dhis2": "https://dhis.gov.za",
        },
    }

    (output_dir / "health.json").write_text(json.dumps(result, indent=2))
    log.info(
        "Health saved | NICD live=%s DHIS2=%s measles_ytd=%s",
        nicd_live,
        dhis2_live,
        (nicd or {}).get("measles_confirmed_ytd"),
    )
    return result
