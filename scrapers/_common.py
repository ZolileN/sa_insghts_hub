"""Shared helpers for Libo Insights data scrapers."""

from __future__ import annotations

import io
import logging
import re
import time
from datetime import datetime, timezone

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Libo-Insights/1.0; public-data-research)",
    "Accept": "text/html,application/pdf,application/json,*/*",
}

STATSSA_PUBLICATIONS = "https://www.statssa.gov.za/publications"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def download_bytes(
    url: str,
    timeout: int = 120,
    verify: bool = True,
    retries: int = 3,
) -> bytes | None:
    for attempt in range(retries):
        try:
            with requests.get(
                url,
                headers=HEADERS,
                timeout=timeout,
                verify=verify,
                stream=True,
            ) as response:
                response.raise_for_status()
                chunks: list[bytes] = []
                for chunk in response.iter_content(chunk_size=65536):
                    if chunk:
                        chunks.append(chunk)
                return b"".join(chunks)
        except Exception as exc:
            log.warning("Download attempt %s failed for %s: %s", attempt + 1, url, exc)
            time.sleep(2 ** attempt)
    return None


def fetch_statssa_pdf(publication: str, filename: str) -> bytes | None:
    url = f"{STATSSA_PUBLICATIONS}/{publication}/{filename}"
    return download_bytes(url, timeout=90)


def extract_pdf_text(pdf_bytes: bytes, max_pages: int = 40) -> str:
    import pdfplumber

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        return "\n".join((page.extract_text() or "") for page in pdf.pages[:max_pages])


def parse_sa_decimal(text: str) -> float:
    return float(text.replace(",", ".").strip())


def find_first_percent(text: str, pattern: str) -> float | None:
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return parse_sa_decimal(match.group(1))


def get_json(
    url: str,
    timeout: int = 30,
    verify: bool = True,
) -> dict | list | None:
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            verify=verify,
        )
        if response.status_code == 200:
            return response.json()
    except Exception as exc:
        log.debug("get_json %s: %s", url, exc)
    return None
