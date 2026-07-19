"""CLI for reviewing and optionally marking near-duplicate signals."""

import argparse

from pipeline.processing.near_duplicate import find_near_duplicates
from pipeline.storage.supabase_repository import SupabaseRepository


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review near-duplicate recent signals.")
    parser.add_argument("--signals", type=int, default=300, help="Recent persisted signals to inspect.")
    parser.add_argument("--threshold", type=float, default=0.82, help="Token-overlap threshold for candidate pairs.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum candidate pairs to print or apply.")
    parser.add_argument("--apply", action="store_true", help="Mark printed candidates as duplicates in Supabase.")
    args = parser.parse_args(argv)

    repository = SupabaseRepository.from_environment()
    rows = repository.recent_signals(limit=args.signals)
    candidates = find_near_duplicates(rows, threshold=args.threshold)[: args.limit]

    print(f"Inspected {len(rows)} recent signals")
    print(f"Near-duplicate candidates: {len(candidates)}")
    for index, candidate in enumerate(candidates, start=1):
        print(f"\n{index}. similarity={candidate.similarity:.3f}")
        print(f"   canonical: {candidate.canonical_title}")
        print(f"   canonical_url: {candidate.canonical_url}")
        print(f"   duplicate: {candidate.duplicate_title}")
        print(f"   duplicate_url: {candidate.duplicate_url}")
        if args.apply:
            repository.mark_signal_duplicate(candidate.duplicate_signal_id, candidate.canonical_signal_id)
            print("   applied: duplicate_of_signal_id updated")

    if not args.apply:
        print("\nReview candidates first. Re-run with --apply only when they are clearly wire-copy or near-duplicate records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
