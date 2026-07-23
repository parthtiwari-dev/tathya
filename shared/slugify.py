"""One tiny deterministic slugify helper, shared so topic and entity slugs
are generated the same way everywhere instead of drifting.
"""

import re


def slugify(text: str, max_length: int = 80) -> str:
    lowered = text.strip().lower()
    hyphenated = re.sub(r"[^a-z0-9]+", "-", lowered)
    trimmed = hyphenated.strip("-")
    collapsed = re.sub(r"-{2,}", "-", trimmed)
    return collapsed[:max_length].strip("-") or "topic"
