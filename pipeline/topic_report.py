"""CLI for the first private Phase 2 candidate-topic report."""

import argparse

from pipeline.processing.topic_report import build_candidate_topics
from pipeline.storage.supabase_repository import SupabaseRepository


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a private candidate-topic report from recent signals.")
    parser.add_argument("--signals", type=int, default=250, help="Recent persisted signals to inspect.")
    parser.add_argument("--topics", type=int, default=10, help="Candidate topics to print.")
    args = parser.parse_args(argv)

    repository = SupabaseRepository.from_environment()
    rows = repository.recent_signals(limit=args.signals)
    candidates = build_candidate_topics(rows, limit=args.topics)
    print(f"Inspected {len(rows)} recent signals")
    print(f"Candidate topics: {len(candidates)}")
    for index, candidate in enumerate(candidates, start=1):
        print(f"\n{index}. {candidate.key}")
        print(f"   score: {candidate.score}")
        print(f"   signals: {candidate.signal_count} canonical: {candidate.canonical_count}")
        print(f"   sources: {', '.join(candidate.source_keys)}")
        print(f"   entities: {', '.join(candidate.top_entities) if candidate.top_entities else 'none'}")
        for url in candidate.representative_urls:
            print(f"   url: {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
