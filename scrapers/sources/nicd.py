"""NICD surveillance — WordPress API + situational report PDFs."""

from __future__ import annotations

import io
import logging
import re
from typing import Any

import requests

from scrapers._common import HEADERS, download_bytes, extract_pdf_text

log = logging.getLogger(__name__)

NICD_POSTS_API = "https://www.nicd.ac.za/wp-json/wp/v2/posts"
NICD_PDF_HOST = "https://www.nicd.ac.za/wp-content/uploads/"


def _fetch_recent_posts(limit: int = 5) -> list[dict[str, Any]]:
    try:
        response = requests.get(
            NICD_POSTS_API,
            params={
                "per_page": limit,
                "_fields": "title,link,date,excerpt",
            },
            headers=HEADERS,
            timeout=60,
        )
        if response.status_code != 200:
            return []
        posts = response.json()
        return [
            {
                "title": p["title"]["rendered"],
                "url": p["link"],
                "date": p["date"],
            }
            for p in posts
        ]
    except Exception as exc:
        log.warning("NICD posts API failed: %s", exc)
        return []


def _pdf_urls_from_post(url: str) -> list[str]:
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code != 200:
            return []
        return re.findall(
            r'href="(https://www\.nicd\.ac\.za/wp-content/uploads/[^"]+\.pdf)"',
            response.text,
            re.IGNORECASE,
        )
    except Exception as exc:
        log.debug("NICD post fetch %s: %s", url, exc)
        return []


def _parse_measles_sitrep_pdf(pdf_bytes: bytes) -> dict[str, Any]:
    text = extract_pdf_text(pdf_bytes, max_pages=12)
    result: dict[str, Any] = {}

    week = re.search(r"ISO Weeks? 1-(\d+)", text, re.IGNORECASE)
    if week:
        result["report_week"] = int(week.group(1))

    measles = re.search(
        r"(\d[\d,]*)\s+laboratory-\s*confirmed measles cases were reported nationally",
        text,
        re.IGNORECASE,
    )
    if measles:
        result["measles_confirmed_ytd"] = int(measles.group(1).replace(",", ""))

    new_cases = re.search(
        r"ISO week \d+,\s*(\d[\d,]*)\s+additional cases were identified",
        text,
        re.IGNORECASE,
    )
    if not new_cases:
        new_cases = re.search(
            r"(\d[\d,]*)\s+additional cases were identified",
            text,
            re.IGNORECASE,
        )
    if new_cases:
        result["measles_new_since_prior_report"] = int(
            new_cases.group(1).replace(",", "")
        )

    rubella = re.search(
        r"total of (\d[\d,]*)\s+laboratory-confirmed rube",
        text,
        re.IGNORECASE,
    )
    if rubella:
        result["rubella_confirmed_ytd"] = int(rubella.group(1).replace(",", ""))

    prov = re.search(
        r"The (Western Cape|Gauteng|KwaZulu-Natal|Eastern Cape|Limpopo|Mpumalanga|North West|Free State|Northern Cape) reported the highest",
        text,
        re.IGNORECASE,
    )
    if prov:
        result["top_province_measles"] = prov.group(1)

    period = re.search(
        r"29 December 2025 to 12 July 2026, ISO\*? Weeks 1-(\d+)",
        text,
        re.IGNORECASE,
    )
    if period:
        result["report_period"] = f"ISO Weeks 1-{period.group(1)} 2026"

    return result


def fetch_nicd_surveillance() -> dict[str, Any] | None:
    posts = _fetch_recent_posts(limit=6)
    if not posts:
        return None

    surveillance: dict[str, Any] = {
        "latest_reports": posts,
        "ingestion_source": "NICD WordPress API",
    }

    for post in posts:
        title_lower = post["title"].lower()
        if "measles" not in title_lower and "rubella" not in title_lower:
            continue
        pdfs = _pdf_urls_from_post(post["url"])
        if not pdfs:
            continue
        pdf_url = pdfs[0]
        post["pdf_url"] = pdf_url
        pdf_bytes = download_bytes(pdf_url, timeout=45)
        if pdf_bytes and pdf_bytes.startswith(b"%PDF"):
            parsed = _parse_measles_sitrep_pdf(pdf_bytes)
            surveillance.update(parsed)
            surveillance["sitrep_pdf_url"] = pdf_url
            log.info(
                "NICD measles sitrep parsed: YTD=%s week=%s",
                parsed.get("measles_confirmed_ytd"),
                parsed.get("report_week"),
            )
            break

    return surveillance if len(surveillance) > 1 else {"latest_reports": posts}
