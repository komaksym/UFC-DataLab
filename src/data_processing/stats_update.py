from __future__ import annotations

import pandas as pd

from .stats_processing import ensure_fight_outcome


FIGHT_IDENTITY_COLUMNS = [
    "red_fighter_name",
    "blue_fighter_name",
    "event_date",
    "event_name",
    "method",
    "round",
    "time",
]


def merge_incremental_fights(
    existing: pd.DataFrame,
    incremental: pd.DataFrame,
) -> pd.DataFrame:
    """Merge newly scraped fights without collapsing same-event rematches.

    Fighter pair, event, and date are not a unique bout key: UFC Ultimate
    Japan contained two Kazushi Sakuraba vs. Marcus Silveira bouts on the
    same card. Method, round, and time provide the discriminator available in
    the tracked schema until UFCStats fight IDs are stored explicitly.
    """

    existing = ensure_fight_outcome(existing)
    incremental = ensure_fight_outcome(incremental)
    combined = pd.concat([incremental, existing], ignore_index=True, sort=False)
    combined = combined.drop_duplicates(subset=FIGHT_IDENTITY_COLUMNS, keep="first")
    combined["_event_date_sort"] = pd.to_datetime(
        combined["event_date"], dayfirst=True, errors="raise"
    )
    combined = combined.sort_values(
        ["_event_date_sort", "event_name", "red_fighter_name", "blue_fighter_name"],
        ascending=[False, True, True, True],
        kind="stable",
    ).drop(columns="_event_date_sort")
    return combined.reset_index(drop=True)
