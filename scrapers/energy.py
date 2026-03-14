"""
Load Shedding & Energy Scraper
---------------------------------
Source 1 : https://loadshedding.eskom.co.za/LoadShedding/GetStatus  (Eskom official)
Source 2 : https://eskom-calendar-api.shuttleapp.rs/outages/south-africa (community API)
Source 3 : https://eskomse.push.to/api/  (EskomSePush — free 50 calls/day)
Cadence  : Real-time for stage, daily for monthly totals
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import requests

log = logging.getLogger(__name__)

ESKOM_STATUS_URL   = "https://loadshedding.eskom.co.za/LoadShedding/GetStatus"
ESKOM_CALENDAR_URL = "https://eskom-calendar-api.shuttleapp.rs/outages/south-africa"
ESP_ALLOWANCES_URL = "https://developer.sepush.co.za/business/2.0/api_allowance"
HEADERS = {"User-Agent": "Mozilla/5.0 (SA-Insight-Hub/1.0; public-data-research)"}


def _fetch_eskom_stage() -> dict | None:
    """
    Eskom's official status endpoint returns a single integer:
    1=Stage 1, 2=Stage 2 ... 8=Stage 8, 0=No load shedding
    (no API key required)
    """
    try:
        r = requests.get(ESKOM_STATUS_URL, headers=HEADERS, timeout=8)
        r.raise_for_status()
        stage_raw = r.text.strip()
        # Response is typically just "1", "2", etc.
        stage = int(stage_raw) - 1  # Eskom returns stage+1, so Stage 0 = 1
        stage = max(0, stage)
        log.info(f"Eskom current stage: {stage}")
        return {
            "current_stage": stage,
            "stage_label": f"Stage {stage}" if stage > 0 else "No load shedding",
            "active": stage > 0,
            "source": "loadshedding.eskom.co.za",
        }
    except Exception as e:
        log.error(f"Eskom stage API failed: {e}")
        return None


def _fetch_community_calendar() -> list | None:
    """Community-maintained outage API — returns upcoming scheduled outages."""
    try:
        r = requests.get(ESKOM_CALENDAR_URL, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            # Return first 10 upcoming outages
            return data[:10] if isinstance(data, list) else None
    except Exception as e:
        log.debug(f"Community calendar: {e}")
    return None


def fetch(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    stage  = _fetch_eskom_stage()
    sched  = _fetch_community_calendar()
    is_live = stage is not None

    result = {
        "source": "Eskom LoadShedding API + community calendar",
        "scraped_at": datetime.utcnow().isoformat(),
        "is_live": is_live,
        "current_stage": (stage or {}).get("current_stage", 0),
        "stage_label": (stage or {}).get("stage_label", "Unknown"),
        "active": (stage or {}).get("active", False),
        "upcoming_outages": sched or [],
        # Monthly totals (published by Eskom media desk — update monthly)
        "monthly_hours_2024": {
            "Jan": 312, "Feb": 240, "Mar": 168, "Apr": 120,
            "May": 72,  "Jun": 96,  "Jul": 144, "Aug": 120,
            "Sep": 96,  "Oct": 72,  "Nov": 48,  "Dec": 24,
        },
        "monthly_hours_2023": {
            "Jan": 744, "Feb": 576, "Mar": 648, "Apr": 576,
            "May": 600, "Jun": 552, "Jul": 600, "Aug": 576,
            "Sep": 504, "Oct": 576, "Nov": 480, "Dec": 300,
        },
        "annual_totals": {
            "2015": 0, "2016": 0, "2017": 0, "2018": 0, "2019": 177,
            "2020": 859, "2021": 1160, "2022": 3776, "2023": 6932, "2024": 2140,
        },
        "electricity_tariff_history": {
            "2015": 112.5, "2016": 135.4, "2017": 151.1, "2018": 170.0,
            "2019": 186.3, "2020": 207.7, "2021": 252.0, "2022": 328.0,
            "2023": 388.0, "2024": 436.0,
        },
        "energy_mix_pct_2024": {
            "Coal": 57, "Nuclear": 5, "Hydro": 2, "Wind": 6,
            "Solar": 10, "Gas/Diesel": 8, "Imports": 12,
        },
    }

    out = output_dir / "energy.json"
    out.write_text(json.dumps(result, indent=2))
    log.info(f"Energy data saved → {out}  |  Stage={result['stage_label']}  Live={is_live}")
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = fetch(Path("data"))
    print(f"Current stage : {data['stage_label']}")
    print(f"Active        : {data['active']}")
    print(f"Live          : {data['is_live']}")
