"""CLI for the first private Phase 2 candidate-topic report."""

import argparse

from pipeline.processing.clusterer import cluster_signals
from pipeline.storage.supabase_repository import SupabaseRepository


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a private candidate-topic report from recent signals.")
    parser.add_argument("--signals", type=int, default=250, help="Recent persisted signals to inspect.")
    parser.add_argument("--topics", type=int, default=10, help="Candidate topics to print.")
    args = parser.parse_args(argv)

    repository = SupabaseRepository.from_environment()
    rows = repository.recent_signals(limit=args.signals)
    candidates = cluster_signals(rows, limit=args.topics)
    print(f"Inspected {len(rows)} recent signals")
    print(f"Candidate topics: {len(candidates)}")
    for index, candidate in enumerate(candidates, start=1):
        print(f"\n{index}. {candidate.key}")
        print(f"   score: {candidate.significance.score:g} promotable: {candidate.significance.promotable}")
        print(f"   signals: {len(candidate.rows)} canonical: {candidate.significance.canonical_count}")
        print(f"   sources: {candidate.significance.independent_source_count}")
        print(f"   official+nonofficial: {candidate.significance.official_source_present}/{candidate.significance.media_or_citizen_source_present}")
        print(f"   duplicate_pairs_nearby: {candidate.duplicate_pairs}")
        print(f"   entities: {', '.join(candidate.entities) if candidate.entities else 'none'}")
        for url in _representative_urls(candidate.rows):
            print(f"   url: {url}")
    return 0


def _representative_urls(rows) -> list[str]:
    urls = []
    for row in rows:
        url = row.get("url")
        if url and url not in urls:
            urls.append(url)
    return urls[:3]


if __name__ == "__main__":
    raise SystemExit(main())
