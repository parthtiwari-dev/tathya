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


def test_media_clusterer_avoids_body_only_entity_bleed() -> None:
    rows = [
        {
            "id": "a",
            "title": "Sonam Wangchuk protest update",
            "raw_text": "Sonam Wangchuk continued his protest.",
            "sources": {"source_key": "media-a", "trust_category": "media"},
        },
        {
            "id": "b",
            "title": "Education minister meets NEET topper",
            "raw_text": "Related links mention Sonam Wangchuk but the article is about education.",
            "sources": {"source_key": "media-b", "trust_category": "media"},
        },
    ]

    clusters = cluster_signals(rows, limit=5)

    sonam_cluster = next(cluster for cluster in clusters if cluster.key == "Sonam Wangchuk")
    assert [row["id"] for row in sonam_cluster.rows] == ["a"]
