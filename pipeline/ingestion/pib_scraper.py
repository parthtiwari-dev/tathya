"""PIB press-release adapter.

PIB publishes an RSS endpoint, but it may reject automated requests. This module
keeps the access failure visible and provides a deterministic parser for captured
RSS payloads instead of silently substituting another source.
"""

from datetime import UTC, datetime
from urllib.request import Request, urlopen

from pipeline.ingestion.rss_watcher import parse_rss_entries
from shared.models import IngestedSignal, SourceDefinition, SourceType


def parse_pib_feed(source: SourceDefinition, payload: bytes) -> list[IngestedSignal]:
    if source.type is not SourceType.PIB:
        raise ValueError(f"Expected a PIB source, got {source.type!s}")
    # PIB's published endpoint is RSS; reuse the lossless parser with an RSS view.
    rss_source = source.model_copy(update={"type": SourceType.RSS})
    return parse_rss_entries(rss_source, payload)


def fetch_pib_signals(source: SourceDefinition) -> list[IngestedSignal]:
    if source.type is not SourceType.PIB:
        raise ValueError(f"Expected a PIB source, got {source.type!s}")
    request = Request(str(source.url), headers={"User-Agent": "Tathya/0.1 (+https://github.com/)"})
    with urlopen(request, timeout=30) as response:  # noqa: S310 -- URL is fixed project config.
        return parse_pib_feed(source, response.read())
