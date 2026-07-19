"""Phase 2 significance scoring without political/editorial judgment."""

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class SignificanceBreakdown:
    score: float
    canonical_count: int
    independent_source_count: int
    official_source_present: bool
    media_or_citizen_source_present: bool
    velocity_24h: int
    promotable: bool


def score_topic(rows: list[dict], now: datetime | None = None) -> SignificanceBreakdown:
    """Score a candidate topic by volume, source diversity, and recency.

    This deliberately avoids any judgment about truth or political importance.
    Only canonical rows count toward volume/source criteria.
    """
    current_time = now or datetime.now(UTC)
    canonical_rows = [row for row in rows if not row.get("duplicate_of_signal_id")]
    source_keys = {_source_key(row) for row in canonical_rows}
    trust_categories = {_trust_category(row) for row in canonical_rows}
    velocity_24h = sum(1 for row in canonical_rows if _within_24h(row.get("published_at"), current_time))
    official_present = "official" in trust_categories
    non_official_present = bool(trust_categories & {"media", "citizen", "foreign"})
    score = len(canonical_rows) * 10 + len(source_keys) * 12 + velocity_24h * 2
    if official_present:
        score += 15
    if non_official_present:
        score += 10
    promotable = len(canonical_rows) >= 3 and len(source_keys) >= 2 and official_present and non_official_present
    return SignificanceBreakdown(
        score=score,
        canonical_count=len(canonical_rows),
        independent_source_count=len(source_keys),
        official_source_present=official_present,
        media_or_citizen_source_present=non_official_present,
        velocity_24h=velocity_24h,
        promotable=promotable,
    )


def _source_key(row: dict) -> str:
    source = row.get("sources") or {}
    return source.get("source_key") or "unknown"


def _trust_category(row: dict) -> str:
    source = row.get("sources") or {}
    return source.get("trust_category") or "unknown"


def _within_24h(value: str | None, now: datetime) -> bool:
    if not value:
        return False
    try:
        published = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    if published.tzinfo is None:
        published = published.replace(tzinfo=UTC)
    return 0 <= (now - published).total_seconds() <= 24 * 60 * 60
