"""PayProp Rental Index — scrape public ZA landing page for headline growth."""

from __future__ import annotations

import logging
import re

import requests

from scrapers._common import HEADERS

log = logging.getLogger(__name__)

PAYPROP_ZA = "https://www.payprop.com/za/rental-index"


def fetch_rental_growth_pct() -> float | None:
    try:
        response = requests.get(PAYPROP_ZA, headers=HEADERS, timeout=15)
        text = response.text
        patterns = [
            r"rental growth[^\d]*(\d+[\.,]\d+)\s*%",
            r"growth of (\d+[\.,]\d+)\s*%",
            r"(\d+[\.,]\d+)\s*%\s*(?:year-on-year|YoY|yoy)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = float(match.group(1).replace(",", "."))
                log.info("PayProp rental growth: %s%%", value)
                return value
    except Exception as exc:
        log.debug("PayProp scrape failed: %s", exc)
    return None
