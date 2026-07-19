"""RSS ingestion adapter; persistence is added after Supabase setup."""

from datetime import UTC, datetime

import feedparser

from shared.models import IngestedSignal, SourceDefinition, SourceType


def fetch_rss_signals(source: SourceDefinition) -> list[IngestedSignal]:
    """Fetch a verified RSS source and return raw entries without topic filtering."""
    if source.type is not SourceType.RSS:
        raise ValueError(f"Expected an RSS source, got {source.type!s}")
    feed = feedparser.parse(str(source.url))
    if feed.bozo:
        raise RuntimeError(f"Could not parse RSS feed for {source.name}: {feed.bozo_exception}")
    signals: list[IngestedSignal] = []
    for entry in feed.entries:
        text = entry.get("summary") or entry.get("description") or entry.get("title")
        link = entry.get("link")
        if not text or not link:
            continue
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        published_at = datetime(*published[:6], tzinfo=UTC) if published else datetime.now(UTC)
        signals.append(IngestedSignal(source_key=source.key, source_url=source.url, canonical_url=link, published_at=published_at, raw_text=text, title=entry.get("title")))
    return signals
