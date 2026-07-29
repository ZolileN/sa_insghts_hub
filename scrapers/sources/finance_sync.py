"""Read cached finance.json for cross-topic sync (e.g. property prime rate)."""

from __future__ import annotations

import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)


def read_prime_rate_pct(output_dir: Path) -> float | None:
    path = output_dir / "finance.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        prime = data.get("prime_rate_pct")
        if prime is not None:
            return float(prime)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        log.debug("finance.json read failed: %s", exc)
    return None
