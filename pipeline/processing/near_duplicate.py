"""Near-duplicate detection for Phase 2 wire-copy review."""

from dataclasses import dataclass
import re


STOPWORDS = {
    "about",
    "after",
    "again",
    "against",
    "also",
    "amid",
    "being",
    "from",
    "have",
    "into",
    "over",
    "said",
    "says",
    "that",
    "their",
    "there",
    "this",
    "under",
    "with",
    "will",
}


@dataclass(frozen=True)
class DuplicateCandidate:
    duplicate_signal_id: str
    canonical_signal_id: str
    similarity: float
    duplicate_url: str
    canonical_url: str
    duplicate_title: str
    canonical_title: str


def find_near_duplicates(signal_rows: list[dict], threshold: float = 0.82) -> list[DuplicateCandidate]:
    """Find likely near-duplicate rows using conservative token overlap.

    This is not a replacement for embeddings. It is the first safe review layer:
    high threshold, canonical row chosen by earliest published timestamp when
    available, and no automatic mutation unless the caller explicitly applies it.
    """
    rows = [row for row in signal_rows if row.get("id") and not row.get("duplicate_of_signal_id")]
    fingerprints = {row["id"]: _fingerprint(_signal_text(row)) for row in rows}
    candidates: list[DuplicateCandidate] = []

    for index, left in enumerate(rows):
        for right in rows[index + 1 :]:
            if _source_key(left) == _source_key(right):
                continue
            similarity = _jaccard(fingerprints[left["id"]], fingerprints[right["id"]])
            if similarity < threshold:
                continue
            canonical, duplicate = _canonical_pair(left, right)
            candidates.append(
                DuplicateCandidate(
                    duplicate_signal_id=duplicate["id"],
                    canonical_signal_id=canonical["id"],
                    similarity=similarity,
                    duplicate_url=duplicate.get("url") or "",
                    canonical_url=canonical.get("url") or "",
                    duplicate_title=duplicate.get("title") or "",
                    canonical_title=canonical.get("title") or "",
                )
            )

    candidates.sort(key=lambda candidate: candidate.similarity, reverse=True)
    return candidates


def _signal_text(row: dict) -> str:
    return " ".join(part for part in [row.get("title"), row.get("raw_text"), row.get("transcript")] if part)


def _fingerprint(text: str) -> frozenset[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return frozenset(token for token in tokens if len(token) > 3 and token not in STOPWORDS)


def _jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _source_key(row: dict) -> str:
    source = row.get("sources") or {}
    return source.get("source_key") or ""


def _canonical_pair(left: dict, right: dict) -> tuple[dict, dict]:
    left_time = left.get("published_at") or ""
    right_time = right.get("published_at") or ""
    if left_time <= right_time:
        return left, right
    return right, left
