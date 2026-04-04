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
    assert not any(column.startswith("red_fighter_") for column in decisive.columns)
    assert not any(column.startswith("blue_fighter_") for column in decisive.columns)


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

    assert generated.columns.tolist() == tracked.columns.tolist()
