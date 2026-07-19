"""Text normalization shared by ingestion and draft generation."""

from html import unescape
from html.parser import HTMLParser


class _TextOnlyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data)


def clean_source_text(value: str | None) -> str:
    if not value:
        return ""
    parser = _TextOnlyParser()
    parser.feed(unescape(value))
    parsed = " ".join(parser.parts) if parser.parts else unescape(value)
    return " ".join(parsed.split())
