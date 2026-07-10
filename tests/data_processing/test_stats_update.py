import pandas as pd

from src.data_processing.stats_update import merge_incremental_fights


def _fight(method: str, round_: str, time: str) -> dict[str, str]:
    return {
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


def test_merge_incremental_fights_preserves_same_event_rematch() -> None:
    no_contest = _fight("Overturned", "1", "1:51")
    rematch = _fight("Submission", "1", "3:44")

    existing = pd.DataFrame([no_contest, rematch])
    incremental = pd.DataFrame([rematch])

    merged = merge_incremental_fights(existing, incremental)

    assert len(merged) == 2
    assert set(merged["fight_outcome"]) == {"no_contest", "red_win"}
    assert set(merged["method"]) == {"Overturned", "Submission"}
