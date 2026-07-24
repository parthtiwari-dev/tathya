"""Text normalization shared by ingestion and draft generation."""

import re

from html import unescape
from html.parser import HTMLParser

# Some sources (confirmed: RBI's RSS feed) double- or triple-HTML-escape embedded
# markup (e.g. tables), so a single unescape() call only partially decodes it and
# leaves literal "&lt;table...&gt;" sequences that HTMLParser can't recognize as
# tags. Unescape repeatedly until the string stops changing, capped to avoid an
# unbounded loop on adversarial input.
_MAX_UNESCAPE_PASSES = 5

# Safety net for malformed markup HTMLParser gives up on (e.g. an unterminated
# attribute quote) -- strip anything that still looks like a tag after parsing.
_RESIDUAL_TAG_RE = re.compile(r"<[^>\n]{1,300}>")


class _TextOnlyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data)


def _fully_unescape(value: str) -> str:
    for _ in range(_MAX_UNESCAPE_PASSES):
        unescaped = unescape(value)
        if unescaped == value:
            return unescaped
        value = unescaped
    return value


def clean_source_text(value: str | None) -> str:
    if not value:
        return ""
    decoded = _fully_unescape(value)
    parser = _TextOnlyParser()
    parser.feed(decoded)
    parsed = " ".join(parser.parts) if parser.parts else decoded
    parsed = _fully_unescape(parsed)
    parsed = _RESIDUAL_TAG_RE.sub(" ", parsed)
    return " ".join(parsed.split())
