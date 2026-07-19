from pipeline.processing.near_duplicate import find_near_duplicates


def test_find_near_duplicates_across_sources_only() -> None:
    rows = [
        {
            "id": "a",
            "published_at": "2026-07-19T10:00:00+00:00",
            "title": "RBI imposes monetary penalty on Example Bank",
            "raw_text": "RBI imposes monetary penalty on Example Bank for regulatory non-compliance.",
            "url": "https://rbi/a",
            "sources": {"source_key": "rbi"},
        },
        {
            "id": "b",
            "published_at": "2026-07-19T11:00:00+00:00",
            "title": "RBI imposes monetary penalty on Example Bank",
            "raw_text": "RBI imposes monetary penalty on Example Bank for regulatory non-compliance.",
            "url": "https://media/b",
            "sources": {"source_key": "media"},
        },
    ]

    candidates = find_near_duplicates(rows, threshold=0.8)

    assert len(candidates) == 1
    assert candidates[0].canonical_signal_id == "a"
    assert candidates[0].duplicate_signal_id == "b"


def test_find_near_duplicates_ignores_same_source_and_existing_duplicates() -> None:
    rows = [
        {"id": "a", "title": "Same story words here", "raw_text": "Same story words here", "sources": {"source_key": "media"}},
        {"id": "b", "title": "Same story words here", "raw_text": "Same story words here", "sources": {"source_key": "media"}},
        {
            "id": "c",
            "title": "Same story words here",
            "raw_text": "Same story words here",
            "duplicate_of_signal_id": "a",
            "sources": {"source_key": "other"},
        },
    ]

    assert find_near_duplicates(rows, threshold=0.8) == []
