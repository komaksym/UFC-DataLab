from __future__ import annotations

import pandas as pd

from .identity import (
    LEGACY_FALLBACK_STATUS,
    LEGACY_IDENTITY_COLUMNS,
    dedupe_stable_on_fight_id,
    ensure_identity_status,
    find_conflicting_fight_ids,
    legacy_frame,
    stable_frame,
    validate_new_records_have_ids,
)
from .stats_processing import ensure_fight_outcome


# Legacy composite key for pre-ID rows. Fighter pair/event/date alone cannot
# discriminate same-card rematches, so method/round/time are included.
FIGHT_IDENTITY_COLUMNS = LEGACY_IDENTITY_COLUMNS


def merge_incremental_fights(
    existing: pd.DataFrame,
    incremental: pd.DataFrame,
) -> pd.DataFrame:
    """Merge newly scraped fights on stable ``fight_id``.

    Stable identity is authoritative:

    - ``fight_id`` is the primary dedupe key. Merging is idempotent: rerunning
      the same incremental input does not create duplicates.
    - Same-card rematches have distinct ``fight_id`` values and are preserved.
    - Identical stable-ID observations coalesce to one deterministic survivor
      (raw inputs remain the evidence); conflicting observations sharing a
      stable ID preserve every version for quarantine.
    - Newly scraped rows without ``fight_id`` are a hard identity failure.
      ``legacy_fallback`` is reserved for genuinely pre-ID historical rows in
      ``existing`` and stays visible via ``identity_status``.
    """

    if incremental is not None and not incremental.empty:
        validate_new_records_have_ids(incremental)

    def _normalize(frame: pd.DataFrame | None) -> pd.DataFrame:
        """Normalize outcomes and identity for one merge input."""
        if frame is None or frame.empty:
            return pd.DataFrame()
        return ensure_identity_status(ensure_fight_outcome(frame))

    existing_norm = _normalize(existing)
    incremental_norm = _normalize(incremental)

    # Split stable vs legacy. Incremental must be stable (validated above);
    # existing may contain pre-ID legacy rows.
    existing_stable = stable_frame(existing_norm) if not existing_norm.empty else pd.DataFrame()
    existing_legacy = legacy_frame(existing_norm) if not existing_norm.empty else pd.DataFrame()
    incremental_stable = stable_frame(incremental_norm) if not incremental_norm.empty else pd.DataFrame()

    # Stable merge: idempotent on fight_id, coalesce identical, keep conflicts.
    if not existing_stable.empty or not incremental_stable.empty:
        combined_stable = pd.concat([incremental_stable, existing_stable], ignore_index=True, sort=False)
        merged_stable = dedupe_stable_on_fight_id(combined_stable)
    else:
        merged_stable = pd.DataFrame()

    # Legacy merge: composite fallback preserving same-card rematches.
    if not existing_legacy.empty:
        legacy_combined = existing_legacy.copy()
        # Incremental legacy should not happen (validated), but keep existing
        # legacy deduped for repeatability.
        legacy_combined = legacy_combined.drop_duplicates(subset=FIGHT_IDENTITY_COLUMNS, keep="first")
        # Ensure legacy rows stay visibly warning-level.
        legacy_combined["identity_status"] = LEGACY_FALLBACK_STATUS
    else:
        legacy_combined = pd.DataFrame()

    if not merged_stable.empty and not legacy_combined.empty:
        combined = pd.concat([merged_stable, legacy_combined], ignore_index=True, sort=False)
    elif not merged_stable.empty:
        combined = merged_stable
    elif not legacy_combined.empty:
        combined = legacy_combined
    else:
        all_columns = list(existing_norm.columns) if not existing_norm.empty else list(incremental_norm.columns)
        return pd.DataFrame(columns=all_columns)

    combined["_event_date_sort"] = pd.to_datetime(
        combined["event_date"], dayfirst=True, errors="raise"
    )
    # Deterministic order: newest events first, then stable fight_id to keep
    # rematches and conflicts in a repeatable sequence.
    sort_keys = ["_event_date_sort", "event_name", "red_fighter_name", "blue_fighter_name"]
    if "fight_id" in combined.columns:
        sort_keys.append("fight_id")
    combined = combined.sort_values(
        sort_keys,
        ascending=[False, True, True, True] + [True] * (len(sort_keys) - 4),
        kind="stable",
    ).drop(columns="_event_date_sort")
    combined = ensure_identity_status(combined)
    return combined.reset_index(drop=True)


__all__ = [
    "FIGHT_IDENTITY_COLUMNS",
    "find_conflicting_fight_ids",
    "merge_incremental_fights",
]
