"""Official website ingestion adapters for server-rendered public pages."""

from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from shared.models import IngestedSignal, SourceDefinition, SourceType


REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Tathya/0.1; +https://github.com/)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
}


@dataclass(frozen=True)
class OfficialArticle:
    url: str
    title: str


class _AnchorParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.articles: list[OfficialArticle] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag != "a":
            return
        attrs_dict = dict(attrs)
        href = attrs_dict.get("href")
        if href and "/en/news_updates/" in href and href.rstrip("/") != self.base_url.rstrip("/"):
            self._href = urljoin(self.base_url, href)
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href:
            title = _clean_text(" ".join(self._text))
            if title:
                self.articles.append(OfficialArticle(url=self._href, title=title))
            self._href = None
            self._text = []


class _PmIndiaArticleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title: str | None = None
        self.published_at: datetime | None = None
        self.paragraphs: list[str] = []
        self._current_tag: str | None = None
        self._buffer: list[str] = []
        self._seen_news_heading = False
        self._collecting_body = False
        self._stop_collecting = False

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"h2", "h4", "p", "blockquote"}:
            self._current_tag = tag
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._current_tag:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != self._current_tag:
            return
        text = _clean_text(" ".join(self._buffer))
        self._current_tag = None
        self._buffer = []
        if not text:
            return
        if tag == "h2" and not self.title and self._seen_news_heading:
            self.title = text
            return
        if tag in {"h2", "h4"} and text == "News Updates":
            self._seen_news_heading = True
            return
        if self.title and not self.published_at:
            parsed = _parse_pmindia_date(text)
            if parsed:
                self.published_at = parsed
                self._collecting_body = True
            return
        if text in {"Loading", "Popular News", "Recent News"}:
            self._stop_collecting = True
            return
        if self._collecting_body and not self._stop_collecting and tag in {"p", "blockquote"}:
            self.paragraphs.append(text)


def fetch_official_website_signals(source: SourceDefinition, limit: int = 10) -> list[IngestedSignal]:
    if source.type is not SourceType.OFFICIAL_WEBSITE:
        raise ValueError(f"Expected an official website source, got {source.type!s}")
    if "pmindia.gov.in/en/news-updates" not in str(source.url):
        raise NotImplementedError(f"No official website adapter is implemented for {source.url}")

    listing = _fetch(str(source.url))
    candidates = parse_pmindia_listing(source, listing)
    signals: list[IngestedSignal] = []
    for article in candidates[:limit]:
        detail_payload = _fetch(article.url)
        signal = parse_pmindia_article(source, article.url, detail_payload, fallback_title=article.title)
        if signal:
            signals.append(signal)
    return signals


def parse_pmindia_listing(source: SourceDefinition, payload: bytes) -> list[OfficialArticle]:
    if source.type is not SourceType.OFFICIAL_WEBSITE:
        raise ValueError(f"Expected an official website source, got {source.type!s}")
    parser = _AnchorParser(str(source.url))
    parser.feed(payload.decode("utf-8", errors="replace"))
    seen: set[str] = set()
    articles: list[OfficialArticle] = []
    for article in parser.articles:
        canonical = article.url.split("?")[0].rstrip("/") + "/?comment=disable"
        if canonical in seen:
            continue
        seen.add(canonical)
        articles.append(OfficialArticle(url=canonical, title=article.title))
    return articles


def parse_pmindia_article(source: SourceDefinition, url: str, payload: bytes, fallback_title: str | None = None) -> IngestedSignal | None:
    if source.type is not SourceType.OFFICIAL_WEBSITE:
        raise ValueError(f"Expected an official website source, got {source.type!s}")
    parser = _PmIndiaArticleParser()
    parser.feed(payload.decode("utf-8", errors="replace"))
    title = parser.title or fallback_title
    raw_text = "\n\n".join(parser.paragraphs)
    if not title or not raw_text:
        return None
    return IngestedSignal(
        source_key=source.key,
        source_url=source.url,
        canonical_url=url,
        published_at=parser.published_at or datetime.now(UTC),
        raw_text=raw_text,
        title=title,
    )


def _fetch(url: str) -> bytes:
    request = Request(url, headers=REQUEST_HEADERS)
    with urlopen(request, timeout=30) as response:  # noqa: S310 -- URL is fixed project config.
        return response.read()


def _parse_pmindia_date(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, "%d %b, %Y").replace(tzinfo=UTC)
    except ValueError:
        return None


def _clean_text(value: str) -> str:
    return " ".join(value.split())
