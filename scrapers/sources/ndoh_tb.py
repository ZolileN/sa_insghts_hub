"""NDOH TB Recovery Plan — annual TB notifications and DR-TB cases."""

from __future__ import annotations

import logging
import re

from scrapers._common import download_bytes, extract_pdf_text

log = logging.getLogger(__name__)

NDOH_TB_REPORTS: list[tuple[str, str]] = [
    (
        "2024",
        "https://www.health.gov.za/wp-content/uploads/2025/05/"
        "TB-Recovery-Plan-4_final_250526-1.pdf",
    ),
    (
        "2023",
        "https://tbthinktank.org/wp-content/uploads/2024/06/"
        "TB-Recovery-Plan-3.0-2024-25-ver010624.pdf",
    ),
]


def _parse_ndoh_tb_text(text: str, year: str, source_url: str) -> dict | None:
    flat = re.sub(r"\s+", " ", text)
    result: dict = {"year": year, "source_url": source_url}

    detailed = re.search(
        r"total of ([\d,]+) people with all types of TB "
        r"\(DS-TB: ([\d,]+); DR-TB: ([\d,]+)\)",
        flat,
        re.IGNORECASE,
    )
    if detailed:
        result["notifications"] = int(detailed.group(1).replace(",", ""))
        result["dr_tb_cases"] = int(detailed.group(3).replace(",", ""))
    else:
        simple = re.search(
            r"reported a total of ([\d,]+) people with TB",
            flat,
            re.IGNORECASE,
        )
        if simple:
            result["notifications"] = int(simple.group(1).replace(",", ""))

    if not result.get("notifications"):
        return None

    log.info(
        "NDOH TB %s: notifications=%s dr_tb=%s",
        year,
        result.get("notifications"),
        result.get("dr_tb_cases"),
    )
    return result


def fetch_ndoh_tb_annual_stats() -> dict | None:
    merged: dict = {"by_year": {}, "sources": []}
    for year, url in NDOH_TB_REPORTS:
        pdf = download_bytes(url, timeout=120)
        if not pdf or not pdf.startswith(b"%PDF"):
            log.debug("NDOH TB PDF skip %s", url)
            continue
        parsed = _parse_ndoh_tb_text(extract_pdf_text(pdf, max_pages=30), year, url)
        if not parsed:
            continue
        merged["by_year"][year] = {
            k: parsed[k]
            for k in ("notifications", "dr_tb_cases")
            if parsed.get(k) is not None
        }
        merged["sources"].append({"year": year, "url": url})

    if not merged["by_year"]:
        return None

    merged["source"] = "NDOH TB Recovery Plan"
    return merged
