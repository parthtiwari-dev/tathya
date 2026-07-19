from pipeline.ingestion import rss_watcher
from pipeline.ingestion.rss_watcher import parse_rss_entries
from shared.models import SourceDefinition, SourceType, TrustCategory


def test_parse_rss_entries_does_not_filter_or_rewrite_source_text() -> None:
    source = SourceDefinition(
        key="test-feed",
        name="Test feed",
        type=SourceType.RSS,
        url="https://example.com/feed.xml",
        trust_category=TrustCategory.MEDIA,
    )
    payload = b'''<?xml version="1.0"?><rss version="2.0"><channel><title>T</title>
      <item><title>A record</title><link>https://example.com/a</link>
      <description>Original source text.</description><pubDate>Sat, 19 Jul 2026 12:00:00 GMT</pubDate></item>
    </channel></rss>'''

    signals = parse_rss_entries(source, payload)

    assert len(signals) == 1
    assert signals[0].title == "A record"
    assert signals[0].raw_text == "Original source text."
    assert str(signals[0].canonical_url) == "https://example.com/a"


def test_fetch_rss_signals_uses_a_transparent_identifying_user_agent(monkeypatch) -> None:
    source = SourceDefinition(key="test-feed", name="Test feed", type=SourceType.RSS, url="https://example.com/feed.xml", trust_category=TrustCategory.MEDIA)

    class Response:
        def read(self) -> bytes:
            return b'<?xml version="1.0"?><rss version="2.0"><channel /></rss>'

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    def fake_urlopen(request, timeout):
        assert request.headers["User-agent"].startswith("Tathya/")
        assert timeout == 30
        return Response()

    monkeypatch.setattr(rss_watcher, "urlopen", fake_urlopen)
    assert rss_watcher.fetch_rss_signals(source) == []


def test_parse_rss_entries_prefers_full_content_when_available() -> None:
    source = SourceDefinition(
        key="official-feed",
        name="Official feed",
        type=SourceType.RSS,
        url="https://example.gov/feed.xml",
        trust_category=TrustCategory.OFFICIAL,
    )
    payload = b'''<?xml version="1.0"?><rss version="2.0"
      xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel>
      <item><title>Short title</title><link>https://example.gov/a</link>
      <description>Short summary.</description>
      <content:encoded>Longer official body text.</content:encoded></item>
    </channel></rss>'''

    signals = parse_rss_entries(source, payload)

    assert signals[0].raw_text == "Longer official body text."
