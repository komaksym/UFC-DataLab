from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype


DECISIVE_OUTCOMES = {"red_win", "blue_win"}
NAN_PLACEHOLDERS = ["-", "--", "---"]
ZERO_PCT_COLUMNS = {
    "red_fighter_sig_str_pct",
    "blue_fighter_sig_str_pct",
    "red_fighter_TD_pct",
    "blue_fighter_TD_pct",
}
RESULT_ALIASES = {
    "W": "W",
    "WIN": "W",
    "L": "L",
    "LOSS": "L",
    "D": "D",
    "DRAW": "D",
    "NC": "NC",
    "N/C": "NC",
    "NO CONTEST": "NC",
    "NO-CONTEST": "NC",
}
RAW_STATS_COLUMN_ORDER = [
    "red_fighter_name",
    "blue_fighter_name",
    "event_date",
    "red_fighter_nickname",
    "blue_fighter_nickname",
    "red_fighter_result",
    "blue_fighter_result",
    "fight_outcome",
    "method",
    "round",
    "time",
    "time_format",
    "referee",
    "details",
    "bout_type",
    "bonus",
    "event_name",
    "event_location",
    "red_fighter_KD",
    "blue_fighter_KD",
    "red_fighter_sig_str",
    "blue_fighter_sig_str",
    "red_fighter_sig_str_pct",
    "blue_fighter_sig_str_pct",
    "red_fighter_total_str",
    "blue_fighter_total_str",
    "red_fighter_TD",
    "blue_fighter_TD",
    "red_fighter_TD_pct",
    "blue_fighter_TD_pct",
    "red_fighter_sub_att",
    "blue_fighter_sub_att",
    "red_fighter_rev",
    "blue_fighter_rev",
    "red_fighter_ctrl",
    "blue_fighter_ctrl",
    "red_fighter_sig_str_head",
    "blue_fighter_sig_str_head",
    "red_fighter_sig_str_body",
    "blue_fighter_sig_str_body",
    "red_fighter_sig_str_leg",
    "blue_fighter_sig_str_leg",
    "red_fighter_sig_str_distance",
    "blue_fighter_sig_str_distance",
    "red_fighter_sig_str_clinch",
    "blue_fighter_sig_str_clinch",
    "red_fighter_sig_str_ground",
    "blue_fighter_sig_str_ground",
    "red_fighter_sig_str_head_pct",
    "blue_fighter_sig_str_head_pct",
    "red_fighter_sig_str_body_pct",
    "blue_fighter_sig_str_body_pct",
    "red_fighter_sig_str_leg_pct",
    "blue_fighter_sig_str_leg_pct",
    "red_fighter_sig_str_distance_pct",
    "blue_fighter_sig_str_distance_pct",
    "red_fighter_sig_str_clinch_pct",
    "blue_fighter_sig_str_clinch_pct",
    "red_fighter_sig_str_ground_pct",
    "blue_fighter_sig_str_ground_pct",
]
LEGACY_PROCESSED_COLUMN_ORDER = [
    "winner_name",
    "loser_name",
    "event_date",
    "method",
    "round",
    "time",
    "time_format",
    "bout_type",
    "event_name",
    "event_location",
    "winner_stance",
    "loser_stance",
    "winner",
    "delta_KD",
    "delta_sig_str_pct",
    "delta_total_str_pct",
    "delta_TD_pct",
    "delta_sub_att",
    "delta_rev",
    "delta_ctrl",
    "delta_sig_str_head_acc_pct",
    "delta_sig_str_body_acc_pct",
    "delta_sig_str_leg_acc_pct",
    "delta_sig_str_distance_acc_pct",
    "delta_sig_str_clinch_acc_pct",
    "delta_sig_str_ground_acc_pct",
    "delta_sig_str_head_tar_pct",
    "delta_sig_str_body_tar_pct",
    "delta_sig_str_leg_tar_pct",
    "delta_sig_str_distance_pos_pct",
    "delta_sig_str_clinch_pos_pct",
    "delta_sig_str_ground_pos_pct",
    "delta_height",
    "delta_reach",
    "delta_slpm_cs",
    "delta_str_acc_cs",
    "delta_sapm_cs",
    "delta_str_def_cs",
    "delta_td_avg_cs",
    "delta_td_acc_cs",
    "delta_td_def_cs",
    "delta_sub_avg_cs",
]


@dataclass(frozen=True)
class DatasetPaths:
    """Default repository paths for tracked dataset artifacts."""

    project_root: Path = Path(__file__).resolve().parents[2]
    raw_stats: Path = project_root / "data/stats/stats_raw.csv"
    processed_stats: Path = project_root / "data/stats/stats_processed.csv"
    processed_all_bouts: Path = project_root / "data/stats/stats_processed_all_bouts.csv"
    fighter_details: Path = project_root / "data/external_data/raw_fighter_details.csv"
    scorecards: Path = project_root / "data/scorecards/OCR_parsed_scorecards/scorecards.csv"
    merged_stats_scorecards: Path = (
        project_root / "data/merged_stats_n_scorecards/merged_stats_n_scorecards.csv"
    )


def normalize_result_marker(value: object) -> str:
    """Normalize raw result markers into a small canonical set."""

    if pd.isna(value):
        return "-"

    normalized_value = RESULT_ALIASES.get(str(value).strip().upper())
    if normalized_value is None:
        raise ValueError(f"Unsupported result marker: {value}")

    return normalized_value


def normalize_event_date_value(value: object) -> object:
    """Normalize event dates into the repository's `dd/mm/YYYY` schema."""

    if pd.isna(value):
        return value
    if not isinstance(value, str):
        return value

    text = value.strip()
    if not text:
        return text

    if "/" in text:
        day, month, year = [part.strip() for part in text.split("/")]
        return f"{int(day):02d}/{int(month):02d}/{year}"

    return pd.to_datetime(text, errors="raise").strftime("%d/%m/%Y")


def reorder_columns(frame: pd.DataFrame, preferred_order: list[str]) -> pd.DataFrame:
    """Return a frame with the preferred columns first and all remaining columns after."""

    ordered = [column for column in preferred_order if column in frame.columns]
    trailing = [column for column in frame.columns if column not in ordered]
    return frame.loc[:, ordered + trailing]


def derive_fight_outcome(red_result: object, blue_result: object) -> str:
    """Derive the fight-level outcome from red/blue result markers."""

    red = normalize_result_marker(red_result)
    blue = normalize_result_marker(blue_result)

    if red == "W" and blue == "L":
        return "red_win"
    if red == "L" and blue == "W":
        return "blue_win"
    if red == "D" and blue == "D":
        return "draw"
    if red == "NC" and blue == "NC":
        return "no_contest"

    raise ValueError(f"Unsupported fight outcome combination: {red}/{blue}")


def ensure_fight_outcome(stats: pd.DataFrame) -> pd.DataFrame:
    """Normalize result columns and ensure the raw stats frame has fight outcomes."""

    stats = stats.copy()
    stats["event_date"] = stats["event_date"].apply(normalize_event_date_value)
    for fighter_name_col in ("red_fighter_name", "blue_fighter_name"):
        stats[fighter_name_col] = stats[fighter_name_col].apply(
            lambda value: value.upper() if isinstance(value, str) else value
        )
    stats["red_fighter_result"] = stats["red_fighter_result"].apply(normalize_result_marker)
    stats["blue_fighter_result"] = stats["blue_fighter_result"].apply(normalize_result_marker)

    fight_outcomes = [
        derive_fight_outcome(red_result, blue_result)
        for red_result, blue_result in zip(
            stats["red_fighter_result"],
            stats["blue_fighter_result"],
        )
    ]

    if "fight_outcome" in stats.columns:
        stats["fight_outcome"] = fight_outcomes
        return reorder_columns(stats, RAW_STATS_COLUMN_ORDER)

    insert_at = stats.columns.get_loc("blue_fighter_result") + 1
    stats.insert(insert_at, "fight_outcome", fight_outcomes)
    return reorder_columns(stats, RAW_STATS_COLUMN_ORDER)


def add_winner_column(stats: pd.DataFrame) -> pd.DataFrame:
    """Add an optional winner column derived from decisive outcomes only."""

    stats = stats.copy()
    winners = stats["fight_outcome"].map({"red_win": "red", "blue_win": "blue"})
    stats["winner"] = winners
    return stats


def rename_significant_strike_columns(fights_stats: pd.DataFrame) -> pd.DataFrame:
    """Mirror the notebook renames for sig strike accuracy/target/position columns."""

    fights_stats = fights_stats.copy()
    sig_str_acc_cols = [
        "fighter_sig_str_head",
        "fighter_sig_str_body",
        "fighter_sig_str_leg",
        "fighter_sig_str_distance",
        "fighter_sig_str_clinch",
        "fighter_sig_str_ground",
    ]
    sig_str_tar_cols = [
        "fighter_sig_str_head_pct",
        "fighter_sig_str_body_pct",
        "fighter_sig_str_leg_pct",
    ]
    sig_str_pos_cols = [
        "fighter_sig_str_distance_pct",
        "fighter_sig_str_clinch_pct",
        "fighter_sig_str_ground_pct",
    ]

    column_name_mappings: dict[str, str] = {}
    for fighter in ("red_", "blue_"):
        for column in sig_str_acc_cols:
            column_name_mappings[f"{fighter}{column}"] = f"{fighter}{column}_acc"

        for column in sig_str_tar_cols:
            base = column.removesuffix("_pct")
            column_name_mappings[f"{fighter}{column}"] = f"{fighter}{base}_tar_pct"

        for column in sig_str_pos_cols:
            base = column.removesuffix("_pct")
            column_name_mappings[f"{fighter}{column}"] = f"{fighter}{base}_pos_pct"

    return fights_stats.rename(columns=column_name_mappings)


def prepare_fights_stats(fights_stats: pd.DataFrame) -> pd.DataFrame:
    """Prepare scraped fight stats for downstream processing."""

    fights_stats = ensure_fight_outcome(fights_stats)

    redundant_cols = ["fighter_sig_str", "fighter_TD"]
    irrelevant_cols = [
        "red_fighter_nickname",
        "blue_fighter_nickname",
        "referee",
        "details",
        "bonus",
    ]
    cols_to_drop = [f"{fighter}{column}" for fighter in ("red_", "blue_") for column in redundant_cols]
    cols_to_drop.extend(irrelevant_cols)

    fights_stats = fights_stats.drop(columns=cols_to_drop, errors="ignore")
    return rename_significant_strike_columns(fights_stats)


def conv_from_inches_to_cm(inches: object) -> object:
    """Convert UFC fighter height/reach strings from inches schema into centimeters."""

    if not isinstance(inches, str):
        return inches

    inches = inches.replace('"', "").strip()
    if "'" in inches:
        feet, inch = inches.split("'")
        whole_inches = int(inch) if inch else 0
        return round(int(feet) * 30.48 + whole_inches * 2.54, 2)

    return round(float(inches) * 2.54, 2)


def prepare_athlete_stats(athlete_stats: pd.DataFrame) -> pd.DataFrame:
    """Normalize the external fighter-details dataset used in processed outputs."""

    athlete_stats = athlete_stats.copy()
    athlete_stats = athlete_stats.drop(columns=["Weight", "DOB"], errors="ignore")
    athlete_stats["fighter_name"] = athlete_stats["fighter_name"].str.upper()
    athlete_stats.columns = athlete_stats.columns.str.lower()
    athlete_stats = athlete_stats.rename(
        columns={
            "slpm": "slpm_cs",
            "str_acc": "str_acc_cs",
            "sapm": "sapm_cs",
            "str_def": "str_def_cs",
            "td_avg": "td_avg_cs",
            "td_acc": "td_acc_cs",
            "td_def": "td_def_cs",
            "sub_avg": "sub_avg_cs",
        }
    )
    athlete_stats["height"] = athlete_stats["height"].apply(conv_from_inches_to_cm)
    athlete_stats["reach"] = athlete_stats["reach"].apply(conv_from_inches_to_cm)
    return athlete_stats


def merge_athlete_stats(fights_stats: pd.DataFrame, athlete_stats: pd.DataFrame) -> pd.DataFrame:
    """Attach external fighter career statistics for both corners."""

    athlete_stats = prepare_athlete_stats(athlete_stats)
    red_mappings = {
        column: f"red_fighter_{column}" for column in athlete_stats.columns if column != "fighter_name"
    }
    blue_mappings = {
        column: f"blue_fighter_{column}" for column in athlete_stats.columns if column != "fighter_name"
    }

    stats = pd.merge(
        fights_stats,
        athlete_stats.rename(columns=red_mappings),
        left_on="red_fighter_name",
        right_on="fighter_name",
        how="left",
    ).drop(columns="fighter_name")
    stats = pd.merge(
        stats,
        athlete_stats.rename(columns=blue_mappings),
        left_on="blue_fighter_name",
        right_on="fighter_name",
        how="left",
    ).drop(columns="fighter_name")
    return stats


def replace_placeholders(stats: pd.DataFrame) -> pd.DataFrame:
    """Replace source placeholders with NaN or zero according to column semantics."""

    stats = stats.copy()
    placeholder_columns = [
        column for column in stats.columns if stats[column].isin(NAN_PLACEHOLDERS).any()
    ]
    cols_to_zero = [column for column in placeholder_columns if column in ZERO_PCT_COLUMNS]
    cols_to_nan = [column for column in placeholder_columns if column not in ZERO_PCT_COLUMNS]

    if cols_to_nan:
        stats[cols_to_nan] = stats[cols_to_nan].replace(NAN_PLACEHOLDERS, np.nan)
    if cols_to_zero:
        stats[cols_to_zero] = stats[cols_to_zero].replace(NAN_PLACEHOLDERS, "0")

    return stats


def find_numeric_object_columns(stats: pd.DataFrame) -> list[str]:
    """Find red/blue string columns that encode numeric values."""

    cols_to_standardize: list[str] = []
    for column in stats.columns:
        if stats[column].dtype != "object":
            continue
        if not (column.startswith("red_") or column.startswith("blue_")):
            continue

        sample = stats[column].dropna().astype(str).head(1)
        if not sample.empty and any(char.isdigit() for char in sample.iloc[0]):
            cols_to_standardize.append(column)

    return cols_to_standardize


def bucket_numeric_object_columns(stats: pd.DataFrame, columns: Iterable[str]) -> tuple[list[str], list[str], list[str]]:
    """Bucket object columns into ratio, percent, and time groups."""

    of_cols: list[str] = []
    pct_cols: list[str] = []
    time_cols: list[str] = []

    for column in columns:
        sample = stats[column].dropna().astype(str).head(1)
        if sample.empty:
            continue

        sample_value = sample.iloc[0]
        if re.search(r"\d+\s*of\s*\d+", sample_value):
            of_cols.append(column)
        elif re.search(r"\d+\s*%", sample_value):
            pct_cols.append(column)
        elif re.search(r"\d+\s*:\s*\d+", sample_value):
            time_cols.append(column)

    return of_cols, pct_cols, time_cols


def convert_ratio_to_pct(value: object) -> object:
    """Convert `x of y` strings into percentages."""

    if pd.isna(value):
        return value
    if not isinstance(value, str):
        return value

    values = value.split("of")
    if len(values) != 2:
        return 0

    made = int(values[0].strip())
    attempted = int(values[1].strip())
    if made == 0 or attempted == 0:
        return 0

    return round((made * 100) / attempted, 2)


def format_time_schema(value: object) -> object:
    """Ensure control-time strings follow `hh:mm:ss` before conversion to seconds."""

    if pd.isna(value):
        return value
    if not isinstance(value, str):
        return value

    parts = value.split(":")
    if len(parts) != 2:
        return value

    minutes, seconds = parts
    return f"00:{minutes.zfill(2)}:{seconds.zfill(2)}"


def standardize_numeric_columns(stats: pd.DataFrame) -> pd.DataFrame:
    """Mirror the notebook conversions for ratio, percentage, and time columns."""

    stats = stats.copy()
    cols_to_standardize = find_numeric_object_columns(stats)
    of_cols, pct_cols, time_cols = bucket_numeric_object_columns(stats, cols_to_standardize)

    for column in of_cols:
        stats[column] = stats[column].apply(convert_ratio_to_pct)
    stats = stats.rename(columns={column: f"{column}_pct" for column in of_cols})

    if pct_cols:
        stats[pct_cols] = stats[pct_cols].apply(lambda column: column.str.strip("%"))

    if time_cols:
        stats[time_cols] = stats[time_cols].replace("0", "0:00")
        for column in time_cols:
            stats[column] = stats[column].apply(format_time_schema)
        stats[time_cols] = stats[time_cols].apply(
            lambda column: pd.to_timedelta(column).dt.total_seconds()
        )

    for column in stats.columns:
        try:
            stats[column] = pd.to_numeric(stats[column], downcast="float")
        except (TypeError, ValueError):
            continue

    return stats


def build_processed_all_bouts(
    fights_stats: pd.DataFrame, athlete_stats: pd.DataFrame
) -> pd.DataFrame:
    """Build the processed all-bouts view that preserves red/blue columns."""

    stats = prepare_fights_stats(fights_stats)
    stats = merge_athlete_stats(stats, athlete_stats)
    stats = replace_placeholders(stats)
    stats = standardize_numeric_columns(stats)
    return add_winner_column(stats)


def rename_condition(column: str) -> str:
    """Rename red/blue columns into winner/loser columns."""

    if column.startswith("red_fighter_"):
        return column.replace("red_fighter_", "winner_")
    if column.startswith("blue_fighter_"):
        return column.replace("blue_fighter_", "loser_")
    return column


def set_winner_n_loser(stats: pd.DataFrame, winner_col: str = "winner") -> pd.DataFrame:
    """Create winner/loser columns from red/blue columns for decisive fights only."""

    stats = stats.copy()
    cols_to_drop: list[str] = []

    for column in stats.columns:
        if not column.startswith("red_fighter_"):
            continue

        base = column.removeprefix("red_fighter_")
        red_col = f"red_fighter_{base}"
        blue_col = f"blue_fighter_{base}"
        if blue_col not in stats.columns:
            continue

        stats[f"winner_{base}"] = np.where(stats[winner_col] == "red", stats[red_col], stats[blue_col])
        stats[f"loser_{base}"] = np.where(stats[winner_col] == "red", stats[blue_col], stats[red_col])
        cols_to_drop.extend([red_col, blue_col])

    return stats.drop(columns=cols_to_drop)


def deltafy_data(stats: pd.DataFrame) -> pd.DataFrame:
    """Convert paired numeric winner/loser columns into winner-minus-loser deltas."""

    stats = stats.copy()
    cols_to_drop: list[str] = []
    delta_cols: dict[str, pd.Series] = {}

    for column in stats.columns:
        if not column.startswith("winner_"):
            continue

        base = column.removeprefix("winner_")
        loser_col = f"loser_{base}"
        if loser_col not in stats.columns:
            continue
        if not is_numeric_dtype(stats[column]):
            continue

        delta_cols[f"delta_{base}"] = np.round(stats[column] - stats[loser_col], 2)
        cols_to_drop.extend([column, loser_col])

    delta_df = pd.DataFrame(delta_cols)
    stats = pd.concat([stats, delta_df], axis=1)
    return stats.drop(columns=cols_to_drop)


def build_processed_decisive_only(all_bouts_stats: pd.DataFrame) -> pd.DataFrame:
    """Build the winner/loser analytical view from the all-bouts processed dataset."""

    stats = all_bouts_stats.loc[all_bouts_stats["fight_outcome"].isin(DECISIVE_OUTCOMES)].copy()
    stats = stats.drop(columns=["red_fighter_result", "blue_fighter_result", "fight_outcome"], errors="ignore")
    cols_order = [rename_condition(column) for column in stats.columns]
    stats = set_winner_n_loser(stats)
    stats = stats.loc[:, cols_order]
    stats = deltafy_data(stats)
    return reorder_columns(stats, LEGACY_PROCESSED_COLUMN_ORDER)


def build_merged_stats_scorecards(
    fights_stats: pd.DataFrame, scorecards: pd.DataFrame
) -> pd.DataFrame:
    """Build the raw all-bouts stats plus scorecards export."""

    fights_stats = ensure_fight_outcome(fights_stats)
    return pd.merge(
        fights_stats,
        scorecards,
        how="left",
        on=["red_fighter_name", "blue_fighter_name", "event_date"],
    )


def load_csv(path: Path, sep: str = ";") -> pd.DataFrame:
    """Read a CSV file with the requested separator."""

    return pd.read_csv(path, sep=sep)


def write_dataset_outputs(paths: DatasetPaths = DatasetPaths()) -> None:
    """Rebuild processed stats and merged scorecards outputs from tracked inputs."""

    raw_stats = load_csv(paths.raw_stats, sep=";")
    athlete_stats = load_csv(paths.fighter_details, sep=",")
    scorecards = load_csv(paths.scorecards, sep=";")

    processed_all_bouts = build_processed_all_bouts(raw_stats, athlete_stats)
    processed_decisive = build_processed_decisive_only(processed_all_bouts)
    merged_stats_scorecards = build_merged_stats_scorecards(raw_stats, scorecards)

    processed_all_bouts.to_csv(paths.processed_all_bouts, sep=";", index=False)
    processed_decisive.to_csv(paths.processed_stats, sep=";", index=False)
    merged_stats_scorecards.to_csv(paths.merged_stats_scorecards, index=False)


if __name__ == "__main__":
    write_dataset_outputs()
