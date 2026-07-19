"""Create deterministic immutable source snapshots at ingestion time."""

from datetime import UTC, datetime
from hashlib import sha256

from shared.models import IngestedSignal, SnapshotRecord


def build_snapshot(signal: IngestedSignal, *, captured_at: datetime | None = None) -> SnapshotRecord:
    """Capture exactly the raw material used to create a signal."""
    captured = captured_at or datetime.now(UTC)
    if captured.tzinfo is None:
        raise ValueError("captured_at must be timezone-aware")
    raw_content = signal.raw_text if signal.transcript is None else f"{signal.raw_text}\n\n{signal.transcript}"
    return SnapshotRecord(
        captured_at=captured,
        raw_content=raw_content,
        content_hash=sha256(raw_content.encode("utf-8")).hexdigest(),
    )
