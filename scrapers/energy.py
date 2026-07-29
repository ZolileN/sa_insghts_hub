"""
Load Shedding & Energy Scraper
---------------------------------
Source 1 : https://loadshedding.eskom.co.za/LoadShedding/GetStatus  (Eskom official)
Source 2 : https://eskom-calendar-api.shuttleapp.rs/outages/south-africa (community API)
Source 3 : https://www.eskom.co.za media statements (FY hours, EAF, streaks)
Cadence  : Real-time for stage; historical series preserved from live scrapes + cache
"""

import logging
from pathlib import Path

import requests

from scrapers._common import (
    HEADERS,
    load_topic_json,
    save_topic_json,
    utc_now_iso,
)
from scrapers.sources.eskom_stats import (
    apply_media_stats_to_energy,
    fetch_eskom_media_stats,
)

log = logging.getLogger(__name__)

ESKOM_STATUS_URL = "https://loadshedding.eskom.co.za/LoadShedding/GetStatus"
ESKOM_CALENDAR_URL = "https://eskom-calendar-api.shuttleapp.rs/outages/south-africa"


def _fetch_eskom_stage() -> dict | None:
    try:
        response = requests.get(ESKOM_STATUS_URL, headers=HEADERS, timeout=8)
        response.raise_for_status()
        stage_raw = response.text.strip()
        stage = int(stage_raw) - 1
        stage = max(0, stage)
        log.info("Eskom current stage: %s", stage)
        return {
            "current_stage": stage,
            "stage_label": f"Stage {stage}" if stage > 0 else "No load shedding",
            "active": stage > 0,
            "stage_source": "loadshedding.eskom.co.za",
        }
    except Exception as exc:
        log.error("Eskom stage API failed: %s", exc)
        return None


def _fetch_community_calendar() -> list | None:
    try:
        response = requests.get(ESKOM_CALENDAR_URL, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data[:10] if isinstance(data, list) else None
    except Exception as exc:
        log.debug("Community calendar: %s", exc)
    return None


def fetch(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    cached = load_topic_json(output_dir, "energy")

    stage = _fetch_eskom_stage()
    sched = _fetch_community_calendar()
    media_stats = fetch_eskom_media_stats()

    result = dict(cached)
    result.update({
        "source": "Eskom LoadShedding API · Eskom media · community calendar",
        "scraped_at": utc_now_iso(),
        "is_live": stage is not None,
    })

    if stage:
        result["current_stage"] = stage["current_stage"]
        result["stage_label"] = stage["stage_label"]
        result["active"] = stage["active"]
        result["stage_source"] = stage["stage_source"]
    elif "current_stage" not in result:
        result["current_stage"] = 0
        result["stage_label"] = "Unknown"
        result["active"] = False

    if sched is not None:
        result["upcoming_outages"] = sched

    if media_stats:
        result = apply_media_stats_to_energy(result, media_stats)
        result["is_live"] = True

    if not stage and not media_stats and not cached:
        raise RuntimeError("Energy: no live Eskom data and no cached energy.json")

    path = save_topic_json(output_dir, "energy", result)
    log.info(
        "Energy data saved → %s | Stage=%s Live=%s",
        path,
        result.get("stage_label"),
        result.get("is_live"),
    )
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = fetch(Path("data"))
    print(f"Current stage : {data['stage_label']}")
    print(f"Live          : {data['is_live']}")
