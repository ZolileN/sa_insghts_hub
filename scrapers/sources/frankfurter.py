"""Frankfurter API — free ECB-linked FX history (https://api.frankfurter.app)."""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date, timedelta

import requests

from scrapers._common import HEADERS

log = logging.getLogger(__name__)

FRANKFURTER_BASE = "https://api.frankfurter.app"


def fetch_usd_zar_monthly_history(months: int = 6) -> dict[str, float]:
    """
    Return last N calendar months of USD/ZAR (month-end rate), keyed YYYY-MM.
    """
    end = date.today()
    start = end - timedelta(days=months * 31 + 5)
    url = (
        f"{FRANKFURTER_BASE}/{start.isoformat()}..{end.isoformat()}"
        "?from=USD&to=ZAR"
    )
    try:
        response = requests.get(url, headers=HEADERS, timeout=45)
        response.raise_for_status()
        rates_by_day = response.json().get("rates", {})
        if not rates_by_day:
            return {}

        monthly: dict[str, list[float]] = defaultdict(list)
        for day, payload in rates_by_day.items():
            zar = payload.get("ZAR")
            if zar is None:
                continue
            monthly[day[:7]].append(float(zar))

        result: dict[str, float] = {}
        for month, values in sorted(monthly.items()):
            result[month] = round(values[-1], 4)
        log.info("Frankfurter USD/ZAR history: %d months", len(result))
        return result
    except Exception as exc:
        log.warning("Frankfurter history failed: %s", exc)
        return {}
