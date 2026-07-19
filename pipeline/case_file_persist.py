"""Persist private extractive case-file drafts into Supabase."""

import argparse

from pipeline.generation.case_file_builder import build_case_file_draft
from pipeline.generation.relations_builder import build_topic_relations
from pipeline.processing.clusterer import cluster_signals
from pipeline.storage.supabase_repository import SupabaseRepository


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Persist extractive topic/event/claim/fact drafts.")
    parser.add_argument("--signals", type=int, default=300, help="Recent persisted signals to inspect.")
    parser.add_argument("--topics", type=int, default=5, help="Candidate topics to persist.")
    parser.add_argument("--promotable-only", action="store_true", help="Persist only clusters that pass the significance gate.")
    args = parser.parse_args(argv)

    repository = SupabaseRepository.from_environment()
    rows = repository.recent_signals(limit=args.signals)
    clusters = cluster_signals(rows, limit=args.topics)
    persisted = 0
    topic_drafts = []
    for cluster in clusters:
        if args.promotable_only and not cluster.significance.promotable:
            continue
        draft = build_case_file_draft(cluster)
        signal_ids = [row["id"] for row in cluster.rows if row.get("id")]
        topic_id = repository.persist_case_file_draft(draft, signal_ids)
        topic_drafts.append((topic_id, draft))
        persisted += 1
        print(f"{draft.title}: persisted topic {topic_id} with {len(signal_ids)} signals, {len(draft.claims)} claims, {len(draft.events)} events, {len(draft.verifiable_facts)} facts")
    relations = build_topic_relations(topic_drafts)
    for relation in relations:
        repository.persist_topic_relation(relation.topic_id_a, relation.topic_id_b, relation.relation_type)
    if relations:
        print(f"Topic relations persisted: {len(relations)}")
    print(f"Total case-file drafts persisted: {persisted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
