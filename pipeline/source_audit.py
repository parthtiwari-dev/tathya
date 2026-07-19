"""Local source validation helpers for Phase 1 activation reviews."""

import argparse

from pipeline.ingestion.dispatcher import fetch_signals
from pipeline.processing.snapshotter import build_snapshot
from shared.config import STARTER_SOURCES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect configured sources without persistence.")
    parser.add_argument("--list", action="store_true", help="List configured sources and activation state.")
    parser.add_argument("--source", help="Source key to fetch even if disabled.")
    parser.add_argument("--limit", type=int, default=10, help="Number of fetched rows to print.")
    args = parser.parse_args(argv)

    sources = {source.key: source for source in STARTER_SOURCES}
    if args.list:
        for source in STARTER_SOURCES:
            state = "enabled" if source.enabled else "disabled"
            print(f"{source.key}\t{state}\t{source.type}\t{source.trust_category}\t{source.url}")
        return 0

    if not args.source:
        parser.error("--source is required unless --list is used")
    source = sources.get(args.source)
    if source is None:
        known = ", ".join(sorted(sources))
        raise SystemExit(f"Unknown source '{args.source}'. Known sources: {known}")

    try:
        signals = fetch_signals(source)
    except Exception as error:
        print(f"{source.key}: FAILED ({error})")
        return 1
    print(f"{source.key}: fetched {len(signals)} signals")
    for index, signal in enumerate(signals[: args.limit], start=1):
        snapshot = build_snapshot(signal)
        title = signal.title or signal.raw_text[:80]
        print(f"\n{index}. {title}")
        print(f"   published_at: {signal.published_at.isoformat()}")
        print(f"   url: {signal.canonical_url}")
        print(f"   text_chars: {len(signal.raw_text)}")
        print(f"   transcript_chars: {len(signal.transcript or '')}")
        print(f"   content_hash: {snapshot.content_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
