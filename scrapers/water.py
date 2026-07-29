"""
DWS Dam Levels Scraper
------------------------
Source  : https://www.dws.gov.za/Hydrology/Weekly/Province.aspx
PDF     : https://www.dws.gov.za/Hydrology/Weekly/Weekly.pdf
Cadence : Weekly (Mondays)
Notes   : DWS may block non-SA IPs — last successful scrape stays in cache.
"""

import logging
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from scrapers._common import (
    HEADERS,
    load_topic_json,
    save_topic_json,
    utc_now_iso,
)

log = logging.getLogger(__name__)

HTML_URL = "https://www.dws.gov.za/Hydrology/Weekly/Province.aspx"
PDF_URL = "https://www.dws.gov.za/Hydrology/Weekly/Weekly.pdf"

PROVINCE_MAP = {
    "western cape": "Western Cape",
    "eastern cape": "Eastern Cape",
    "kwazulu-natal": "KwaZulu-Natal",
    "kwa-zulu natal": "KwaZulu-Natal",
    "gauteng": "Gauteng",
    "limpopo": "Limpopo",
    "mpumalanga": "Mpumalanga",
    "north west": "North West",
    "free state": "Free State",
    "northern cape": "Northern Cape",
}


def _parse_html_table(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    result = {}

    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            if len(cells) < 3:
                continue
            label = cells[0].lower().replace("\xa0", " ").strip()
            prov = PROVINCE_MAP.get(label)
            if not prov:
                continue
            nums = []
            for cell in cells[1:]:
                cell = cell.replace("%", "").replace(",", ".").strip()
                try:
                    nums.append(float(cell))
                except ValueError:
                    pass
            if len(nums) >= 2:
                result[prov] = {
                    "this_week_pct": nums[0],
                    "last_week_pct": nums[1] if len(nums) > 1 else None,
                    "last_year_pct": nums[2] if len(nums) > 2 else None,
                }

    return result


def _parse_individual_dams(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    dams = []
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cells) < 4:
                continue
            name = cells[0].strip()
            if not name or name.lower() in ("name", "dam", "reservoir"):
                continue
            nums = []
            for cell in cells[1:]:
                cell = cell.replace("%", "").replace(",", ".").strip()
                try:
                    nums.append(float(cell))
                except ValueError:
                    pass
            if nums and name and len(name) > 2:
                dams.append({
                    "name": name,
                    "this_week_pct": nums[0] if nums else None,
                    "last_week_pct": nums[1] if len(nums) > 1 else None,
                    "capacity_mm3": nums[2] if len(nums) > 2 else None,
                })
    return dams[:50]


def fetch(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    cached = load_topic_json(output_dir, "water")

    provinces: dict = {}
    dams: list = []
    is_live = False
    report_date = None

    try:
        response = requests.get(HTML_URL, headers=HEADERS, timeout=20)
        response.raise_for_status()

        match = re.search(
            r"(\d{1,2}\s+\w+\s+\d{4}|\d{4}-\d{2}-\d{2})",
            response.text,
        )
        report_date = match.group(1) if match else None

        provinces = _parse_html_table(response.text)
        dams = _parse_individual_dams(response.text)
        is_live = bool(provinces)
        log.info("DWS: parsed %d provinces, %d dams", len(provinces), len(dams))

    except Exception as exc:
        log.error("DWS HTML scrape failed: %s", exc)

    if not provinces:
        if not cached.get("provinces"):
            raise RuntimeError("Water: DWS unreachable and no cached water.json")
        log.warning("DWS unreachable — keeping last successful province/dam data")
        provinces = cached.get("provinces", {})
        dams = cached.get("dams", [])
        report_date = cached.get("report_date")

    pcts = [
        v["this_week_pct"]
        for v in provinces.values()
        if v.get("this_week_pct") is not None
    ]
    national_avg = round(sum(pcts) / len(pcts), 1) if pcts else cached.get("national_avg_pct")

    result = dict(cached)
    result.update({
        "source": "DWS Weekly State of Reservoirs",
        "url": HTML_URL,
        "pdf_url": PDF_URL,
        "scraped_at": utc_now_iso(),
        "report_date": report_date or cached.get("report_date"),
        "is_live": is_live,
        "national_avg_pct": national_avg,
        "provinces": provinces,
        "dams": dams,
    })

    path = save_topic_json(output_dir, "water", result)
    log.info("Dam data saved → %s | national avg = %s%% live=%s", path, national_avg, is_live)
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = fetch(Path("data"))
    print(f"National avg: {data['national_avg_pct']}%")
