"""Stable UFCStats identity helpers for the stats source adapter.

Derives source identifiers from the UFCStats links already present in event
and fight pages. Stable identity is never derived from normalized names,
event labels, or dates.
"""

from __future__ import annotations

import re
from typing import Optional


SOURCE_UFCSTATS = "ufcstats"
STABLE_IDENTITY_STATUS = "stable"
LEGACY_FALLBACK_STATUS = "legacy_fallback"

# Note: these constants intentionally mirror src/data_processing/identity.py.
# The source adapter must stay pandas-free, so the small duplication keeps
# layers separated instead of forcing a cross-layer import.

_MISSING_TOKENS = {"", "-", "--", "---"}

# Fight/event/fighter detail URL patterns, e.g.:
#   http://ufcstats.com/fight-details/b35e47f2f58ef026
#   http://ufcstats.com/event-details/daff32bc96d1eabf
#   http://ufcstats.com/fighter-details/07f72a2a7591b409
_ID_PATTERNS = {
    "fight": re.compile(r"/fight-details/([^/?#\s]+)"),
    "event": re.compile(r"/event-details/([^/?#\s]+)"),
    "fighter": re.compile(r"/fighter-details/([^/?#\s]+)"),
}


def is_missing_id(value: object) -> bool:
    """Return True when a source identifier is absent or a placeholder."""
    if value is None:
        return True
    # NaN check without importing pandas at the adapter boundary.
    try:
        import math

        if isinstance(value, float) and math.isnan(value):
            return True
    except Exception:
        pass
    text = str(value).strip()
    return text in _MISSING_TOKENS


def extract_ufcstats_id(url: Optional[object], kind: str) -> Optional[str]:
    """Extract a UFCStats identifier from a detail URL.

    Args:
        url: Source URL such as ``http://ufcstats.com/fight-details/<id>``.
        kind: One of ``"fight"``, ``"event"``, or ``"fighter"``.

    Returns:
        The identifier string, or None when the URL is missing or does not
        contain the expected ``<kind>-details/<id>`` segment.
    """
    pattern = _ID_PATTERNS.get(kind)
    if pattern is None:
        raise ValueError(f"Unsupported UFCStats id kind: {kind}")
    if url is None:
        return None
    text = str(url).strip()
    if not text:
        return None
    match = pattern.search(text)
    if not match:
        return None
    candidate = match.group(1).strip().rstrip("/")
    if candidate in _MISSING_TOKENS:
        return None
    return candidate or None


def normalize_id_value(value: object) -> Optional[str]:
    """Strip an identifier and map placeholders to None."""
    if is_missing_id(value):
        return None
    text = str(value).strip()
    return text or None
