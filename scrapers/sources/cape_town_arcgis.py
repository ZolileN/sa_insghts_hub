"""City of Cape Town — ArcGIS Open Data Hub search API."""

from __future__ import annotations

import logging
import re
from typing import Any

import requests
import urllib3

from scrapers._common import HEADERS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log = logging.getLogger(__name__)

ARCGIS_HUB = "https://opendata-cctegis.opendata.arcgis.com/api/v3/datasets"


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text or "").strip()


def fetch_cape_town_open_data(queries: list[str] | None = None) -> dict[str, Any] | None:
    queries = queries or [
        "cape town valuation",
        "cape town property",
        "cape town dam",
        "general valuation",
    ]
    datasets: list[dict[str, Any]] = []
    seen: set[str] = set()

    for query in queries:
        try:
            response = requests.get(
                ARCGIS_HUB,
                params={"q": query, "page[size]": 8},
                headers=HEADERS,
                timeout=25,
                verify=False,
            )
            if response.status_code != 200:
                continue
            for item in response.json().get("data", []):
                dataset_id = item.get("id", "")
                if dataset_id in seen:
                    continue
                seen.add(dataset_id)
                attrs = item.get("attributes", {})
                desc = _strip_html(attrs.get("description") or "")
                if "cape town" not in desc.lower() and "cape town" not in query:
                    continue
                datasets.append(
                    {
                        "id": dataset_id,
                        "record_count": attrs.get("recordCount"),
                        "description": desc[:160],
                        "query": query,
                    }
                )
        except Exception as exc:
            log.debug("Cape Town ArcGIS query %s: %s", query, exc)

    if not datasets:
        return None

    total_records = sum(
        d.get("record_count") or 0 for d in datasets if d.get("record_count")
    )
    log.info(
        "Cape Town open data: %d datasets, ~%s records",
        len(datasets),
        total_records,
    )
    return {
        "portal": "https://opendata-cctegis.opendata.arcgis.com",
        "gv_roll": "GV2025",
        "gv_implementation_year": 2026,
        "dataset_count": len(datasets),
        "total_records": total_records,
        "datasets": datasets[:12],
        "ingestion_source": "ArcGIS Hub API",
    }
