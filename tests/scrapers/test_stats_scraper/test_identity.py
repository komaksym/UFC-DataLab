"""Source-adapter identity fixtures: IDs derive from links, never names/dates."""

from src.scraping.ufc_stats.ufcstats_scraping.identity import (
    LEGACY_FALLBACK_STATUS,
    STABLE_IDENTITY_STATUS,
    extract_ufcstats_id,
    is_missing_id,
    normalize_id_value,
)


def test_is_missing_id_treats_placeholders_as_missing() -> None:
    """Placeholders and empties are never stable identity."""
    assert is_missing_id(None)
    assert is_missing_id("")
    assert is_missing_id("   ")
    assert is_missing_id("-")
    assert is_missing_id("--")
    assert is_missing_id("---")
    assert not is_missing_id("b35e47f2f58ef026")


def test_extract_ufcstats_id_supports_all_kinds() -> None:
    """Fight, event, and fighter IDs come from their own detail URLs."""
    assert (
        extract_ufcstats_id("http://ufcstats.com/fight-details/abc123", "fight") == "abc123"
    )
    assert (
        extract_ufcstats_id("http://ufcstats.com/event-details/ev456", "event") == "ev456"
    )
    assert (
        extract_ufcstats_id("http://ufcstats.com/fighter-details/f789", "fighter") == "f789"
    )


def test_extract_ufcstats_id_rejects_cross_kind_and_missing() -> None:
    """A fight URL never yields an event ID; missing URLs yield None."""
    assert extract_ufcstats_id("http://ufcstats.com/fight-details/abc123", "event") is None
    assert extract_ufcstats_id(None, "fight") is None
    assert extract_ufcstats_id("", "fight") is None
    assert extract_ufcstats_id("http://ufcstats.com/statistics/events/completed", "fight") is None


def test_extract_ufcstats_id_handles_trailing_slash_and_query() -> None:
    """Real-world URL variants still resolve to the same stable ID."""
    assert (
        extract_ufcstats_id("http://ufcstats.com/fight-details/abc123/", "fight") == "abc123"
    )
    assert (
        extract_ufcstats_id("http://ufcstats.com/fight-details/abc123?page=all", "fight")
        == "abc123"
    )


def test_normalize_id_value_strips_and_preserves_missing() -> None:
    """Whitespace is stripped; placeholders become None for hard-failure checks."""
    assert normalize_id_value("  abc123  ") == "abc123"
    assert normalize_id_value("-") is None
    assert normalize_id_value(None) is None


def test_identity_status_constants_are_distinct() -> None:
    """legacy_fallback stays visibly distinct from stable."""
    assert STABLE_IDENTITY_STATUS == "stable"
    assert LEGACY_FALLBACK_STATUS == "legacy_fallback"
    assert STABLE_IDENTITY_STATUS != LEGACY_FALLBACK_STATUS
