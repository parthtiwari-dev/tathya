"""Small CLI compatibility helpers."""

import sys


def ensure_utf8_stdout() -> None:
    """Prefer UTF-8 CLI output on Windows terminals with legacy encodings."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
