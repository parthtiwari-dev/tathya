import json
from datetime import UTC, datetime

from pipeline.generation.case_file_builder import CaseFileDraft, DraftClaim, DraftEvent, DraftFact
from pipeline.storage import supabase_repository
from pipeline.storage.supabase_repository import SupabaseRepository
from shared.models import IngestedSignal


def test_persist_signal_posts_the_complete_atomic_payload(monkeypatch) -> None:
    signal = IngestedSignal(source_key="source", source_url="https://example.com/feed", canonical_url="https://example.com/story", published_at=datetime(2026, 7, 19, tzinfo=UTC), raw_text="Snapshot me")

    class Response:
        def read(self) -> bytes:
            return b'"d98b1ff1-52b3-4e35-9c0f-f214a5178770"'

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    def fake_urlopen(request, timeout):
        assert request.full_url == "https://project.supabase.co/rest/v1/rpc/record_signal_snapshot"
        assert request.get_header("Authorization") == "Bearer test-key"
        assert timeout == 30
        body = json.loads(request.data)
        assert body["p_source_key"] == "source"
        assert body["p_raw_content"] == "Snapshot me"
        assert len(body["p_content_hash"]) == 64
        return Response()

    monkeypatch.setattr(supabase_repository, "urlopen", fake_urlopen)
    repository = SupabaseRepository("https://project.supabase.co/", "test-key")
    assert repository.persist_signal(signal) == "d98b1ff1-52b3-4e35-9c0f-f214a5178770"


def test_void_rpc_response_is_accepted(monkeypatch) -> None:
    class Response:
        def read(self) -> bytes:
            return b""

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    monkeypatch.setattr(supabase_repository, "urlopen", lambda *_args, **_kwargs: Response())
    repository = SupabaseRepository("https://project.supabase.co", "test-key")
    repository.record_source_run("source", 1, "success")


def test_source_activation_rpcs(monkeypatch) -> None:
    calls = []

    def fake_rpc(self, function_name, payload):
        calls.append((function_name, payload))
        if function_name == "set_source_enabled":
            return False
        return [{"signal_count": 2, "snapshot_count": 2}]

    monkeypatch.setattr(SupabaseRepository, "_rpc", fake_rpc)
    repository = SupabaseRepository("https://project.supabase.co", "test-key")

    assert repository.set_source_enabled("source", True) is False
    assert repository.source_activation_summary("source")["signal_count"] == 2
    assert calls == [
        ("set_source_enabled", {"p_source_key": "source", "p_enabled": True}),
        ("source_activation_summary", {"p_source_key": "source"}),
    ]


def test_recent_signals_gets_joined_source_rows(monkeypatch) -> None:
    class Response:
        def read(self) -> bytes:
            return b'[{"id":"1","sources":{"source_key":"rbi-press-releases"}}]'

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    def fake_urlopen(request, timeout):
        assert request.full_url.startswith("https://project.supabase.co/rest/v1/signals?")
        assert "sources%28source_key%2Ctrust_category%29" in request.full_url
        assert request.get_header("Authorization") == "Bearer test-key"
        assert timeout == 30
        return Response()

    monkeypatch.setattr(supabase_repository, "urlopen", fake_urlopen)
    repository = SupabaseRepository("https://project.supabase.co", "test-key")

    assert repository.recent_signals(5)[0]["sources"]["source_key"] == "rbi-press-releases"


def test_embedding_repository_methods(monkeypatch) -> None:
    calls = []

    def fake_rpc(self, function_name, payload):
        calls.append((function_name, payload))
        if function_name == "match_similar_signals":
            return [{"id": "a"}]

    monkeypatch.setattr(SupabaseRepository, "_rpc", fake_rpc)
    repository = SupabaseRepository("https://project.supabase.co", "test-key")

    repository.store_signal_embedding("signal-id", "[0.1]")
    assert repository.match_similar_signals("[0.1]", match_count=5, match_threshold=0.7) == [{"id": "a"}]
    assert calls == [
        ("store_signal_embedding", {"p_signal_id": "signal-id", "p_embedding": "[0.1]"}),
        (
            "match_similar_signals",
            {"p_query_embedding": "[0.1]", "p_match_count": 5, "p_match_threshold": 0.7},
        ),
    ]


def test_mark_signal_duplicate_rpc(monkeypatch) -> None:
    calls = []

    def fake_rpc(self, function_name, payload):
        calls.append((function_name, payload))

    monkeypatch.setattr(SupabaseRepository, "_rpc", fake_rpc)
    repository = SupabaseRepository("https://project.supabase.co", "test-key")

    repository.mark_signal_duplicate("duplicate-id", "canonical-id")

    assert calls == [
        (
            "mark_signal_duplicate",
            {
                "p_duplicate_signal_id": "duplicate-id",
                "p_canonical_signal_id": "canonical-id",
            },
        )
    ]


def test_persist_case_file_draft_calls_append_rpcs(monkeypatch) -> None:
    calls = []

    def fake_rpc(self, function_name, payload):
        calls.append((function_name, payload))
        if function_name == "upsert_topic_cluster":
            return "topic-id"
        return "row-id"

    monkeypatch.setattr(SupabaseRepository, "_rpc", fake_rpc)
    repository = SupabaseRepository("https://project.supabase.co", "test-key")
    draft = CaseFileDraft(
        title="Reserve Bank of India",
        neutral_summary="summary",
        significance_score=42,
        promotable=False,
        events=(DraftEvent("2026-07-20", "event", ("signal-id",), ("https://rbi/a",)),),
        claims=(DraftClaim("govt", "claim", "quote", "signal-id", "https://rbi/a"),),
        verifiable_facts=(DraftFact("fact", "https://rbi/a", "dataset", "quote"),),
        related_entities=("Reserve Bank of India",),
    )

    assert repository.persist_case_file_draft(draft, ["signal-id"]) == "topic-id"
    assert [call[0] for call in calls] == [
        "upsert_topic_cluster",
        "append_topic_event",
        "append_topic_claim",
        "append_topic_fact",
    ]
    assert calls[0][1]["p_signal_ids"] == ["signal-id"]
