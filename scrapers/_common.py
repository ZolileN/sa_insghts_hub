"""Shared helpers for Libo Insights data scrapers."""

from __future__ import annotations

import io
import json
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Libo-Insights/1.0; public-data-research)",
    "Accept": "text/html,application/pdf,application/json,*/*",
}

STATSSA_PUBLICATIONS = "https://www.statssa.gov.za/publications"

TOPIC_FILES = {
    "crime": "crime.json",
    "forex": "forex.json",
    "water": "water.json",
    "finance": "finance.json",
    "energy": "energy.json",
    "employment": "employment.json",
    "health": "health.json",
    "education": "education.json",
    "property": "property.json",
    "fraud": "fraud.json",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def topic_path(output_dir: Path, topic: str) -> Path:
    filename = TOPIC_FILES.get(topic, f"{topic}.json")
    return output_dir / filename


def load_topic_json(output_dir: Path, topic: str) -> dict:
    """Load the last committed JSON for a topic (production cache)."""
    path = topic_path(output_dir, topic)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        log.warning("Could not parse cached %s", path)
        return {}


def save_topic_json(output_dir: Path, topic: str, data: dict) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = topic_path(output_dir, topic)
    path.write_text(json.dumps(data, indent=2))
    return path


def merge_preserve(
    cached: dict,
    updates: dict,
    preserve_keys: tuple[str, ...] = (),
) -> dict:
    """Apply updates; keep cached subtrees when updates omit or empty them."""
    merged = dict(cached)
    for key, value in updates.items():
        if key in preserve_keys and not value:
            continue
        merged[key] = value
    return merged


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
