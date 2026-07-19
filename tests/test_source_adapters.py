from datetime import UTC, datetime

import pytest

from pipeline.ingestion.parliament_scraper import parse_parliament_html
from pipeline.ingestion.pib_scraper import parse_pib_feed
from pipeline.ingestion import youtube_watcher
from pipeline.ingestion.dispatcher import fetch_signals
from pipeline.ingestion.youtube_watcher import build_youtube_signal, extract_video_id
from shared.models import SourceDefinition, SourceType, TrustCategory


def test_pib_parser_preserves_source_text() -> None:
    source = SourceDefinition(key="pib", name="PIB", type=SourceType.PIB, url="https://pib.gov.in/feed", trust_category=TrustCategory.OFFICIAL)
    payload = b'<rss><channel><item><title>Release</title><link>https://pib.gov.in/release/1</link><description>Official text.</description></item></channel></rss>'
    assert parse_pib_feed(source, payload)[0].raw_text == "Official text."


def test_parliament_parser_requires_rows_and_preserves_cells() -> None:
    source = SourceDefinition(key="ls", name="Lok Sabha", type=SourceType.PARLIAMENT, url="https://sansad.in/ls/questions/questions-and-answers", trust_category=TrustCategory.OFFICIAL)
    payload = b"<table><tr><th>Q.No</th><th>Subject</th></tr><tr><td>1</td><td>Water policy</td></tr></table>"
    signal = parse_parliament_html(source, payload)[0]
    assert signal.title == "Subject"
    assert signal.raw_text == "Q.No | Subject"

    with pytest.raises(RuntimeError, match="No server-rendered"):
        parse_parliament_html(source, b"<html>client-rendered</html>")


def test_youtube_signal_and_video_id() -> None:
    source = SourceDefinition(key="yt", name="Official YouTube", type=SourceType.YOUTUBE, url="https://youtube.com/@official", trust_category=TrustCategory.OFFICIAL)
    assert extract_video_id("https://www.youtube.com/watch?v=abcdefghijk") == "abcdefghijk"
    signal = build_youtube_signal(source, "https://youtu.be/abcdefghijk", "Speech", datetime(2026, 7, 19, tzinfo=UTC), "Transcript")
    assert signal.transcript == "Transcript"


def test_youtube_feed_keeps_video_when_captions_are_unavailable(monkeypatch) -> None:
    source = SourceDefinition(key="yt", name="Official YouTube", type=SourceType.YOUTUBE, url="https://www.youtube.com/feeds/videos.xml?channel_id=abc", trust_category=TrustCategory.OFFICIAL)

    class Response:
        def read(self) -> bytes:
            return b'''<feed xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015"><entry><yt:videoId>abcdefghijk</yt:videoId><title>Briefing</title><link href="https://www.youtube.com/watch?v=abcdefghijk" /></entry></feed>'''
        def __enter__(self): return self
        def __exit__(self, *_args): return None

    monkeypatch.setattr(youtube_watcher, "urlopen", lambda *_args, **_kwargs: Response())
    monkeypatch.setattr(youtube_watcher, "fetch_transcript", lambda *_args: (_ for _ in ()).throw(RuntimeError("disabled")))
    signals = youtube_watcher.fetch_youtube_signals(source)
    assert signals[0].title == "Briefing"
    assert signals[0].transcript is None


def test_dispatcher_selects_pib_adapter(monkeypatch) -> None:
    source = SourceDefinition(key="pib", name="PIB", type=SourceType.PIB, url="https://pib.gov.in/feed", trust_category=TrustCategory.OFFICIAL)
    monkeypatch.setattr("pipeline.ingestion.dispatcher.fetch_pib_signals", lambda selected: ["ok"])
    assert fetch_signals(source) == ["ok"]
