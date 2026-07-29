"""Parse Stats SA QLFS provincial unemployment table from PDF text."""

from __future__ import annotations

import re

PROVINCES = [
    "Western Cape",
    "Eastern Cape",
    "Northern Cape",
    "Free State",
    "KwaZulu-Natal",
    "North West",
    "Gauteng",
    "Mpumalanga",
    "Limpopo",
]

_PROVINCE_PATTERN = (
    r"(?P<name>"
    + "|".join(re.escape(p) for p in PROVINCES)
    + r")\s+"
    r"(?P<unemp>\d+,\d)\s+\d+,\d\s+(?P<unemp_q>\d+,\d)\s+"
    r"[\d,\.\s]+"
    r"(?P<expanded>\d+,\d)\s+\d+,\d\s+(?P<expanded_q>\d+,\d)"
)


def _sa_float(token: str) -> float:
    return float(token.replace(",", "."))


def parse_provincial_qlfs_table(text: str) -> dict[str, dict[str, float]]:
    """
  Parse Table E style rows, e.g.
  Western Cape 19,6 18,1 19,6 ... 24,8 23,7 24,8 ...
    """
    result: dict[str, dict[str, float]] = {}
    for match in re.finditer(_PROVINCE_PATTERN, text):
        name = match.group("name")
        result[name] = {
            "unemployment": _sa_float(match.group("unemp_q")),
            "expanded_unemployment": _sa_float(match.group("expanded_q")),
        }
    return result
