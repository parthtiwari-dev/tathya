"""YouTube transcript adapter for videos that expose captions."""

from datetime import UTC, datetime
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

import feedparser
from youtube_transcript_api import YouTubeTranscriptApi

from shared.models import IngestedSignal, SourceDefinition, SourceType


def extract_video_id(video_url: str) -> str:
    parsed = urlparse(video_url)
    if parsed.hostname in {"youtu.be", "www.youtu.be"}:
        video_id = parsed.path.strip("/").split("/")[0]
    else:
        video_id = parse_qs(parsed.query).get("v", [""])[0]
    if len(video_id) != 11:
        raise ValueError(f"Could not extract a YouTube video id from {video_url}")
    return video_id


def fetch_transcript(video_id: str, languages: tuple[str, ...] = ("en", "hi")) -> str:
    transcript = YouTubeTranscriptApi().fetch(video_id, languages=list(languages))
    pieces = [getattr(item, "text", item.get("text", "")) for item in transcript]
    text = " ".join(piece.strip() for piece in pieces if piece.strip())
    if not text:
        raise RuntimeError(f"YouTube video {video_id} returned an empty transcript")
    return text


def build_youtube_signal(source: SourceDefinition, video_url: str, title: str, published_at: datetime, transcript: str | None) -> IngestedSignal:
    if source.type is not SourceType.YOUTUBE:
        raise ValueError(f"Expected a YouTube source, got {source.type!s}")
    extract_video_id(video_url)
    return IngestedSignal(
        source_key=source.key,
        source_url=source.url,
        canonical_url=video_url,
        published_at=published_at,
        raw_text=title,
        title=title,
        transcript=transcript,
    )


def fetch_youtube_signals(source: SourceDefinition) -> list[IngestedSignal]:
    """Read a configured channel's public Atom feed and fetch captions per video.

    A video without captions remains a signal with ``transcript=None``. It is not
    discarded and can later use the roadmap's Supadata fallback.
    """
    if source.type is not SourceType.YOUTUBE:
        raise ValueError(f"Expected a YouTube source, got {source.type!s}")
    request = Request(str(source.url), headers={"User-Agent": "Tathya/0.1 (+https://github.com/)"})
    with urlopen(request, timeout=30) as response:  # noqa: S310 -- URL is fixed project config.
        feed = feedparser.parse(response.read())
    if feed.bozo:
        raise RuntimeError(f"Could not parse YouTube feed for {source.name}: {feed.bozo_exception}")

    signals: list[IngestedSignal] = []
    for entry in feed.entries:
        video_id = entry.get("yt_videoid")
        if not video_id:
            continue
        video_url = entry.get("link") or f"https://www.youtube.com/watch?v={video_id}"
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        published_at = datetime(*published[:6], tzinfo=UTC) if published else datetime.now(UTC)
        try:
            transcript = fetch_transcript(video_id)
        except Exception:
            transcript = None
        signals.append(build_youtube_signal(source, video_url, entry.get("title") or video_id, published_at, transcript))
    return signals
