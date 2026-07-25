"""Applies the archive/reopen lifecycle transitions (roadmap Phase 5).

Archive direction: a live topic with no new signal in ARCHIVE_AFTER_DAYS gets
archived here.

Reopen direction is handled elsewhere, for free: whenever
pipeline/case_file_persist.py runs a promotable cluster that matches an
existing topic's title, upsert_topic_cluster's on-conflict clause (see
db/migrations/008_topic_status_promotion.sql) upgrades that topic straight
back to 'live', regardless of whether it was 'archived' or 'raw_cluster'
before -- so a dormant topic reopening on new signals needs no separate code
path here. This module only ever moves status in the archive direction.
"""

import argparse

from pipeline.lifecycle.activity_monitor import find_stale_live_topics
from pipeline.storage.supabase_repository import SupabaseRepository


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive live topics with no recent signal.")
    parser.add_argument(
        "--dry-run", action="store_true", help="Report what would be archived without writing."
    )
    args = parser.parse_args(argv)

    repository = SupabaseRepository.from_environment()
    stale = find_stale_live_topics(repository)

    if not stale:
        print("No stale live topics found.")
        return 0

    verb = "[dry-run] would archive" if args.dry_run else "archiving"
    for topic in stale:
        print(f"{verb}: {topic['title']} (last signal {topic['last_signal_at']})")

    if not args.dry_run:
        repository.archive_topics([topic["id"] for topic in stale])

    print(f"{'Would archive' if args.dry_run else 'Archived'} {len(stale)} topic(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
