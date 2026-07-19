from datetime import UTC, datetime

from pipeline import source_activation
from shared.models import IngestedSignal


def test_source_activation_persists_once_and_restores_db_state(monkeypatch, capsys) -> None:
    signal = IngestedSignal(
        source_key="hindustan-times-india",
        source_url="https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
        canonical_url="https://example.com/story",
        published_at=datetime(2026, 7, 19, tzinfo=UTC),
        raw_text="Story",
    )
    calls = []

    class Repository:
        @classmethod
        def from_environment(cls):
            return cls()

        def set_source_enabled(self, source_key, enabled):
            calls.append(("set", source_key, enabled))
            return False

        def persist_signal(self, selected):
            calls.append(("persist", selected.source_key))

        def record_source_run(self, source_key, signal_count, status, detail=None):
            calls.append(("run", source_key, signal_count, status, detail))

        def source_activation_summary(self, source_key):
            return {
                "signal_count": 1,
                "snapshot_count": 1,
                "canonical_signal_count": 1,
                "source_run_count": 1,
                "enabled": False,
            }

    monkeypatch.setattr(source_activation, "fetch_signals", lambda _source: [signal])
    monkeypatch.setattr(source_activation, "SupabaseRepository", Repository)

    assert source_activation.main(["--source", "hindustan-times-india"]) == 0
    assert calls == [
        ("set", "hindustan-times-india", True),
        ("persist", "hindustan-times-india"),
        ("run", "hindustan-times-india", 1, "success", "one-shot source activation review"),
        ("set", "hindustan-times-india", False),
    ]
    assert "signals=1 snapshots=1 canonical=1 runs=1 db_enabled=False" in capsys.readouterr().out


def test_source_activation_does_not_touch_supabase_when_fetch_fails(monkeypatch, capsys) -> None:
    def fail(_source):
        raise RuntimeError("blocked")

    monkeypatch.setattr(source_activation, "fetch_signals", fail)
    assert source_activation.main(["--source", "hindustan-times-india"]) == 1
    assert "FAILED (blocked)" in capsys.readouterr().out
