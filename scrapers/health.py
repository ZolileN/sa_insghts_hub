"""
Health Scraper — NICD surveillance + DHIS2 + SANAC
Sources : https://www.nicd.ac.za (WordPress API + PDF sitreps)
          https://dhis.gov.za · SANAC · SAMRC
"""

import logging
import re
from pathlib import Path

import requests

from scrapers._common import HEADERS, load_topic_json, save_topic_json, utc_now_iso
from scrapers.sources.nicd import fetch_nicd_surveillance

log = logging.getLogger(__name__)

DHIS2_BASE = "https://dhis.gov.za/dhis/api"

_YEAR_SUFFIX = re.compile(r"^(.+)_(\d{4})$")


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


def _latest_year(annual: dict) -> str | None:
    years = [y for y in annual.keys() if re.fullmatch(r"\d{4}", y)]
    return max(years) if years else None


def _migrate_section_annual(section: dict, metric_names: tuple[str, ...]) -> dict:
    """Move legacy `metric_2023` keys into `annual: { 2023: { metric: value } }`."""
    section = dict(section)
    annual = dict(section.get("annual", {}))

    for key, value in list(section.items()):
        match = _YEAR_SUFFIX.match(key)
        if not match:
            continue
        metric, year = match.group(1), match.group(2)
        if metric not in metric_names:
            continue
        annual.setdefault(year, {})
        annual[year][metric] = value

    if annual:
        section["annual"] = annual
        report_year = _latest_year(annual)
        if report_year:
            section["report_year"] = report_year

    return section


def _migrate_health_payload(data: dict) -> dict:
    data = dict(data)
    if data.get("hiv"):
        data["hiv"] = _migrate_section_annual(
            data["hiv"],
            ("new_infections", "aids_deaths"),
        )
    if data.get("tb"):
        data["tb"] = _migrate_section_annual(
            data["tb"],
            ("notifications", "dr_tb_cases"),
        )
    return data


def fetch(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    cached = load_topic_json(output_dir, "health")

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

    result = dict(cached)
    result.update({
        "source": "NICD · SAMRC · SANAC · NDOH DHIS2",
        "scraped_at": utc_now_iso(),
        "is_live": nicd_live or dhis2_live,
        "dhis2_connected": dhis2_live,
        "ingestion": ingestion,
        "data_sources": {
            "nicd": "https://www.nicd.ac.za",
            "samrc": "https://www.samrc.ac.za",
            "healthsites": "https://healthsites.io",
            "dhis2": "https://dhis.gov.za",
        },
    })

    if nicd:
        result["surveillance"] = nicd
    elif "surveillance" not in result:
        result["surveillance"] = None

    result = _migrate_health_payload(result)

    if not nicd_live and not dhis2_live and not cached:
        raise RuntimeError("Health: no live NICD/DHIS2 data and no cached health.json")

    path = save_topic_json(output_dir, "health", result)
    log.info(
        "Health saved → %s | NICD live=%s DHIS2=%s measles_ytd=%s",
        path,
        nicd_live,
        dhis2_live,
        (nicd or result.get("surveillance") or {}).get("measles_confirmed_ytd"),
    )
    return result
