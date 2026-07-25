"""Persist case-file drafts into Supabase.

Defaults to Gemini-grounded generation with an automatic fallback to the
deterministic extractive builder per topic (see grounded_case_file_draft.py
and docs/audit_and_next_steps.md Section 7.2). Pass --extractive-only to skip
Gemini entirely, e.g. for a cheap/offline dry run or if GEMINI_API_KEY isn't
set in this environment.
"""

import argparse

from pipeline.generation.case_file_builder import build_case_file_draft
from pipeline.generation.grounded_case_file_draft import build_grounded_case_file_draft
from pipeline.generation.relations_builder import build_topic_relations
from pipeline.processing.clusterer import cluster_signals
from pipeline.storage.supabase_repository import SupabaseRepository


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Persist topic/event/claim/fact drafts.")
    parser.add_argument("--signals", type=int, default=300, help="Recent persisted signals to inspect.")
    parser.add_argument("--topics", type=int, default=5, help="Candidate topics to persist.")
    parser.add_argument("--promotable-only", action="store_true", help="Persist only clusters that pass the significance gate.")
    parser.add_argument("--extractive-only", action="store_true", help="Skip Gemini generation entirely; always use the deterministic extractive builder.")
    args = parser.parse_args(argv)

    repository = SupabaseRepository.from_environment()
    rows = repository.recent_signals(limit=args.signals)
    clusters = cluster_signals(rows, limit=args.topics)
    persisted = 0
    path_counts = {"grounded": 0, "extractive_fallback": 0, "extractive_only": 0}
    topic_drafts = []
    for cluster in clusters:
        if args.promotable_only and not cluster.significance.promotable:
            continue
        if args.extractive_only:
            draft, path = build_case_file_draft(cluster), "extractive_only"
        else:
            draft, path = build_grounded_case_file_draft(cluster)
        path_counts[path] += 1
        signal_ids = [row["id"] for row in cluster.rows if row.get("id")]
        topic_id = repository.persist_case_file_draft(draft, signal_ids)
        topic_drafts.append((topic_id, draft))
        persisted += 1
        print(f"[{path}] {draft.title}: persisted topic {topic_id} with {len(signal_ids)} signals, {len(draft.claims)} claims, {len(draft.events)} events, {len(draft.verifiable_facts)} facts")
    relations = build_topic_relations(topic_drafts)
    for relation in relations:
        repository.persist_topic_relation(relation.topic_id_a, relation.topic_id_b, relation.relation_type)
    if relations:
        print(f"Topic relations persisted: {len(relations)}")
    print(f"Total case-file drafts persisted: {persisted} (grounded: {path_counts['grounded']}, extractive fallback: {path_counts['extractive_fallback']}, extractive-only: {path_counts['extractive_only']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
