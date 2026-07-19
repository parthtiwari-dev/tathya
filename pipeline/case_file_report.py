"""CLI for private Phase 3 extractive case-file drafts."""

import argparse
import json
from dataclasses import asdict

from pipeline.cli_encoding import ensure_utf8_stdout
from pipeline.generation.case_file_builder import build_case_file_draft
from pipeline.processing.clusterer import cluster_signals
from pipeline.storage.supabase_repository import SupabaseRepository


def main(argv: list[str] | None = None) -> int:
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="Build private extractive case-file drafts from recent signals.")
    parser.add_argument("--signals", type=int, default=300, help="Recent persisted signals to inspect.")
    parser.add_argument("--topics", type=int, default=5, help="Draft case files to print.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of readable text.")
    args = parser.parse_args(argv)

    rows = SupabaseRepository.from_environment().recent_signals(limit=args.signals)
    clusters = cluster_signals(rows, limit=args.topics)
    drafts = [build_case_file_draft(cluster) for cluster in clusters]
    if args.json:
        print(json.dumps([asdict(draft) for draft in drafts], indent=2))
        return 0

    print(f"Inspected {len(rows)} recent signals")
    print(f"Case-file drafts: {len(drafts)}")
    for index, draft in enumerate(drafts, start=1):
        print(f"\n{index}. {draft.title}")
        print(f"   score: {draft.significance_score:g} promotable: {draft.promotable}")
        print(f"   summary: {draft.neutral_summary}")
        print(f"   entities: {', '.join(draft.related_entities) if draft.related_entities else 'none'}")
        print(f"   events: {len(draft.events)} claims: {len(draft.claims)} facts: {len(draft.verifiable_facts)}")
        for claim in draft.claims[:3]:
            print(f"   claim[{claim.source_type}]: {claim.quoted_span}")
            print(f"      url: {claim.source_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
