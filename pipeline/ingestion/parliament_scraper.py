"""Parser for tabular Digital Sansad question pages.

Digital Sansad pages are partly client-rendered. The parser accepts a server
rendered table when available and fails explicitly when the page contains no
records, so a frontend redesign cannot produce fabricated parliamentary data.
"""

from datetime import UTC, datetime
from html.parser import HTMLParser
from urllib.request import Request, urlopen

from shared.models import IngestedSignal, SourceDefinition, SourceType


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "tr":
            self._row = []
        elif tag in {"td", "th"} and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._cell is not None and self._row is not None:
            value = " ".join("".join(self._cell).split())
            self._row.append(value)
            self._cell = None
        elif tag == "tr" and self._row:
            self.rows.append(self._row)
            self._row = None


def parse_parliament_html(source: SourceDefinition, payload: bytes) -> list[IngestedSignal]:
    if source.type is not SourceType.PARLIAMENT:
        raise ValueError(f"Expected a Parliament source, got {source.type!s}")
    parser = _TableParser()
    parser.feed(payload.decode("utf-8", errors="replace"))
    rows = [row for row in parser.rows if len(row) >= 2 and any(row)]
    if not rows:
        raise RuntimeError(f"No server-rendered question rows found for {source.name}; page needs a structured API adapter")
    now = datetime.now(UTC)
    return [
        IngestedSignal(
            source_key=source.key,
            source_url=source.url,
            canonical_url=f"{source.url}#question-{index}",
            published_at=now,
            raw_text=" | ".join(row),
            title=row[1] if len(row) > 1 else row[0],
        )
        for index, row in enumerate(rows, start=1)
    ]


def fetch_parliament_signals(source: SourceDefinition) -> list[IngestedSignal]:
    request = Request(str(source.url), headers={"User-Agent": "Tathya/0.1 (+https://github.com/)"})
    with urlopen(request, timeout=30) as response:  # noqa: S310 -- URL is fixed project config.
        return parse_parliament_html(source, response.read())
