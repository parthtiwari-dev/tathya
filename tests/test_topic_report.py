from pipeline.processing.topic_report import build_candidate_topics


def test_build_candidate_topics_groups_by_seed_entity() -> None:
    rows = [
        {
            "title": "RBI announces action",
            "raw_text": "Reserve Bank of India issued a press release.",
            "url": "https://rbi.org.in/1",
            "duplicate_of_signal_id": None,
            "sources": {"source_key": "rbi-press-releases"},
        },
        {
            "title": "Finance Ministry response",
            "raw_text": "Finance Ministry commented on RBI action.",
            "url": "https://example.com/2",
            "duplicate_of_signal_id": None,
            "sources": {"source_key": "indian-express-india"},
        },
    ]

    topics = build_candidate_topics(rows)

    assert topics[0].key == "Reserve Bank of India"
    assert topics[0].signal_count == 2
    assert set(topics[0].source_keys) == {"indian-express-india", "rbi-press-releases"}


def test_build_candidate_topics_tracks_canonical_count() -> None:
    rows = [
        {"title": "RBI update", "raw_text": "RBI update", "url": "https://a", "duplicate_of_signal_id": None, "sources": {"source_key": "rbi"}},
        {"title": "RBI update", "raw_text": "RBI update", "url": "https://b", "duplicate_of_signal_id": "existing", "sources": {"source_key": "media"}},
    ]

    topic = build_candidate_topics(rows)[0]

    assert topic.signal_count == 2
    assert topic.canonical_count == 1


def test_build_candidate_topics_promotes_cross_source_public_actor_topic() -> None:
    rows = [
        {
            "title": "Sonam Wangchuk hunger strike",
            "raw_text": "Sonam Wangchuk hunger strike continues.",
            "url": "https://a",
            "duplicate_of_signal_id": None,
            "sources": {"source_key": "indian-express-india"},
        },
        {
            "title": "Wangchuk can end hunger strike",
            "raw_text": "Wangchuk can end hunger strike, says family.",
            "url": "https://b",
            "duplicate_of_signal_id": None,
            "sources": {"source_key": "hindustan-times-india"},
        },
    ]

    topic = build_candidate_topics(rows)[0]

    assert topic.key == "Sonam Wangchuk"
    assert topic.signal_count == 2
    assert set(topic.source_keys) == {"hindustan-times-india", "indian-express-india"}
