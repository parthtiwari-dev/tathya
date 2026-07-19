from datetime import UTC, datetime

import pytest

from pipeline.processing.snapshotter import build_snapshot
from shared.models import IngestedSignal


def test_snapshot_keeps_raw_content_and_has_stable_hash() -> None:
    signal = IngestedSignal(source_key="example-news", source_url="https://example.com/feed.xml", canonical_url="https://example.com/article", published_at=datetime(2026, 7, 19, tzinfo=UTC), raw_text="A source statement.", transcript="A caption transcript.")
    snapshot = build_snapshot(signal, captured_at=datetime(2026, 7, 19, 12, tzinfo=UTC))
    assert snapshot.raw_content == "A source statement.\n\nA caption transcript."
    assert snapshot.content_hash == "0295f500cc438b555f04b81d12ab5852af311992a1842c9c7dcd013f752cd1cc"


def test_snapshot_rejects_naive_capture_time() -> None:
    signal = IngestedSignal(source_key="example-news", source_url="https://example.com/feed.xml", canonical_url="https://example.com/article", published_at=datetime(2026, 7, 19, tzinfo=UTC), raw_text="A source statement.")
    with pytest.raises(ValueError, match="timezone-aware"):
        build_snapshot(signal, captured_at=datetime(2026, 7, 19))
