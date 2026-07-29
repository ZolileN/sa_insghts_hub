"""Vulekamali CKAN API — national budget datasets."""

from __future__ import annotations

import logging
import re
from typing import Any

import requests

from scrapers._common import HEADERS

log = logging.getLogger(__name__)

VULEKAMALI_CKAN = "https://data.vulekamali.gov.za/api/3/action"


def _ckan_action(action: str, params: dict[str, Any] | None = None) -> dict | None:
    url = f"{VULEKAMALI_CKAN}/{action}"
    try:
        response = requests.get(url, params=params or {}, headers=HEADERS, timeout=45)
        if response.status_code != 200:
            return None
        payload = response.json()
        if payload.get("success"):
            return payload.get("result")
    except Exception as exc:
        log.warning("Vulekamali CKAN %s failed: %s", action, exc)
    return None


def fetch_budget_summary() -> dict[str, Any] | None:
    search = _ckan_action(
        "package_search",
        {"q": "estimates national expenditure", "rows": 5},
    )
    if not search:
        return None

    results = search.get("results", [])
    packages = [
        {
            "name": r.get("name"),
            "title": r.get("title"),
            "financial_year": _financial_year_from_title(r.get("title", "")),
        }
        for r in results
    ]

    financial_years = sorted(
        {p["financial_year"] for p in packages if p.get("financial_year")},
        reverse=True,
    )

    return {
        "portal": "https://vulekamali.gov.za",
        "datastore": "https://data.vulekamali.gov.za",
        "packages_found": len(results),
        "latest_financial_year": financial_years[0] if financial_years else None,
        "packages": packages[:5],
        "ingestion_source": "Vulekamali CKAN API",
    }


def _financial_year_from_title(title: str) -> str | None:
    match = re.search(r"20\d{2}[-/]20\d{2}", title)
    return match.group(0).replace("/", "-") if match else None
