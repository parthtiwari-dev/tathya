"""RSS ingestion adapter; persistence is added after Supabase setup."""

from datetime import UTC, datetime
from time import struct_time
from urllib.request import Request, urlopen

import feedparser

from pipeline.processing.text_cleaner import clean_source_text
from shared.models import IngestedSignal, SourceDefinition, SourceType


def parse_rss_entries(source: SourceDefinition, payload: bytes) -> list[IngestedSignal]:
    """Convert one RSS/Atom payload into raw signals without topic filtering."""
    if source.type is not SourceType.RSS:
        raise ValueError(f"Expected an RSS source, got {source.type!s}")
    feed = feedparser.parse(payload)
    if feed.bozo:
        raise RuntimeError(f"Could not parse RSS feed for {source.name}: {feed.bozo_exception}")
    signals: list[IngestedSignal] = []
    for entry in feed.entries:
        text = _entry_text(entry)
        link = entry.get("link")
        if not text or not link:
            continue
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        published_at = _to_datetime(published) if published else datetime.now(UTC)
        signals.append(IngestedSignal(source_key=source.key, source_url=source.url, canonical_url=link, published_at=published_at, raw_text=clean_source_text(text), title=clean_source_text(entry.get("title")) or None))
    return signals


def fetch_rss_signals(source: SourceDefinition) -> list[IngestedSignal]:
    """Fetch a configured RSS source and return its raw entries."""
    request = Request(str(source.url), headers={"User-Agent": "Tathya/0.1 (+https://github.com/)"})
    with urlopen(request, timeout=30) as response:  # noqa: S310 -- URL is fixed project config.
        return parse_rss_entries(source, response.read())


def _to_datetime(value: struct_time) -> datetime:
    return datetime(*value[:6], tzinfo=UTC)


def _entry_text(entry) -> str | None:
    content_items = entry.get("content") or []
    content_values = [item.get("value", "") for item in content_items if item.get("value")]
    return next(
        (
            candidate
            for candidate in [*content_values, entry.get("summary"), entry.get("description"), entry.get("title")]
            if candidate
        ),
        None,
    )
