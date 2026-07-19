from pipeline.processing.clusterer import cluster_signals


def test_cluster_signals_returns_scored_entity_cluster() -> None:
    rows = [
        {
            "id": "a",
            "title": "RBI update",
            "raw_text": "Reserve Bank of India issued an update.",
            "url": "https://rbi/a",
            "sources": {"source_key": "rbi", "trust_category": "official"},
        },
        {
            "id": "b",
            "title": "RBI update reported",
            "raw_text": "RBI update reported by media.",
            "url": "https://media/b",
            "sources": {"source_key": "media", "trust_category": "media"},
        },
    ]

    cluster = cluster_signals(rows, limit=1)[0]

    assert cluster.key == "Reserve Bank of India"
    assert "Reserve Bank of India" in cluster.entities
    assert cluster.significance.independent_source_count == 2


def test_cluster_signals_skips_existing_duplicates() -> None:
    rows = [
        {"id": "a", "title": "RBI update", "raw_text": "RBI update", "sources": {"source_key": "rbi", "trust_category": "official"}},
        {
            "id": "b",
            "title": "RBI update",
            "raw_text": "RBI update",
            "duplicate_of_signal_id": "a",
            "sources": {"source_key": "media", "trust_category": "media"},
        },
    ]

    cluster = cluster_signals(rows, limit=1)[0]

    assert len(cluster.rows) == 1
