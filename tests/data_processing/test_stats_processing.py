from pathlib import Path

import pandas as pd

from src.data_processing.stats_processing import (
    DatasetPaths,
    build_merged_stats_scorecards,
    build_processed_all_bouts,
    build_processed_decisive_only,
    normalize_event_date_value,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_sample_raw_stats() -> pd.DataFrame:
    """Load a small raw-stats sample and force decisive/draw/no-contest variants."""

    raw_stats = pd.read_csv(PROJECT_ROOT / "data/stats/stats_raw.csv", sep=";").head(3).copy()
    raw_stats.loc[0, ["red_fighter_result", "blue_fighter_result"]] = ["W", "L"]
    raw_stats.loc[1, ["red_fighter_result", "blue_fighter_result"]] = ["D", "D"]
    raw_stats.loc[2, ["red_fighter_result", "blue_fighter_result"]] = ["NC", "NC"]
    raw_stats = raw_stats.drop(columns=["fight_outcome"], errors="ignore")
    return raw_stats


def load_athlete_stats() -> pd.DataFrame:
    """Load the tracked fighter-details dataset used in processed outputs."""

    return pd.read_csv(PROJECT_ROOT / "data/external_data/raw_fighter_details.csv")


def test_build_processed_all_bouts_preserves_non_decisive_rows() -> None:
    """The all-bouts processed output must keep draw/no-contest fights representable."""

    processed = build_processed_all_bouts(load_sample_raw_stats(), load_athlete_stats())

    assert processed["fight_outcome"].tolist() == ["red_win", "draw", "no_contest"]
    assert processed.loc[0, "winner"] == "red"
    assert pd.isna(processed.loc[1, "winner"])
    assert pd.isna(processed.loc[2, "winner"])
    assert "red_fighter_name" in processed.columns
    assert "winner_name" not in processed.columns


def test_normalize_event_date_value_handles_scraped_month_names() -> None:
    """Freshly scraped UFC Stats dates should normalize into the tracked date format."""

    assert normalize_event_date_value("September 13, 2025") == "13/09/2025"
    assert normalize_event_date_value("1/2/2025") == "01/02/2025"


def test_build_processed_decisive_only_filters_non_decisive_rows() -> None:
    """The decisive analytical output must exclude draw/no-contest fights."""

    processed = build_processed_all_bouts(load_sample_raw_stats(), load_athlete_stats())
    decisive = build_processed_decisive_only(processed)

    assert len(decisive) == 1
    assert decisive.loc[0, "winner"] == "red"
    assert decisive.loc[0, "winner_name"] == processed.loc[0, "red_fighter_name"]
    assert "fight_outcome" not in decisive.columns
    # Stable corner IDs survive the winner/loser projection so the original
    # bout stays identifiable; other red_/blue_ stat columns become winner_/loser_.
    assert "red_fighter_id" in decisive.columns
    assert "blue_fighter_id" in decisive.columns
    remaining_red = [c for c in decisive.columns if c.startswith("red_fighter_") and c not in {"red_fighter_id", "red_fighter_url"}]
    remaining_blue = [c for c in decisive.columns if c.startswith("blue_fighter_") and c not in {"blue_fighter_id", "blue_fighter_url"}]
    assert remaining_red == []
    assert remaining_blue == []


def test_build_merged_stats_scorecards_carries_fight_outcome() -> None:
    """Merged scorecards output should preserve the normalized fight outcome field."""

    raw_stats = load_sample_raw_stats()
    scorecards = pd.DataFrame(
        [
            {
                "red_fighter_name": raw_stats.loc[0, "red_fighter_name"],
                "blue_fighter_name": raw_stats.loc[0, "blue_fighter_name"],
                "event_date": raw_stats.loc[0, "event_date"],
                "red_fighter_total_pts": "49 48 48",
                "blue_fighter_total_pts": "46 47 47",
            }
        ]
    )

    merged = build_merged_stats_scorecards(raw_stats, scorecards)

    assert "fight_outcome" in merged.columns
    assert merged.loc[0, "fight_outcome"] == "red_win"
    assert merged.loc[1, "fight_outcome"] == "draw"
    assert merged.loc[2, "fight_outcome"] == "no_contest"
    assert merged.loc[0, "red_fighter_total_pts"] == "49 48 48"


def test_decisive_processed_schema_matches_tracked_output() -> None:
    """The scripted decisive output should preserve the tracked schema contract."""

    paths = DatasetPaths(project_root=PROJECT_ROOT)
    raw_stats = pd.read_csv(paths.raw_stats, sep=";")
    athlete_stats = pd.read_csv(paths.fighter_details)
    tracked = pd.read_csv(paths.processed_stats, sep=";")

    generated = build_processed_decisive_only(build_processed_all_bouts(raw_stats, athlete_stats))

    # Tracked outputs predate stable IDs and are legacy rows; the new contract
    # preserves every tracked column in order while leading with stable identity.
    for column in tracked.columns:
        assert column in generated.columns, f"Missing tracked column: {column}"
    assert generated.columns.tolist()[:5] == [
        "fight_id",
        "event_id",
        "red_fighter_id",
        "blue_fighter_id",
        "identity_status",
    ]
    # Legacy tracked rows without source IDs stay visibly warning-level.
    assert set(generated["identity_status"].unique()) <= {"legacy_fallback", "stable"}


def _stable_raw_row(fight_id: str, red_result: str = "W", blue_result: str = "L") -> dict[str, object]:
    """Build a minimal normalized raw row carrying stable UFCStats identity."""

    return {
        "fight_id": fight_id,
        "event_id": "ev-1",
        "red_fighter_id": "red-1",
        "blue_fighter_id": "blue-1",
        "fight_url": f"http://ufcstats.com/fight-details/{fight_id}",
        "event_url": "http://ufcstats.com/event-details/ev-1",
        "red_fighter_url": "http://ufcstats.com/fighter-details/red-1",
        "blue_fighter_url": "http://ufcstats.com/fighter-details/blue-1",
        "source": "ufcstats",
        "red_fighter_name": "RED FIGHTER",
        "blue_fighter_name": "BLUE FIGHTER",
        "event_date": "01/01/2025",
        "event_name": "UFC Test Event",
        "red_fighter_result": red_result,
        "blue_fighter_result": blue_result,
        "method": "U-DEC",
        "round": "3",
        "time": "5:00",
    }


def test_stable_identity_flows_through_all_bouts_decisive_and_merged() -> None:
    """Stable IDs remain authoritative from raw through derived outputs."""

    from src.data_processing.stats_processing import ensure_fight_outcome

    raw = pd.DataFrame([_stable_raw_row("stable-abc"), _stable_raw_row("stable-draw", "D", "D")])
    ensured = ensure_fight_outcome(raw)

    assert ensured.loc[0, "identity_status"] == "stable"
    assert ensured.loc[0, "fight_id"] == "stable-abc"
    assert ensured.loc[0, "red_fighter_id"] == "red-1"

    all_bouts = build_processed_all_bouts(raw, load_athlete_stats())
    assert "fight_id" in all_bouts.columns
    assert all_bouts.loc[0, "identity_status"] == "stable"

    decisive = build_processed_decisive_only(all_bouts)
    assert len(decisive) == 1
    assert decisive.iloc[0]["fight_id"] == "stable-abc"
    assert decisive.iloc[0]["red_fighter_id"] == "red-1"
    assert decisive.iloc[0]["blue_fighter_id"] == "blue-1"

    scorecards = pd.DataFrame(
        [
            {
                "red_fighter_name": ensured.loc[0, "red_fighter_name"],
                "blue_fighter_name": ensured.loc[0, "blue_fighter_name"],
                "event_date": ensured.loc[0, "event_date"],
                "red_fighter_total_pts": "30 27",
                "blue_fighter_total_pts": "27 30",
            }
        ]
    )
    merged = build_merged_stats_scorecards(raw, scorecards)
    assert "fight_id" in merged.columns
    assert merged.loc[0, "fight_id"] == "stable-abc"
    assert merged.loc[0, "fight_outcome"] == "red_win"


def test_legacy_rows_without_ids_are_visibly_warning_level() -> None:
    """Pre-ID historical rows use legacy_fallback, never silent stable identity."""

    from src.data_processing.stats_processing import ensure_fight_outcome

    raw = pd.DataFrame([_stable_raw_row("stable-1")])
    raw = raw.drop(columns=["fight_id"])
    ensured = ensure_fight_outcome(raw)

    assert ensured.loc[0, "identity_status"] == "legacy_fallback"


def test_ids_names_results_outcomes_stay_corner_aligned() -> None:
    """Red/blue corners never swap across the processing boundary."""

    from src.data_processing.stats_processing import ensure_fight_outcome

    raw = pd.DataFrame([_stable_raw_row("corner-1", "W", "L")])
    ensured = ensure_fight_outcome(raw)

    assert ensured.loc[0, "red_fighter_name"] == "RED FIGHTER"
    assert ensured.loc[0, "blue_fighter_name"] == "BLUE FIGHTER"
    assert ensured.loc[0, "red_fighter_id"] == "red-1"
    assert ensured.loc[0, "blue_fighter_id"] == "blue-1"
    assert (ensured.loc[0, "red_fighter_result"], ensured.loc[0, "blue_fighter_result"]) == ("W", "L")
    assert ensured.loc[0, "fight_outcome"] == "red_win"
