"""Incremental-update identity fixtures: stable IDs, legacy, duplicates."""

import pandas as pd
import pytest

from src.data_processing.identity import (
    LEGACY_FALLBACK_STATUS,
    STABLE_IDENTITY_STATUS,
    dedupe_stable_on_fight_id,
    ensure_identity_status,
    find_conflicting_fight_ids,
    find_duplicate_fight_ids,
    validate_new_records_have_ids,
)


def _row(fight_id: object, method: str = "U-DEC", extra: dict | None = None) -> dict:
    row = {
        "fight_id": fight_id,
        "event_id": "ev-1",
        "red_fighter_id": "red-1",
        "blue_fighter_id": "blue-1",
        "method": method,
    }
    if extra:
        row.update(extra)
    return row


def test_ensure_identity_status_assigns_stable_and_legacy() -> None:
    """Stable rows become stable; pre-ID rows become visibly legacy_fallback."""
    frame = pd.DataFrame([_row("stable-1"), _row(None), _row("-")])
    out = ensure_identity_status(frame)

    assert out.loc[0, "identity_status"] == STABLE_IDENTITY_STATUS
    assert out.loc[1, "identity_status"] == LEGACY_FALLBACK_STATUS
    assert out.loc[2, "identity_status"] == LEGACY_FALLBACK_STATUS


def test_ensure_identity_status_preserves_explicit_status() -> None:
    """Explicit statuses are never silently overwritten."""
    frame = pd.DataFrame([_row("stable-1", extra={"identity_status": "stable"})])
    out = ensure_identity_status(frame)
    assert out.loc[0, "identity_status"] == "stable"


def test_validate_new_records_rejects_missing_ids() -> None:
    """New scrapes without fight_id are hard identity failures."""
    frame = pd.DataFrame([_row(None)])
    with pytest.raises(ValueError, match="Hard identity failure"):
        validate_new_records_have_ids(frame)


def test_validate_new_records_rejects_missing_column() -> None:
    """A missing fight_id column is also a hard failure for new data."""
    frame = pd.DataFrame([{"method": "U-DEC"}])
    with pytest.raises(ValueError, match="Hard identity failure"):
        validate_new_records_have_ids(frame)


def test_validate_new_records_rejects_smuggled_legacy_status() -> None:
    """Incremental rows must not carry legacy_fallback even with a fight_id."""
    frame = pd.DataFrame([_row("stable-1", extra={"identity_status": "legacy_fallback"})])
    with pytest.raises(ValueError, match="must not carry.*legacy_fallback"):
        validate_new_records_have_ids(frame)


def test_find_duplicate_and_conflicting_ids() -> None:
    """Identical duplicates are not conflicts; differing rows are."""
    identical = pd.DataFrame([_row("dup-1"), _row("dup-1")])
    assert find_duplicate_fight_ids(identical) == ["dup-1"]
    assert find_conflicting_fight_ids(identical) == set()

    conflicting = pd.DataFrame([_row("c-1", method="U-DEC"), _row("c-1", method="KO/TKO")])
    assert find_conflicting_fight_ids(conflicting) == {"c-1"}


def test_dedupe_coalesces_identical_and_preserves_conflicts() -> None:
    """Identical stable observations coalesce; conflicts keep every version."""
    identical = pd.DataFrame([_row("dup-1"), _row("dup-1")])
    assert len(dedupe_stable_on_fight_id(identical)) == 1

    conflicting = pd.DataFrame([_row("c-1", method="U-DEC"), _row("c-1", method="KO/TKO")])
    deduped = dedupe_stable_on_fight_id(conflicting)
    assert len(deduped) == 2
    assert set(deduped["method"]) == {"U-DEC", "KO/TKO"}


def test_rematches_with_distinct_ids_are_not_duplicates() -> None:
    """Same fighters on the same card stay separate when fight_ids differ."""
    frame = pd.DataFrame([_row("rematch-1"), _row("rematch-2")])
    assert find_duplicate_fight_ids(frame) == []
    assert len(dedupe_stable_on_fight_id(frame)) == 2
