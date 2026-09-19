import pandas as pd
import pytest

from src.data_processing.identity import find_conflicting_fight_ids
from src.data_processing.stats_update import merge_incremental_fights


def _fight(
    method: str,
    round_: str,
    time: str,
    fight_id: str | None = None,
    **overrides: object,
) -> dict[str, object]:
    row: dict[str, object] = {
        "red_fighter_name": "KAZUSHI SAKURABA",
        "blue_fighter_name": "MARCUS SILVEIRA",
        "event_date": "21/12/1997",
        "event_name": "UFC - Ultimate Japan",
        "red_fighter_result": "NC" if method == "Overturned" else "W",
        "blue_fighter_result": "NC" if method == "Overturned" else "L",
        "method": method,
        "round": round_,
        "time": time,
    }
    if fight_id is not None:
        row.update(
            {
                "fight_id": fight_id,
                "event_id": "ev-ultimate-japan",
                "red_fighter_id": "sakuraba-id",
                "blue_fighter_id": "silveira-id",
                "fight_url": f"http://ufcstats.com/fight-details/{fight_id}",
                "event_url": "http://ufcstats.com/event-details/ev-ultimate-japan",
                "source": "ufcstats",
            }
        )
    row.update(overrides)
    return row


def test_merge_incremental_fights_preserves_same_event_rematch() -> None:
    no_contest = _fight("Overturned", "1", "1:51", fight_id="fight-nc-1")
    rematch = _fight("Submission", "1", "3:44", fight_id="fight-rematch-2")

    existing = pd.DataFrame([no_contest, rematch])
    incremental = pd.DataFrame([rematch])

    merged = merge_incremental_fights(existing, incremental)

    assert len(merged) == 2
    assert set(merged["fight_outcome"]) == {"no_contest", "red_win"}
    assert set(merged["method"]) == {"Overturned", "Submission"}
    # Same-card rematches keep distinct stable IDs.
    assert set(merged["fight_id"]) == {"fight-nc-1", "fight-rematch-2"}
    assert set(merged["identity_status"]) == {"stable"}


def test_merge_is_idempotent_on_stable_fight_id() -> None:
    fight = _fight("Submission", "1", "3:44", fight_id="stable-1")
    existing = pd.DataFrame([fight])
    incremental = pd.DataFrame([fight])

    merged_once = merge_incremental_fights(existing, incremental)
    merged_twice = merge_incremental_fights(merged_once, incremental)

    assert len(merged_once) == 1
    assert len(merged_twice) == 1
    assert merged_twice.iloc[0]["fight_id"] == "stable-1"


def test_merge_repeated_incremental_input_does_not_duplicate() -> None:
    fight = _fight("KO/TKO", "2", "1:00", fight_id="repeat-1")
    existing = pd.DataFrame([fight])
    incremental = pd.DataFrame([fight, fight])

    merged = merge_incremental_fights(existing, incremental)

    assert len(merged) == 1
    assert merged.iloc[0]["fight_id"] == "repeat-1"


def test_merge_identical_duplicates_coalesce_deterministically() -> None:
    fight = _fight("Submission", "1", "3:44", fight_id="dup-1")
    existing = pd.DataFrame([fight])
    incremental = pd.DataFrame([dict(fight), dict(fight)])

    merged = merge_incremental_fights(existing, incremental)

    assert len(merged) == 1
    assert merged.iloc[0]["identity_status"] == "stable"


def test_merge_conflicting_duplicates_preserve_every_version() -> None:
    base = _fight("Submission", "1", "3:44", fight_id="conflict-1")
    altered = dict(base)
    altered["method"] = "KO/TKO"

    existing = pd.DataFrame([base])
    incremental = pd.DataFrame([altered])

    merged = merge_incremental_fights(existing, incremental)

    # Conflicting observations sharing a stable ID preserve every version for
    # quarantine instead of silently collapsing.
    assert len(merged) == 2
    assert set(merged["fight_id"]) == {"conflict-1"}
    assert set(merged["method"]) == {"Submission", "KO/TKO"}
    assert find_conflicting_fight_ids(merged) == {"conflict-1"}


def test_merge_rejects_incremental_missing_fight_id() -> None:
    legacy_row = _fight("Submission", "1", "3:44")
    existing = pd.DataFrame([_fight("Submission", "1", "3:44", fight_id="stable-1")])
    incremental = pd.DataFrame([legacy_row])

    with pytest.raises(ValueError, match="Hard identity failure.*fight_id"):
        merge_incremental_fights(existing, incremental)


def test_merge_marks_pre_id_legacy_rows_warning_visible() -> None:
    legacy_nc = _fight("Overturned", "1", "1:51")
    legacy_rematch = _fight("Submission", "1", "3:44")
    new_fight = _fight("KO/TKO", "1", "0:30", fight_id="new-stable-1")

    existing = pd.DataFrame([legacy_nc, legacy_rematch])
    incremental = pd.DataFrame([new_fight])

    merged = merge_incremental_fights(existing, incremental)

    assert len(merged) == 3
    legacy = merged[merged["fight_id"].isna() | (merged["fight_id"].astype(str).isin(["-", "--", "---"]))]
    # Legacy rows without stable IDs stay visibly warning-level.
    assert set(legacy["identity_status"]) == {"legacy_fallback"}
    assert set(merged[merged["fight_id"] == "new-stable-1"]["identity_status"]) == {"stable"}
    # Legacy same-card rematch still discriminated by method/round/time.
    assert set(legacy["method"]) == {"Overturned", "Submission"}
