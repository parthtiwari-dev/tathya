from datetime import UTC, datetime

from pipeline.processing.significance_scorer import score_topic


def test_score_topic_requires_official_and_nonofficial_sources_for_promotion() -> None:
    rows = [
        {
            "published_at": "2026-07-20T10:00:00+00:00",
            "sources": {"source_key": "rbi", "trust_category": "official"},
        },
        {
            "published_at": "2026-07-20T10:10:00+00:00",
            "sources": {"source_key": "media-a", "trust_category": "media"},
        },
        {
            "published_at": "2026-07-20T10:20:00+00:00",
            "sources": {"source_key": "media-b", "trust_category": "media"},
        },
    ]

    score = score_topic(rows, now=datetime(2026, 7, 20, 12, tzinfo=UTC))

    assert score.promotable is True
    assert score.official_source_present is True
    assert score.media_or_citizen_source_present is True
    assert score.independent_source_count == 3


def test_score_topic_ignores_existing_duplicates() -> None:
    rows = [
        {"published_at": "2026-07-20T10:00:00+00:00", "sources": {"source_key": "rbi", "trust_category": "official"}},
        {
            "published_at": "2026-07-20T10:10:00+00:00",
            "duplicate_of_signal_id": "existing",
            "sources": {"source_key": "media-a", "trust_category": "media"},
        },
    ]

    score = score_topic(rows, now=datetime(2026, 7, 20, 12, tzinfo=UTC))

    assert score.canonical_count == 1
    assert score.promotable is False
