"""SANAC annual report — Thembisa HIV estimates cited in public PDFs."""

from __future__ import annotations

import logging
import re

from scrapers._common import download_bytes, extract_pdf_text

log = logging.getLogger(__name__)

SANAC_ANNUAL_PDF = (
    "https://sanac.org.za/wp-content/uploads/2025/01/"
    "Annual-Report-South-African-National-AIDS-Council-Trust_V1.9_Compress.pdf"
)


def _parse_sanac_text(text: str, source_url: str) -> dict | None:
    flat = re.sub(r"\s+", " ", text)
    result: dict = {"source_url": source_url, "by_year": {}}

    new_inf = re.search(
        r"new HIV infections decreased from [\d,]+ .*? to ([\d, ]+)\s*\(incidence",
        flat,
        re.IGNORECASE,
    )
    aids = re.search(
        r"there were ([\d,]+)\s+AIDS-related deaths, down from",
        flat,
        re.IGNORECASE,
    )
    if not aids:
        aids = re.search(r"51,\s*152 AIDS-related deaths", flat, re.IGNORECASE)

    year_deaths = re.search(
        r"In (\d{4}), there were [\d,]+\s+AIDS-related deaths",
        flat,
        re.IGNORECASE,
    )

    if new_inf:
        y = "2022"
        result["by_year"].setdefault(y, {})["new_infections"] = int(
            re.sub(r"[\s,]", "", new_inf.group(1))
        )

    if aids:
        if aids.lastindex:
            y = year_deaths.group(1) if year_deaths else "2022"
            deaths = int(aids.group(1).replace(",", ""))
        else:
            y = "2022"
            deaths = 51152
        result["by_year"].setdefault(y, {})["aids_deaths"] = deaths

    success = re.search(
        r"treatment success rate was at ([\d.]+)%",
        flat,
        re.IGNORECASE,
    )
    if success:
        result["tb_treatment_success_pct"] = float(success.group(1))

    if not result["by_year"] and not result.get("tb_treatment_success_pct"):
        return None

    result["report_period"] = "FY 2023/24 (SANAC annual report)"
    log.info(
        "SANAC annual parsed: years=%s TB success=%s",
        list(result["by_year"].keys()),
        result.get("tb_treatment_success_pct"),
    )
    return result


def fetch_sanac_annual_stats() -> dict | None:
    pdf = download_bytes(SANAC_ANNUAL_PDF, timeout=120)
    if not pdf or not pdf.startswith(b"%PDF"):
        log.warning("SANAC annual PDF unavailable")
        return None
    text = extract_pdf_text(pdf, max_pages=40)
    return _parse_sanac_text(text, SANAC_ANNUAL_PDF)
