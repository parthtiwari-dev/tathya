"""Phase 1 command entrypoint for fetching configured RSS sources.

This command is intentionally dry-run only until a Supabase project has been
configured. It proves that the source layer produces snapshots without choosing
or filtering topics.
"""

from pipeline.ingestion.rss_watcher import fetch_rss_signals
from pipeline.processing.snapshotter import build_snapshot
from shared.config import STARTER_SOURCES
from shared.models import SourceType


def main() -> int:
    total = 0
    failed_sources = 0
    for source in STARTER_SOURCES:
        if not source.enabled or source.type is not SourceType.RSS:
            continue
        try:
            signals = fetch_rss_signals(source)
        except Exception as error:  # A broken source must not stop all other watchers.
            failed_sources += 1
            print(f"{source.key}: FAILED ({error})")
            continue
        snapshots = [build_snapshot(signal) for signal in signals]
        print(f"{source.key}: {len(snapshots)} signals prepared")
        total += len(snapshots)
    print(f"Total signals prepared: {total}")
    return 1 if failed_sources else 0


if __name__ == "__main__":
    raise SystemExit(main())
