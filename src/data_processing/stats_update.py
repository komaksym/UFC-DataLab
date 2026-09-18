from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .stats_processing import ensure_fight_outcome


LEGACY_FIGHT_IDENTITY_COLUMNS = [
    "red_fighter_name",
    "blue_fighter_name",
    "event_date",
    "event_name",
    "method",
    "round",
    "time",
]
FIGHT_IDENTITY_COLUMNS = LEGACY_FIGHT_IDENTITY_COLUMNS
_AUDIT_COLUMNS = {
    "identity_status",
    "record_state",
    "identity_conflict_code",
    "observation_source",
    "observation_order",
}


@dataclass(frozen=True)
class IncrementalMergeResult:
    """Auditable result of reconciling existing and incremental fight observations."""

    merged: pd.DataFrame
    raw_observations: pd.DataFrame
    quarantine: pd.DataFrame


def _identity_missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() in {"", "-"}
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _require_incremental_fight_ids(incremental: pd.DataFrame) -> None:
    if "fight_id" not in incremental.columns:
        if not incremental.empty:
            raise ValueError("New incremental UFCStats observations require fight_id")
        return

    if incremental["fight_id"].map(_identity_missing).any():
        raise ValueError("New incremental UFCStats observations require fight_id")


def _fingerprint(row: pd.Series, columns: list[str]) -> tuple[str, ...]:
    values: list[str] = []
    for column in columns:
        value = row.get(column)
        if _identity_missing(value):
            values.append("<NA>")
        else:
            values.append(str(value))
    return tuple(values)


def _sorted(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty or "event_date" not in frame.columns:
        return frame.reset_index(drop=True)

    frame = frame.copy()
    frame["_event_date_sort"] = pd.to_datetime(
        frame["event_date"], dayfirst=True, errors="raise"
    )
    sort_columns = [
        column
        for column in (
            "_event_date_sort",
            "event_name",
            "red_fighter_name",
            "blue_fighter_name",
            "fight_id",
        )
        if column in frame.columns
    ]
    ascending = [False] + [True] * (len(sort_columns) - 1)
    return (
        frame.sort_values(sort_columns, ascending=ascending, kind="stable")
        .drop(columns="_event_date_sort")
        .reset_index(drop=True)
    )


def merge_incremental_fights(
    existing: pd.DataFrame,
    incremental: pd.DataFrame,
) -> IncrementalMergeResult:
    """Reconcile fight observations with stable UFCStats fight IDs as authority.

    New observations must carry fight_id. Stable-ID rematches remain distinct,
    repeated identical observations coalesce only in the merged view, and every
    conflicting version of one stable ID is retained in raw evidence and quarantine.
    Existing pre-ID history may use the visible legacy fallback key.
    """

    _require_incremental_fight_ids(incremental)

    existing_normalized = ensure_fight_outcome(existing)
    incremental_normalized = ensure_fight_outcome(incremental)

    existing_normalized = existing_normalized.copy()
    incremental_normalized = incremental_normalized.copy()
    existing_normalized["observation_source"] = "existing"
    incremental_normalized["observation_source"] = "incremental"

    raw = pd.concat(
        [incremental_normalized, existing_normalized],
        ignore_index=True,
        sort=False,
    )
    raw["observation_order"] = range(len(raw))
    raw["identity_conflict_code"] = pd.NA

    if raw.empty:
        empty = raw.copy()
        return IncrementalMergeResult(empty, empty, empty)

    stable_mask = ~raw["fight_id"].map(_identity_missing)
    stable = raw.loc[stable_mask].copy()
    legacy = raw.loc[~stable_mask].copy()

    accepted_rows: list[pd.Series] = []
    conflict_indices: list[int] = []
    fingerprint_columns = sorted(
        column for column in raw.columns if column not in _AUDIT_COLUMNS
    )

    for _, group in stable.groupby("fight_id", sort=False, dropna=False):
        fingerprints = {
            _fingerprint(row, fingerprint_columns)
            for _, row in group.iterrows()
        }
        if len(fingerprints) == 1:
            accepted_rows.append(group.iloc[0].copy())
            continue

        conflict_indices.extend(group.index.tolist())

    if conflict_indices:
        raw.loc[conflict_indices, "record_state"] = "quarantined"
        raw.loc[conflict_indices, "identity_conflict_code"] = "FIGHT_ID_CONFLICT"

    if accepted_rows:
        accepted_stable = pd.DataFrame(accepted_rows)
    else:
        accepted_stable = raw.iloc[0:0].copy()

    if legacy.empty:
        accepted_legacy = legacy
    else:
        legacy_subset = [
            column for column in LEGACY_FIGHT_IDENTITY_COLUMNS if column in legacy.columns
        ]
        if legacy_subset:
            accepted_legacy = legacy.drop_duplicates(subset=legacy_subset, keep="first")
        else:
            accepted_legacy = legacy.drop_duplicates(keep="first")

    merged = pd.concat(
        [accepted_stable, accepted_legacy],
        ignore_index=True,
        sort=False,
    )
    merged = merged.drop(
        columns=["observation_source", "observation_order", "identity_conflict_code"],
        errors="ignore",
    )
    quarantine = raw.loc[conflict_indices].copy().reset_index(drop=True)
    raw = raw.reset_index(drop=True)

    return IncrementalMergeResult(
        merged=_sorted(merged),
        raw_observations=raw,
        quarantine=quarantine,
    )
