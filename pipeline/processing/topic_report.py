"""Private Phase 2 candidate-topic report built from persisted signals."""

from collections import defaultdict
from dataclasses import dataclass

from pipeline.processing.entity_matcher import match_entities


@dataclass(frozen=True)
class CandidateTopic:
    key: str
    signal_count: int
    canonical_count: int
    source_keys: tuple[str, ...]
    top_entities: tuple[str, ...]
    representative_urls: tuple[str, ...]

    @property
    def score(self) -> int:
        return self.canonical_count * 10 + len(self.source_keys) * 5 + len(self.top_entities)


def build_candidate_topics(signal_rows: list[dict], limit: int = 10) -> list[CandidateTopic]:
    buckets: dict[str, list[dict]] = defaultdict(list)
    entity_names_by_bucket: dict[str, set[str]] = defaultdict(set)

    for row in signal_rows:
        text = " ".join(part for part in [row.get("title"), row.get("raw_text"), row.get("transcript")] if part)
        matches = match_entities(text)
        if matches:
            bucket_key = matches[0].name
            for entity in matches:
                entity_names_by_bucket[bucket_key].add(entity.name)
        else:
            bucket_key = _fallback_bucket(row)
        buckets[bucket_key].append(row)

    candidates = [_candidate_from_bucket(key, rows, entity_names_by_bucket[key]) for key, rows in buckets.items()]
    candidates.sort(key=lambda candidate: (candidate.score, candidate.signal_count), reverse=True)
    return candidates[:limit]


def _candidate_from_bucket(key: str, rows: list[dict], entity_names: set[str]) -> CandidateTopic:
    source_keys = sorted({_source_key(row) for row in rows})
    canonical_rows = [row for row in rows if not row.get("duplicate_of_signal_id")]
    urls = []
    for row in rows:
        url = row.get("url")
        if url and url not in urls:
            urls.append(url)
    return CandidateTopic(
        key=key,
        signal_count=len(rows),
        canonical_count=len(canonical_rows),
        source_keys=tuple(source_keys),
        top_entities=tuple(sorted(entity_names)),
        representative_urls=tuple(urls[:3]),
    )


def _source_key(row: dict) -> str:
    source = row.get("sources") or {}
    return source.get("source_key") or "unknown"


def _fallback_bucket(row: dict) -> str:
    title = row.get("title") or row.get("raw_text") or "unmatched"
    words = [word.strip(".,:;!?()[]'\"").lower() for word in title.split()]
    meaningful = [word for word in words if len(word) > 4]
    return "unmatched:" + " ".join(meaningful[:4])
