"""
Property Scraper — FNB Property Barometer + PayProp Rental Index
Source : FNB/Lightstone press releases · PayProp quarterly rental report
Cadence: Monthly (FNB) / Quarterly (PayProp)

Note: Lightstone and PayProp raw data APIs require commercial agreements.
We scrape publicly released figures from press releases and news articles.
"""
import json, logging, re
from pathlib import Path
import requests
from bs4 import BeautifulSoup

from scrapers._common import HEADERS, load_topic_json, save_topic_json, utc_now_iso
from scrapers.sources.finance_sync import read_prime_rate_pct
from scrapers.sources.payprop import fetch_rental_growth_pct
from scrapers.sources.cape_town_arcgis import fetch_cape_town_open_data

log = logging.getLogger(__name__)

FNB_URL = "https://www.fnb.co.za/downloads/property/property-barometer.html"
PAYPROP_URL = "https://payprop.com/rental-index"


def _scrape_page_for_rate(url: str, pattern: str) -> float | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        m = re.search(pattern, r.text, re.IGNORECASE)
        if m:
            return float(m.group(1).replace(",", "."))
    except Exception as e:
        log.debug(f"Property scrape {url}: {e}")
    return None


def fetch(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    cached = load_topic_json(output_dir, "property")

    result = dict(cached)
    result.update({
        "source": "Lightstone · FNB Property Barometer · PayProp · Cape Town Open Data",
        "scraped_at": utc_now_iso(),
        "is_live": False,
    })

    if "national" not in result:
        result["national"] = {}
    if "provinces" not in result:
        result["provinces"] = {}

    ingestion: dict[str, bool | str] = {
        "fnb_barometer": False,
        "payprop": False,
        "inside_airbnb": False,
        "cape_town_open_data": False,
        "csg_dlrrd": False,
    }

    yoy = _scrape_page_for_rate(FNB_URL, r"growth[^\d]*(\d+[.,]\d+)\s*%")
    if yoy:
        result["national"]["yoy_growth_pct"] = yoy
        result["is_live"] = True
        ingestion["fnb_barometer"] = True

    payprop_growth = fetch_rental_growth_pct()
    if payprop_growth is not None:
        ingestion["payprop"] = True
        result["is_live"] = True
        result["national"]["rental_growth_yoy_pct"] = payprop_growth

    prime = read_prime_rate_pct(output_dir)
    if prime is not None:
        result["national"]["prime_rate_pct"] = prime

    cape_town = fetch_cape_town_open_data()
    if cape_town:
        result["cape_town_open"] = cape_town
        ingestion["cape_town_open_data"] = True
        result["is_live"] = True

    result["ingestion"] = ingestion

    if not result.get("national") and not cached:
        raise RuntimeError("Property: no cached property.json")

    save_topic_json(output_dir, "property", result)
    log.info("Property data saved | live=%s ingestion=%s", result["is_live"], ingestion)
    return result


# ─────────────────────────────────────────────────────────────────────────────

"""
Fraud Scraper — SABRIC Annual Report
Source : https://www.sabric.co.za/media-and-news/annual-reports/
Format : PDF (text extraction via pdfplumber)
Cadence: Annual (typically May/June)
"""
import io


def fetch_fraud(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    sabric_pdf_urls = [
        "https://www.sabric.co.za/wp-content/uploads/2025/08/SABRIC_annual-report-2024.pdf",
        "https://www.sabric.co.za/wp-content/uploads/2025/09/CRIME-STATISTICS-REPORT-2024.pdf",
    ]

    pdf_data = None
    pdf_source = None
    for pdf_url in sabric_pdf_urls:
        try:
            response = requests.get(pdf_url, headers=HEADERS, timeout=30)
            if response.status_code == 200 and response.content.startswith(b"%PDF"):
                pdf_data = response.content
                pdf_source = pdf_url
                log.info("SABRIC PDF downloaded: %s", pdf_url)
                break
        except Exception as exc:
            log.debug("SABRIC PDF %s: %s", pdf_url, exc)

    if not pdf_data:
        try:
            response = requests.get(
                "https://www.sabric.co.za/media-and-news/annual-reports/",
                headers=HEADERS,
                timeout=15,
            )
            soup = BeautifulSoup(response.text, "lxml")
            for anchor in soup.find_all("a", href=True):
                href = anchor["href"]
                if "annual-report" in href.lower() and href.endswith(".pdf"):
                    pdf_url = href if href.startswith("http") else "https://www.sabric.co.za" + href
                    pdf_response = requests.get(pdf_url, headers=HEADERS, timeout=30)
                    if pdf_response.status_code == 200:
                        pdf_data = pdf_response.content
                        pdf_source = pdf_url
                        break
        except Exception as exc:
            log.debug("SABRIC index scrape: %s", exc)

    cached = load_topic_json(output_dir, "fraud")
    fraud_parsed = {}
    if pdf_data:
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
                text = "\n".join(p.extract_text() or "" for p in pdf.pages[:20])

            # Extract total losses
            m = re.search(r"R\s*(\d+[\.,]\d*)\s*(billion|bn|million|m)", text, re.IGNORECASE)
            if m:
                val = float(m.group(1).replace(",", "."))
                unit = m.group(2).lower()
                fraud_parsed["total_losses_r_billion"] = val if "bill" in unit else val / 1000

            # Extract SIM swap count
            m2 = re.search(r"sim\s*swap[^\d]*(\d[\d,]+)", text, re.IGNORECASE)
            if m2:
                fraud_parsed["sim_swap_incidents"] = int(m2.group(1).replace(",", ""))

        except Exception as e:
            log.warning(f"PDF parse failed: {e}")

    if not fraud_parsed and not cached:
        raise RuntimeError("Fraud: SABRIC scrape failed and no cached fraud.json")

    result = dict(cached)
    result.update({
        "source": "SABRIC Annual Report",
        "scraped_at": utc_now_iso(),
        "is_live": bool(fraud_parsed),
        "pdf_url": pdf_source or cached.get("pdf_url"),
    })
    if fraud_parsed.get("total_losses_r_billion") is not None:
        result["total_losses_r_billion"] = fraud_parsed["total_losses_r_billion"]
    if fraud_parsed.get("sim_swap_incidents") is not None:
        result["sim_swap_incidents"] = fraud_parsed["sim_swap_incidents"]

    save_topic_json(output_dir, "fraud", result)
    log.info("Fraud data saved | total_losses=R%sB live=%s", result.get("total_losses_r_billion"), result["is_live"])
    return result
