from pipeline import embed_signals, semantic_search


def test_embed_signals_batches_and_stores(monkeypatch, capsys) -> None:
    rows = [{"id": "a", "title": "One"}, {"id": "b", "title": "Two"}]
    stored = []

    class Repository:
        @classmethod
        def from_environment(cls):
            return cls()

        def recent_signals_without_embeddings(self, limit):
            assert limit == 2
            return rows

        def store_signal_embedding(self, signal_id, embedding_literal):
            stored.append((signal_id, embedding_literal))

    class Embedder:
        def encode_passages(self, batch):
            return [[0.1] * 768 for _row in batch]

    monkeypatch.setattr(embed_signals, "SupabaseRepository", Repository)
    monkeypatch.setattr(embed_signals, "LocalEmbedder", Embedder)

    assert embed_signals.main(["--limit", "2", "--batch-size", "1"]) == 0
    assert [item[0] for item in stored] == ["a", "b"]
    assert "Total embeddings stored: 2" in capsys.readouterr().out


def test_semantic_search_prints_ranked_results(monkeypatch, capsys) -> None:
    class Repository:
        @classmethod
        def from_environment(cls):
            return cls()

        def match_similar_signals(self, embedding_literal, match_count, match_threshold):
            return [
                {
                    "title": "RBI penalty",
                    "similarity": 0.91,
                    "source_key": "rbi-press-releases",
                    "trust_category": "official",
                    "url": "https://rbi/a",
                }
            ]

    class Embedder:
        def encode_query(self, query):
            return [0.1] * 768

    monkeypatch.setattr(semantic_search, "SupabaseRepository", Repository)
    monkeypatch.setattr(semantic_search, "LocalEmbedder", Embedder)

    assert semantic_search.main(["RBI penalty"]) == 0
    assert "RBI penalty" in capsys.readouterr().out
