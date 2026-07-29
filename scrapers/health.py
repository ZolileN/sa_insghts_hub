"""
Health Scraper — NICD surveillance + DHIS2 + SANAC + NDOH TB
Sources : https://www.nicd.ac.za (WordPress API + PDF sitreps)
          https://dhis.gov.za · SANAC annual reports · NDOH TB Recovery Plan
"""

import logging
import re
from pathlib import Path

import requests

from scrapers._common import HEADERS, load_topic_json, save_topic_json, utc_now_iso
from scrapers.sources.nicd import fetch_nicd_surveillance
from scrapers.sources.ndoh_tb import fetch_ndoh_tb_annual_stats
from scrapers.sources.sanac_annual import fetch_sanac_annual_stats

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


def _merge_annual_section(
    section: dict,
    by_year: dict,
    metric_names: tuple[str, ...],
) -> dict:
    section = dict(section)
    annual = dict(section.get("annual", {}))
    for year, metrics in by_year.items():
        if not re.fullmatch(r"\d{4}", str(year)):
            continue
        bucket = dict(annual.get(year, {}))
        for name in metric_names:
            if metrics.get(name) is not None:
                bucket[name] = metrics[name]
        if bucket:
            annual[str(year)] = bucket
    if annual:
        section["annual"] = annual
        section["report_year"] = _latest_year(annual)
    return section


def apply_annual_health_stats(
    cached: dict,
    sanac: dict | None,
    ndoh_tb: dict | None,
) -> dict:
    result = dict(cached)

    if sanac:
        hiv = dict(result.get("hiv", {}))
        hiv = _merge_annual_section(
            hiv,
            sanac.get("by_year", {}),
            ("new_infections", "aids_deaths"),
        )
        hiv["sanac_report_period"] = sanac.get("report_period")
        hiv["sanac_source_url"] = sanac.get("source_url")
        if sanac.get("by_year"):
            hiv["report_year"] = _latest_year(sanac["by_year"])
        result["hiv"] = hiv

        if sanac.get("tb_treatment_success_pct") is not None:
            tb = dict(result.get("tb", {}))
            tb["treatment_success_pct"] = sanac["tb_treatment_success_pct"]
            tb["treatment_success_source"] = sanac.get("source_url")
            result["tb"] = tb

    if ndoh_tb:
        tb = dict(result.get("tb", {}))
        tb = _merge_annual_section(
            tb,
            ndoh_tb.get("by_year", {}),
            ("notifications", "dr_tb_cases"),
        )
        tb["ndoh_tb_sources"] = ndoh_tb.get("sources")
        tb["ndoh_tb_source"] = ndoh_tb.get("source")
        if ndoh_tb.get("by_year"):
            tb["report_year"] = _latest_year(ndoh_tb["by_year"])
        result["tb"] = tb

    return result


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
    cached = _migrate_health_payload(load_topic_json(output_dir, "health"))

    dhis2_info = _fetch_dhis2("system/info")
    dhis2_live = dhis2_info is not None

    nicd = fetch_nicd_surveillance()
    nicd_live = nicd is not None and bool(nicd.get("measles_confirmed_ytd"))

    sanac = fetch_sanac_annual_stats()
    ndoh_tb = fetch_ndoh_tb_annual_stats()
    annual_live = bool(sanac or ndoh_tb)

    ingestion = {
        "nicd_api": bool(nicd),
        "nicd_pdf": bool(nicd and nicd.get("sitrep_pdf_url")),
        "dhis2": dhis2_live,
        "sanac_annual": bool(sanac),
        "ndoh_tb": bool(ndoh_tb),
        "samrc": False,
        "healthsites": False,
    }

    result = dict(cached)
    result.update({
        "source": "NICD · SANAC annual · NDOH TB Recovery Plan · NDOH DHIS2",
        "scraped_at": utc_now_iso(),
        "is_live": nicd_live or dhis2_live or annual_live,
        "dhis2_connected": dhis2_live,
        "ingestion": ingestion,
        "data_sources": {
            "nicd": "https://www.nicd.ac.za",
            "sanac": "https://sanac.org.za/reports/sa-nasa/",
            "ndoh_tb": "https://www.health.gov.za/tb-recovery-plan/",
            "samrc": "https://www.samrc.ac.za",
            "healthsites": "https://healthsites.io",
            "dhis2": "https://dhis.gov.za",
        },
    })

    if nicd:
        result["surveillance"] = nicd
    elif "surveillance" not in result:
        result["surveillance"] = None

    result = apply_annual_health_stats(result, sanac, ndoh_tb)

    if sanac and result.get("hiv", {}).get("annual"):
        sanac_years = sanac.get("by_year", {})
        annual = dict(result["hiv"]["annual"])
        for year in list(annual.keys()):
            if year not in sanac_years and year < max(sanac_years.keys(), default="0"):
                continue
        if "2017" in annual and "2017" not in sanac_years:
            del annual["2017"]
        result["hiv"]["annual"] = annual
        result["hiv"]["report_year"] = _latest_year(sanac_years)

    if ndoh_tb and result.get("tb", {}).get("annual"):
        result["tb"]["report_year"] = _latest_year(ndoh_tb.get("by_year", {}))

    if not nicd_live and not dhis2_live and not annual_live and not cached:
        raise RuntimeError("Health: no live sources and no cached health.json")

    path = save_topic_json(output_dir, "health", result)
    log.info(
        "Health saved → %s | NICD=%s SANAC=%s NDOH_TB=%s report_years hiv=%s tb=%s",
        path,
        nicd_live,
        bool(sanac),
        bool(ndoh_tb),
        result.get("hiv", {}).get("report_year"),
        result.get("tb", {}).get("report_year"),
    )
    return result
