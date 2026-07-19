from pipeline import case_file_persist


def test_case_file_persist_writes_cluster_drafts(monkeypatch, capsys) -> None:
    rows = [
        {
            "id": "a",
            "published_at": "2026-07-20T10:00:00+00:00",
            "title": "RBI announces update",
            "raw_text": "Reserve Bank of India announced a regulatory update.",
            "url": "https://rbi/a",
            "sources": {"source_key": "rbi", "trust_category": "official"},
        }
    ]
    persisted = []

    class Repository:
        @classmethod
        def from_environment(cls):
            return cls()

        def recent_signals(self, limit):
            assert limit == 10
            return rows

        def persist_case_file_draft(self, draft, signal_ids):
            persisted.append((draft.title, signal_ids))
            return "topic-id"

    monkeypatch.setattr(case_file_persist, "SupabaseRepository", Repository)

    assert case_file_persist.main(["--signals", "10", "--topics", "1"]) == 0
    assert persisted == [("Reserve Bank of India", ["a"])]
    assert "Total case-file drafts persisted: 1" in capsys.readouterr().out


def test_case_file_persist_can_skip_non_promotable(monkeypatch, capsys) -> None:
    rows = [
        {
            "id": "a",
            "title": "RBI announces update",
            "raw_text": "Reserve Bank of India announced a regulatory update.",
            "url": "https://rbi/a",
            "sources": {"source_key": "rbi", "trust_category": "official"},
        }
    ]

    class Repository:
        @classmethod
        def from_environment(cls):
            return cls()

        def recent_signals(self, limit):
            return rows

        def persist_case_file_draft(self, draft, signal_ids):
            raise AssertionError("Should not persist non-promotable clusters")

    monkeypatch.setattr(case_file_persist, "SupabaseRepository", Repository)

    assert case_file_persist.main(["--signals", "10", "--topics", "1", "--promotable-only"]) == 0
    assert "Total case-file drafts persisted: 0" in capsys.readouterr().out
