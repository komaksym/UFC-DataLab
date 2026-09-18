import pandas as pd
import pytest

from src.data_processing.stats_update import merge_incremental_fights


def _fight(
    fight_id: object,
    *,
    red: str = "KAZUSHI SAKURABA",
    blue: str = "MARCUS SILVEIRA",
    red_result: str = "W",
    blue_result: str = "L",
    method: str = "Submission",
    time: str = "3:44",
) -> dict[str, object]:
    suffix = str(fight_id) if fight_id is not None else "legacy"
    return {
        "fight_id": fight_id,
        "event_id": "event-1997",
        "red_fighter_id": f"red-{suffix}",
        "blue_fighter_id": f"blue-{suffix}",
        "fight_url": f"http://ufcstats.com/fight-details/{suffix}",
        "event_url": "http://ufcstats.com/event-details/event-1997",
        "red_fighter_url": f"http://ufcstats.com/fighter-details/red-{suffix}",
        "blue_fighter_url": f"http://ufcstats.com/fighter-details/blue-{suffix}",
        "corner_orientation": "red_blue",
        "source_provenance": "ufcstats" if fight_id is not None else pd.NA,
        "red_fighter_name": red,
        "blue_fighter_name": blue,
        "event_date": "21/12/1997",
        "event_name": "UFC - Ultimate Japan",
        "red_fighter_result": red_result,
        "blue_fighter_result": blue_result,
        "method": method,
        "round": "1",
        "time": time,
    }


def test_new_incremental_observation_without_fight_id_is_hard_failure() -> None:
    incremental = pd.DataFrame([_fight(None)])

    with pytest.raises(ValueError, match="require fight_id"):
        merge_incremental_fights(pd.DataFrame(), incremental)


def test_stable_fight_id_preserves_same_card_rematches_and_repeated_input() -> None:
    first = _fight("fight-a", method="Submission", time="3:44")
    rematch = _fight("fight-b", method="Submission", time="3:44")

    initial = merge_incremental_fights(pd.DataFrame(), pd.DataFrame([first, rematch]))
    repeated = merge_incremental_fights(initial.merged, pd.DataFrame([first, rematch]))

    assert initial.merged["fight_id"].tolist() == ["fight-a", "fight-b"]
    assert repeated.merged["fight_id"].tolist() == ["fight-a", "fight-b"]
    assert len(repeated.raw_observations) == 4
    assert repeated.quarantine.empty


def test_identical_stable_id_observations_coalesce_but_remain_raw_visible() -> None:
    fight = _fight("fight-a")
    result = merge_incremental_fights(
        pd.DataFrame([fight]),
        pd.DataFrame([fight, fight]),
    )

    assert result.merged["fight_id"].tolist() == ["fight-a"]
    assert len(result.raw_observations) == 3
    assert result.quarantine.empty


def test_conflicting_stable_id_observations_preserve_and_quarantine_every_version() -> None:
    original = _fight("fight-a", red_result="W", blue_result="L")
    conflicting = _fight("fight-a", red_result="L", blue_result="W")

    result = merge_incremental_fights(
        pd.DataFrame([original]),
        pd.DataFrame([conflicting]),
    )

    assert result.merged.empty
    assert len(result.raw_observations) == 2
    assert len(result.quarantine) == 2
    assert set(result.quarantine["record_state"]) == {"quarantined"}
    assert set(result.quarantine["identity_conflict_code"]) == {"FIGHT_ID_CONFLICT"}
    assert set(result.quarantine["fight_outcome"]) == {"red_win", "blue_win"}


def test_pre_id_existing_row_uses_visible_legacy_fallback_warning() -> None:
    legacy = _fight(None)
    legacy.pop("fight_id")

    result = merge_incremental_fights(pd.DataFrame([legacy]), pd.DataFrame())

    assert len(result.merged) == 1
    assert result.merged.loc[0, "identity_status"] == "legacy_fallback"
    assert result.merged.loc[0, "record_state"] == "warning"
    assert result.merged.loc[0, "source_provenance"] == "legacy_historical"
    assert pd.isna(result.merged.loc[0, "fight_id"])
