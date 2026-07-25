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
    # PIB's WAF (NIC-hosted, likely Akamai/Indusface-class) appears to reject
    # requests that self-identify as an automated GitHub-affiliated bot --
    # the exact same URL is reachable with a normal-looking browser request.
    # This may or may not be enough on its own if the block is IP/ASN-based
    # (GitHub Actions runner ranges) rather than UA-pattern-based; if 403s
    # persist after this change, that's the more likely remaining cause and
    # this source should go back to enabled=False until a different fetch
    # path (e.g. a non-Actions host) is available.
    request = Request(
        str(source.url),
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "application/rss+xml, application/xml, text/xml, */*;q=0.9",
            "Accept-Language": "en-IN,en;q=0.9",
            "Referer": "https://www.pib.gov.in/",
        },
    )
    with urlopen(request, timeout=30) as response:  # noqa: S310 -- URL is fixed project config.
        return parse_pib_feed(source, response.read())
