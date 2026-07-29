"""
Forex / ZAR Exchange Rate Scraper
-----------------------------------
Source 1 : https://open.er-api.com/v6/latest/USD  (free, no key needed)
Source 2 : https://api.frankfurter.app  (SARB-aligned historical series)
Source 3 : https://www.resbank.co.za/SarbWebApi/   (SARB public API)
Cadence  : Real-time / daily
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import requests

from scrapers.sources.frankfurter import fetch_usd_zar_monthly_history

log = logging.getLogger(__name__)

ER_API = "https://open.er-api.com/v6/latest/USD"
SARB_API = "https://custom.resbank.co.za/SarbWebApi/WebIndicators/CurrentGroupData/Rates"

CURRENCIES = ["ZAR", "EUR", "GBP", "JPY", "AUD", "CNY", "NGN", "KES", "BWP"]


def _fetch_live_rates() -> dict | None:
    try:
        r = requests.get(ER_API, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get("result") == "success":
            rates = data["rates"]
            return {
                "usd_zar": round(rates.get("ZAR", 0), 4),
                "eur_zar": round(rates.get("ZAR", 0) / rates.get("EUR", 1), 4),
                "gbp_zar": round(rates.get("ZAR", 0) / rates.get("GBP", 1), 4),
                "usd_bwp": round(rates.get("BWP", 0), 4),
                "usd_ngn": round(rates.get("NGN", 0), 4),
                "usd_kes": round(rates.get("KES", 0), 4),
                "all_vs_usd": {c: round(rates[c], 4) for c in CURRENCIES if c in rates},
                "timestamp": data.get("time_last_update_utc", ""),
                "next_update": data.get("time_next_update_utc", ""),
            }
    except Exception as e:
        log.error(f"Exchange rate API failed: {e}")
    return None


def _fetch_sarb_rates() -> dict | None:
    try:
        r = requests.get(
            SARB_API,
            timeout=10,
            headers={"Accept": "application/json"},
        )
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        log.warning(f"SARB API failed: {e}")
    return None


def fetch(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    live = _fetch_live_rates()
    sarb = _fetch_sarb_rates()
    frankfurter_history = fetch_usd_zar_monthly_history(months=6)

    usd_zar = (live or _fallback_rates()).get("usd_zar", 18.64)

    result = {
        "source": "open.er-api.com · Frankfurter · SARB",
        "scraped_at": datetime.utcnow().isoformat(),
        "live_rates": live or _fallback_rates(),
        "sarb_data": sarb,
        "is_live": live is not None,
        "usd_zar_history": frankfurter_history or _fallback_history(),
        "intelligence": {
            "import_cost_per_usd_1000_r": round(usd_zar * 1000),
            "sarb_official_url": (
                "https://www.resbank.co.za/en/home/what-we-do/statistics/"
                "key-statistics/selected-historical-rates"
            ),
            "frankfurter_api": "https://api.frankfurter.app",
        },
        "ingestion": {
            "open_er_api": live is not None,
            "frankfurter": bool(frankfurter_history),
            "sarb_api": sarb is not None,
        },
    }

    out = output_dir / "forex.json"
    out.write_text(json.dumps(result, indent=2))
    log.info(
        "Forex data saved → %s  |  USD/ZAR = %s",
        out,
        result["live_rates"].get("usd_zar"),
    )
    return result


def _fallback_rates() -> dict:
    return {
        "usd_zar": 18.64,
        "eur_zar": 20.21,
        "gbp_zar": 23.48,
        "usd_bwp": 13.72,
        "usd_ngn": 1600.0,
        "usd_kes": 129.5,
        "all_vs_usd": {"ZAR": 18.64, "EUR": 0.922, "GBP": 0.793},
        "timestamp": "fallback",
    }


def _fallback_history() -> dict[str, float]:
    return {
        "2026-03": 18.95,
        "2026-04": 18.42,
        "2026-05": 17.88,
        "2026-06": 17.35,
        "2026-07": 16.71,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = fetch(Path("data"))
    print(f"USD/ZAR: {data['live_rates']['usd_zar']}")
    print(f"History months: {len(data['usd_zar_history'])}")
