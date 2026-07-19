"""Roadmap Phase 3 topic-relation builder."""

from dataclasses import dataclass
import re

from pipeline.generation.case_file_builder import CaseFileDraft


@dataclass(frozen=True)
class TopicRelationCandidate:
    topic_id_a: str
    topic_id_b: str
    relation_type: str
    reason: str


def build_topic_relations(topic_drafts: list[tuple[str, CaseFileDraft]]) -> tuple[TopicRelationCandidate, ...]:
    """Detect topic links from shared entities or explicit title/text references."""
    candidates: list[TopicRelationCandidate] = []
    for index, (topic_id_a, draft_a) in enumerate(topic_drafts):
        for topic_id_b, draft_b in topic_drafts[index + 1 :]:
            shared_entities = sorted(set(draft_a.related_entities) & set(draft_b.related_entities))
            if shared_entities:
                candidates.append(
                    TopicRelationCandidate(
                        topic_id_a=topic_id_a,
                        topic_id_b=topic_id_b,
                        relation_type="same_policy_area",
                        reason="shared entities: " + ", ".join(shared_entities[:5]),
                    )
                )
                continue

            shared_terms = _shared_title_terms(draft_a.title, draft_b.title)
            if shared_terms:
                candidates.append(
                    TopicRelationCandidate(
                        topic_id_a=topic_id_a,
                        topic_id_b=topic_id_b,
                        relation_type="related",
                        reason="shared title terms: " + ", ".join(shared_terms[:5]),
                    )
                )
    return tuple(candidates)


def _shared_title_terms(title_a: str, title_b: str) -> list[str]:
    terms_a = set(_meaningful_terms(title_a))
    terms_b = set(_meaningful_terms(title_b))
    return sorted(terms_a & terms_b)


def _meaningful_terms(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 4 and token not in {"government", "india", "unmatched"}
    ]
