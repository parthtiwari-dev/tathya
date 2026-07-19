import json
from datetime import UTC, datetime

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
