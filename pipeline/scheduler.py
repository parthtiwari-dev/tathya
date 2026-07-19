"""Phase 1 command entrypoint for configured RSS sources."""

import argparse

from pipeline.ingestion.dispatcher import fetch_signals
from pipeline.processing.snapshotter import build_snapshot
from pipeline.monitoring.health_check import assess_signal_count
from pipeline.monitoring.telegram import send_alert
from pipeline.storage.supabase_repository import SupabaseRepository
from shared.config import STARTER_SOURCES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch configured RSS sources without topic curation.")
    parser.add_argument("--persist", action="store_true", help="Persist signals and snapshots to Supabase.")
    parser.add_argument("--test-alert", action="store_true", help="Send a Telegram test alert and exit.")
    args = parser.parse_args(argv)
    if args.test_alert:
        delivered = send_alert("Tathya test alert: Telegram notifications are configured correctly.")
        print("Telegram test alert sent" if delivered else "Telegram credentials are missing or alert delivery failed")
        return 0 if delivered else 1
    repository = SupabaseRepository.from_environment() if args.persist else None
    total = 0
    failed_sources = 0
    for source in STARTER_SOURCES:
        if not source.enabled:
            continue
        try:
            signals = fetch_signals(source)
        except Exception as error:  # A broken source must not stop all other watchers.
            failed_sources += 1
            if repository:
                repository.record_source_run(source.key, 0, "failure", str(error))
            send_alert(f"Tathya watcher failed: {source.key}\n{error}")
            print(f"{source.key}: FAILED ({error})")
            continue
        assessment = assess_signal_count(source.key, len(signals), repository.recent_source_counts(source.key) if repository else [])
        if repository:
            for signal in signals:
                repository.persist_signal(signal)
            print(f"{source.key}: {len(signals)} signals persisted")
        else:
            snapshots = [build_snapshot(signal) for signal in signals]
            print(f"{source.key}: {len(snapshots)} signals prepared")
        if repository:
            repository.record_source_run(source.key, len(signals), "success")
        if assessment.is_abnormal_drop:
            message = f"Tathya source alert: {source.key} produced {len(signals)} signals vs recent median {assessment.baseline_count:g}"
            print(f"ALERT {message}")
            send_alert(message)
        total += len(signals)
    verb = "persisted" if repository else "prepared"
    print(f"Total signals {verb}: {total}")
    return 1 if failed_sources else 0


if __name__ == "__main__":
    raise SystemExit(main())
