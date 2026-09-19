"""Stable fight identity for normalized UFCStats observations.

Single source for identity semantics used by dataset processing and
incremental updates:

- ``fight_id`` is the primary identity. It is derived from UFCStats
  fight-detail URLs, never from names, event labels, or dates.
- Rows with a stable ``fight_id`` carry ``identity_status=stable``.
- Genuinely pre-ID historical rows without ``fight_id`` carry
  ``identity_status=legacy_fallback`` and remain visibly warning-level.
  New scraped rows must never be silently assigned legacy fallback.
- Identical stable-ID observations may coalesce deterministically while
  remaining visible in raw evidence; conflicting observations sharing a
  stable ID must preserve every version for quarantine.
"""

from __future__ import annotations

import pandas as pd

# Note: SOURCE/STABLE/LEGACY constants intentionally mirror
# src/scraping/ufc_stats/ufcstats_scraping/identity.py. The scraper adapter
# must stay pandas-free, so the small duplication preserves layer separation.
SOURCE_UFCSTATS = "ufcstats"
STABLE_IDENTITY_STATUS = "stable"
LEGACY_FALLBACK_STATUS = "legacy_fallback"

IDENTITY_COLUMNS = [
    "fight_id",
    "event_id",
    "red_fighter_id",
    "blue_fighter_id",
    "fight_url",
    "event_url",
    "red_fighter_url",
    "blue_fighter_url",
    "source",
    "identity_status",
]

# Composite fallback key for genuinely pre-ID legacy rows. Method/round/time
# discriminate same-card rematches (e.g. Sakuraba vs. Silveira twice on UFC
# Ultimate Japan) until stable fight IDs exist.
LEGACY_IDENTITY_COLUMNS = [
    "red_fighter_name",
    "blue_fighter_name",
    "event_date",
    "event_name",
    "method",
    "round",
    "time",
]

_MISSING_TOKENS = {"", "-", "--", "---"}


def is_missing_id_value(value: object) -> bool:
    """Return True for absent or placeholder identifiers."""
    if value is None:
        return True
    try:
        if pd.isna(value):  # type: ignore[call-overload]
            return True
    except Exception:
        pass
    return str(value).strip() in _MISSING_TOKENS


def ensure_identity_status(frame: pd.DataFrame) -> pd.DataFrame:
    """Ensure identity columns exist and assign stable/legacy status.

    Rows with a present ``fight_id`` become ``stable`` unless they already
    carry an explicit status. Rows without ``fight_id`` become
    ``legacy_fallback``. Existing explicit statuses are preserved so new
    scrapes cannot be silently downgraded to legacy.
    """
    frame = frame.copy()
    for column in IDENTITY_COLUMNS:
        if column not in frame.columns:
            frame[column] = pd.NA

    def _status(row: pd.Series) -> str:
        """Derive stable/legacy status for one row, preserving explicit values."""
        current = row.get("identity_status")
        if not is_missing_id_value(current):
            return str(current).strip()
        if is_missing_id_value(row.get("fight_id")):
            return LEGACY_FALLBACK_STATUS
        return STABLE_IDENTITY_STATUS

    frame["identity_status"] = frame.apply(_status, axis=1)

    # Default provenance for stable rows that lack an explicit source.
    needs_source = frame["identity_status"].eq(STABLE_IDENTITY_STATUS) & frame["source"].apply(
        is_missing_id_value
    )
    frame.loc[needs_source, "source"] = SOURCE_UFCSTATS
    return frame


def validate_new_records_have_ids(frame: pd.DataFrame) -> None:
    """Reject newly scraped rows without a stable ``fight_id``.

    ``identity_status=legacy_fallback`` is reserved for genuinely pre-ID
    historical records and must never silently authorize a new row.
    """
    if "fight_id" not in frame.columns:
        if len(frame) == 0:
            return
        raise ValueError(
            "Hard identity failure: newly scraped records lack a fight_id column. "
            f"{LEGACY_FALLBACK_STATUS} is reserved for genuinely pre-ID history."
        )
    missing = frame[frame["fight_id"].apply(is_missing_id_value)]
    if not missing.empty:
        urls = missing.get("fight_url", pd.Series(["?"] * len(missing))).tolist()[:3]
        raise ValueError(
            "Hard identity failure: newly scraped record without fight_id "
            f"(examples fight_url={urls!r}). {LEGACY_FALLBACK_STATUS} is reserved "
            "for genuinely pre-ID historical records."
        )
    if "identity_status" in frame.columns:
        smuggled = frame[frame["identity_status"].astype(str).str.strip() == LEGACY_FALLBACK_STATUS]
        if not smuggled.empty:
            raise ValueError(
                "Hard identity failure: newly scraped records must not carry "
                f"{LEGACY_FALLBACK_STATUS} even with a fight_id. It is reserved "
                "for genuinely pre-ID historical records."
            )


def stable_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Return only rows carrying a stable ``fight_id``."""
    if "fight_id" not in frame.columns:
        return frame.iloc[0:0].copy()
    return frame[~frame["fight_id"].apply(is_missing_id_value)].copy()


def legacy_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Return only rows without a stable ``fight_id`` (pre-ID history)."""
    if "fight_id" not in frame.columns:
        return frame.copy()
    return frame[frame["fight_id"].apply(is_missing_id_value)].copy()


def find_duplicate_fight_ids(frame: pd.DataFrame) -> list[str]:
    """Return stable ``fight_id`` values observed more than once, sorted."""
    if "fight_id" not in frame.columns or frame.empty:
        return []
    stable = stable_frame(frame)
    if stable.empty:
        return []
    dup_mask = stable["fight_id"].astype(str).duplicated(keep=False)
    return sorted(str(value) for value in stable.loc[dup_mask, "fight_id"].astype(str).unique())


def _normalized_for_compare(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize a frame for identical/conflicting comparison."""
    norm = frame.copy()
    # Normalize NaN/None/placeholders so identical source rows compare equal
    # while genuine value differences remain visible.
    for column in norm.columns:
        norm[column] = norm[column].apply(
            lambda value: "__MISSING__" if is_missing_id_value(value) and column in IDENTITY_COLUMNS else value
        )
    # pandas duplicated treats NaN as equal, but normalize anyway for stability.
    return norm.fillna("__NA__").astype(str)


def find_conflicting_fight_ids(frame: pd.DataFrame) -> set[str]:
    """Return stable ``fight_id`` values with conflicting observations.

    A stable ID with multiple identical rows is a deterministic duplicate and
    is not conflicting. A stable ID with two or more distinct row signatures
    is conflicting and every version must be preserved for quarantine.
    """
    conflicts: set[str] = set()
    if "fight_id" not in frame.columns or frame.empty:
        return conflicts
    for fight_id, group in stable_frame(frame).groupby("fight_id", sort=False):
        if len(group) <= 1:
            continue
        distinct = _normalized_for_compare(group).drop_duplicates()
        if len(distinct) > 1:
            conflicts.add(str(fight_id))
    return conflicts


def dedupe_stable_on_fight_id(frame: pd.DataFrame) -> pd.DataFrame:
    """Coalesce identical stable-ID duplicates; preserve conflicts.

    Identical observations (all columns equal after normalization) keep a
    single deterministic survivor. Conflicting observations keep every
    version so quarantine can inspect each one. Raw evidence remains in the
    caller inputs; this only determines the trusted merged view.
    """
    if "fight_id" not in frame.columns or frame.empty:
        return frame.copy()
    parts: list[pd.DataFrame] = []
    for _, group in stable_frame(frame).groupby("fight_id", sort=False):
        if len(group) == 1:
            parts.append(group)
            continue
        norm = _normalized_for_compare(group)
        # Deterministic survivor: sort by the normalized signature and keep first.
        order = norm.apply(lambda row: "|".join(row.values), axis=1).sort_values(kind="stable").index
        ordered = group.loc[order]
        distinct = norm.loc[order].drop_duplicates()
        if len(distinct) == 1:
            parts.append(ordered.iloc[[0]])
        else:
            parts.append(ordered)
    if not parts:
        return frame.iloc[0:0].copy()
    return pd.concat(parts, ignore_index=False)
