"""Eskom published statistics from media statements (FY hours, EAF, streaks)."""

from __future__ import annotations

import logging
import re

import requests

from scrapers._common import HEADERS

log = logging.getLogger(__name__)

MEDIA_URLS = [
    "https://www.eskom.co.za/eskom-marks-300-days-without-loadshedding/",
    "https://www.eskom.co.za/eskom-maintains-grid-stability-as-winter-demand-rises-midnight-marks-a-year-without-loadshedding/",
    "https://www.eskom.co.za/eskoms-power-system-remains-stable-and-supporting-the-return-to-work-strengthened-by-increasing-plant-availability-and-sustained-reduction-in-unplanned-outages/",
]


def _parse_media_html(html: str, source_url: str) -> dict | None:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)

    hours_match = re.search(
        r"(\d+)\s+hours?\s+of\s+loadshedding",
        text,
        re.IGNORECASE,
    )
    streak_match = re.search(
        r"(\d+)\s+consecutive\s+days?\s+without",
        text,
        re.IGNORECASE,
    )
    eaf_match = re.search(
        r"Energy\s+Availability\s+Factor[^%]{0,80}?(\d{2,3}(?:\.\d+)?)\s*%",
        text,
        re.IGNORECASE,
    )
    fy_match = re.search(
        r"financial\s+year[^0-9]{0,40}(\d{4})\s*/\s*(\d{2,4})",
        text,
        re.IGNORECASE,
    )
    calendar_2025 = re.search(
        r"only\s+(\d+)\s+hours?\s+of\s+loadshedding\s+recorded\s+in\s+April\s+and\s+May\s+2025",
        text,
        re.IGNORECASE,
    )

    if not any([hours_match, streak_match, eaf_match]):
        return None

    result: dict = {"source_url": source_url}
    if hours_match:
        result["loadshedding_hours_fy"] = int(hours_match.group(1))
    if streak_match:
        result["consecutive_days_without"] = int(streak_match.group(1))
    if eaf_match:
        result["eaf_pct"] = float(eaf_match.group(1))
    if fy_match:
        end = fy_match.group(2)
        if len(end) == 2:
            end = fy_match.group(1)[:2] + end
        result["financial_year"] = f"{fy_match.group(1)}/{end[-2:]}"
    if calendar_2025:
        result["calendar_year_hours"] = {2025: int(calendar_2025.group(1))}

    no_interruptions_current_fy = re.search(
        r"no\s+interruptions?\s+in\s+the\s+current\s+financial\s+year",
        text,
        re.IGNORECASE,
    )
    if no_interruptions_current_fy:
        result["current_fy_hours"] = 0

    return result


def fetch_eskom_media_stats() -> dict | None:
    """Merge stats from the latest Eskom media statements."""
    merged: dict = {}
    for url in MEDIA_URLS:
        try:
            response = requests.get(url, headers=HEADERS, timeout=20)
            if response.status_code != 200:
                continue
            parsed = _parse_media_html(response.text, url)
            if parsed:
                merged.update(parsed)
        except Exception as exc:
            log.debug("Eskom media %s: %s", url, exc)

    if not merged:
        return None

    merged["source"] = "eskom.co.za media statements"
    log.info(
        "Eskom media stats: FY hrs=%s streak=%s EAF=%s",
        merged.get("loadshedding_hours_fy"),
        merged.get("consecutive_days_without"),
        merged.get("eaf_pct"),
    )
    return merged


def apply_media_stats_to_energy(cached: dict, stats: dict) -> dict:
    """Merge scraped Eskom media figures into energy payload."""
    energy = dict(cached)
    energy["fy_stats"] = stats

    annual = dict(energy.get("annual_totals", {}))
    calendar_hours = stats.get("calendar_year_hours", {})
    for year, hours in calendar_hours.items():
        annual[str(year)] = hours

    if stats.get("current_fy_hours") == 0:
        # Current FY started Apr — label end year from financial_year or calendar
        fy = stats.get("financial_year", "")
        if "/" in fy:
            end_year = fy.split("/")[0]
            if len(fy.split("/")[1]) == 2:
                end_year = str(int(fy.split("/")[0]) + 1)
            annual[str(end_year)] = 0

    loadshedding_fy = stats.get("loadshedding_hours_fy")
    if loadshedding_fy is not None and stats.get("financial_year"):
        fy_label = stats["financial_year"]
        energy["loadshedding_hours_by_fy"] = energy.get("loadshedding_hours_by_fy", {})
        energy["loadshedding_hours_by_fy"][fy_label] = loadshedding_fy

    energy["annual_totals"] = annual
    return energy
