"""
Forex / ZAR Exchange Rate Scraper
-----------------------------------
Source 1 : https://open.er-api.com/v6/latest/USD  (free, no key needed)
Source 2 : https://api.frankfurter.app  (SARB-aligned historical series)
Source 3 : https://www.resbank.co.za/SarbWebApi/   (SARB public API)
Cadence  : Real-time / daily
"""

import logging
from pathlib import Path

import requests

from scrapers._common import load_topic_json, save_topic_json, utc_now_iso
from scrapers.sources.frankfurter import fetch_usd_zar_monthly_history

log = logging.getLogger(__name__)

ER_API = "https://open.er-api.com/v6/latest/USD"
SARB_API = "https://custom.resbank.co.za/SarbWebApi/WebIndicators/CurrentGroupData/Rates"

CURRENCIES = ["ZAR", "EUR", "GBP", "JPY", "AUD", "CNY", "NGN", "KES", "BWP"]


def _fetch_live_rates() -> dict | None:
    try:
        response = requests.get(ER_API, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("result") == "success":
            rates = data["rates"]
            return {
                "usd_zar": round(rates.get("ZAR", 0), 4),
                "eur_zar": round(rates.get("ZAR", 0) / rates.get("EUR", 1), 4),
                "gbp_zar": round(rates.get("ZAR", 0) / rates.get("GBP", 1), 4),
                "usd_bwp": round(rates.get("BWP", 0), 4),
                "usd_ngn": round(rates.get("NGN", 0), 4),
                "usd_kes": round(rates.get("KES", 0), 4),
                "all_vs_usd": {
                    c: round(rates[c], 4) for c in CURRENCIES if c in rates
                },
                "timestamp": data.get("time_last_update_utc", ""),
                "next_update": data.get("time_next_update_utc", ""),
            }
    except Exception as exc:
        log.error("Exchange rate API failed: %s", exc)
    return None


def _fetch_sarb_rates() -> dict | None:
    try:
        response = requests.get(
            SARB_API,
            timeout=10,
            headers={"Accept": "application/json"},
        )
        if response.status_code == 200:
            return response.json()
    except Exception as exc:
        log.warning("SARB API failed: %s", exc)
    return None


def fetch(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    cached = load_topic_json(output_dir, "forex")

    live = _fetch_live_rates()
    sarb = _fetch_sarb_rates()
    frankfurter_history = fetch_usd_zar_monthly_history(months=12)

    if not live and not frankfurter_history and not cached.get("live_rates"):
        raise RuntimeError("Forex: no live rates and no cached forex.json")

    live_rates = live or cached.get("live_rates", {})
    usd_zar_history = frankfurter_history or cached.get("usd_zar_history", {})
    usd_zar = live_rates.get("usd_zar") or cached.get("live_rates", {}).get("usd_zar")

    result = dict(cached)
    result.update({
        "source": "open.er-api.com · Frankfurter · SARB",
        "scraped_at": utc_now_iso(),
        "live_rates": live_rates,
        "sarb_data": sarb if sarb is not None else cached.get("sarb_data"),
        "is_live": live is not None,
        "usd_zar_history": usd_zar_history,
        "intelligence": {
            "import_cost_per_usd_1000_r": round((usd_zar or 0) * 1000),
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
    })

    path = save_topic_json(output_dir, "forex", result)
    log.info("Forex data saved → %s | USD/ZAR = %s", path, live_rates.get("usd_zar"))
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = fetch(Path("data"))
    print(f"USD/ZAR: {data['live_rates'].get('usd_zar')}")
