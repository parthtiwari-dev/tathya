"""Phase 2 candidate clustering over recent persisted signals."""

from collections import defaultdict
from dataclasses import dataclass

from pipeline.processing.entity_matcher import match_entities
from pipeline.processing.near_duplicate import find_near_duplicates
from pipeline.processing.significance_scorer import SignificanceBreakdown, score_topic


@dataclass(frozen=True)
class TopicCluster:
    key: str
    rows: tuple[dict, ...]
    entities: tuple[str, ...]
    duplicate_pairs: int
    significance: SignificanceBreakdown


def cluster_signals(signal_rows: list[dict], limit: int = 10) -> list[TopicCluster]:
    duplicate_pairs = find_near_duplicates(signal_rows)
    duplicate_ids = {candidate.duplicate_signal_id for candidate in duplicate_pairs}
    buckets: dict[str, list[dict]] = defaultdict(list)
    entities_by_bucket: dict[str, set[str]] = defaultdict(set)

    for row in signal_rows:
        if row.get("id") in duplicate_ids or row.get("duplicate_of_signal_id"):
            continue
        text = signal_text(row)
        matches = match_entities(text)
        if matches:
            bucket_key = matches[0].name
            for entity in matches:
                entities_by_bucket[bucket_key].add(entity.name)
        else:
            bucket_key = fallback_bucket(row)
        buckets[bucket_key].append(row)

    clusters = [
        TopicCluster(
            key=key,
            rows=tuple(rows),
            entities=tuple(sorted(entities_by_bucket[key])),
            duplicate_pairs=_duplicate_count_for_rows(rows, duplicate_pairs),
            significance=score_topic(rows),
        )
        for key, rows in buckets.items()
    ]
    clusters.sort(key=lambda cluster: (cluster.significance.score, len(cluster.rows)), reverse=True)
    return clusters[:limit]


def signal_text(row: dict) -> str:
    return " ".join(part for part in [row.get("title"), row.get("raw_text"), row.get("transcript")] if part)


def fallback_bucket(row: dict) -> str:
    title = row.get("title") or row.get("raw_text") or "unmatched"
    words = [word.strip(".,:;!?()[]'\"").lower() for word in title.split()]
    meaningful = [word for word in words if len(word) > 4]
    return "unmatched:" + " ".join(meaningful[:4])


def _duplicate_count_for_rows(rows: list[dict], duplicate_pairs) -> int:
    row_ids = {row.get("id") for row in rows}
    return sum(1 for candidate in duplicate_pairs if candidate.canonical_signal_id in row_ids)
