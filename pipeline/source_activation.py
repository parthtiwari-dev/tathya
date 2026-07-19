"""Persist one disabled source once for manual Supabase inspection."""

import argparse

from pipeline.ingestion.dispatcher import fetch_signals
from pipeline.storage.supabase_repository import SupabaseRepository
from shared.config import STARTER_SOURCES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Persist one configured source once for activation review.")
    parser.add_argument("--source", required=True, help="Source key to activate locally.")
    parser.add_argument("--limit", type=int, default=200, help="Maximum fetched signals to persist.")
    parser.add_argument("--keep-db-enabled", action="store_true", help="Leave the source enabled in Supabase after the one-shot run.")
    args = parser.parse_args(argv)

    sources = {source.key: source for source in STARTER_SOURCES}
    source = sources.get(args.source)
    if source is None:
        known = ", ".join(sorted(sources))
        raise SystemExit(f"Unknown source '{args.source}'. Known sources: {known}")

    print(f"{source.key}: fetching candidate source")
    try:
        signals = fetch_signals(source)[: args.limit]
    except Exception as error:
        print(f"{source.key}: FAILED ({error})")
        return 1
    if not signals:
        print(f"{source.key}: no signals fetched; not changing Supabase")
        return 1

    repository = SupabaseRepository.from_environment()
    previous_enabled = repository.set_source_enabled(source.key, True)
    print(f"{source.key}: Supabase source temporarily enabled")
    try:
        for signal in signals:
            repository.persist_signal(signal)
        repository.record_source_run(source.key, len(signals), "success", "one-shot source activation review")
    finally:
        if not args.keep_db_enabled:
            repository.set_source_enabled(source.key, previous_enabled)
            print(f"{source.key}: Supabase source restored to enabled={previous_enabled}")

    print(f"{source.key}: {len(signals)} signals persisted for manual inspection")
    summary = repository.source_activation_summary(source.key)
    if summary:
        print(
            "summary: "
            f"signals={summary['signal_count']} "
            f"snapshots={summary['snapshot_count']} "
            f"canonical={summary['canonical_signal_count']} "
            f"runs={summary['source_run_count']} "
            f"db_enabled={summary['enabled']}"
        )
    print("Next: inspect this source in Supabase before enabling it in shared/config.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
