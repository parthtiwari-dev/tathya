"""Extractive Phase 3 case-file draft builder.

These drafts are intentionally plain and source-bound. They are audit artifacts,
not public case files and not LLM prose.
"""

from dataclasses import dataclass
import re

from pipeline.processing.clusterer import TopicCluster, signal_text
from pipeline.processing.entity_matcher import entity_type
from pipeline.processing.text_cleaner import clean_source_text
from shared.slugify import slugify


@dataclass(frozen=True)
class DraftEvent:
    event_date: str
    description: str
    source_signal_ids: tuple[str, ...]
    source_urls: tuple[str, ...]


@dataclass(frozen=True)
class DraftClaim:
    source_type: str
    claim_text: str
    quoted_span: str
    source_signal_id: str
    source_url: str


@dataclass(frozen=True)
class DraftFact:
    fact_text: str
    primary_doc_url: str
    doc_type: str
    quoted_span: str


@dataclass(frozen=True)
class DraftOpenQuestion:
    question: str
    related_claim_source_signal_id: str


@dataclass(frozen=True)
class DraftContradiction:
    entity_name: str
    statement_a_text: str
    statement_a_date: str
    statement_a_source_signal_id: str
    statement_b_text: str
    statement_b_date: str
    statement_b_source_signal_id: str


@dataclass(frozen=True)
class CaseFileDraft:
    title: str
    slug: str
    neutral_summary: str
    significance_score: float
    promotable: bool
    events: tuple[DraftEvent, ...]
    claims: tuple[DraftClaim, ...]
    verifiable_facts: tuple[DraftFact, ...]
    related_entities: tuple[str, ...]
    ministry_entity_name: str | None
    open_questions: tuple[DraftOpenQuestion, ...] = ()
    contradictions: tuple[DraftContradiction, ...] = ()


def build_case_file_draft(cluster: TopicCluster) -> CaseFileDraft:
    rows = list(cluster.rows)
    claims = tuple(_claims(rows))
    return CaseFileDraft(
        title=cluster.key,
        slug=slugify(cluster.key),
        neutral_summary=_summary(rows),
        significance_score=cluster.significance.score,
        promotable=cluster.significance.promotable,
        events=tuple(_events(rows)),
        claims=claims,
        verifiable_facts=tuple(_facts(rows)),
        related_entities=cluster.entities,
        ministry_entity_name=_ministry_entity(cluster.entities),
        open_questions=tuple(_open_questions(claims)),
        # Contradiction detection needs cross-signal semantic comparison the
        # extractive builder deliberately doesn't do (see roadmap: no
        # fabricated/inferred content). Left empty until a grounded generation
        # step (e.g. gemini_case_file.py) is wired into persistence.
        contradictions=(),
    )


def _ministry_entity(entity_names: tuple[str, ...]) -> str | None:
    return next((name for name in entity_names if entity_type(name) == "ministry"), None)


def _open_questions(claims: tuple[DraftClaim, ...]) -> list[DraftOpenQuestion]:
    """Flag the structural case of 'no official claim has been added yet'.

    This is purely a presence/absence check over what was already extracted
    -- it never invents or infers content, consistent with the rest of this
    builder.
    """
    if not claims or any(claim.source_type == "govt" for claim in claims):
        return []
    first = claims[0]
    return [
        DraftOpenQuestion(
            question=(
                "No official government statement on this has been recorded as a "
                "verifiable fact yet -- only "
                + ("citizen and " if any(c.source_type == "citizen" for c in claims) else "")
                + "media reporting exists so far."
            ),
            related_claim_source_signal_id=first.source_signal_id,
        )
    ]


def _summary(rows: list[dict]) -> str:
    source_count = len({_source_key(row) for row in rows})
    signal_count = len(rows)
    titles = [row.get("title") for row in rows if row.get("title")]
    representative = titles[0] if titles else "source material"
    return f"{signal_count} canonical signals from {source_count} source(s) currently cluster around: {representative}"


def _events(rows: list[dict]) -> list[DraftEvent]:
    events: list[DraftEvent] = []
    for row in rows[:8]:
        events.append(
            DraftEvent(
                event_date=(row.get("published_at") or "")[:10],
                description=_first_sentence(row),
                source_signal_ids=(row.get("id") or "",),
                source_urls=(row.get("url") or "",),
            )
        )
    return events


def _claims(rows: list[dict]) -> list[DraftClaim]:
    claims: list[DraftClaim] = []
    for row in rows[:12]:
        span = _first_sentence(row)
        if not span:
            continue
        claims.append(
            DraftClaim(
                source_type=_claim_source_type(row),
                claim_text=span,
                quoted_span=span,
                source_signal_id=row.get("id") or "",
                source_url=row.get("url") or "",
            )
        )
    return claims


def _facts(rows: list[dict]) -> list[DraftFact]:
    facts: list[DraftFact] = []
    for row in rows:
        if _trust_category(row) != "official":
            continue
        span = _first_sentence(row)
        if not span:
            continue
        facts.append(
            DraftFact(
                fact_text=span,
                primary_doc_url=row.get("url") or "",
                doc_type=_doc_type(row),
                quoted_span=span,
            )
        )
    return facts[:8]


def _first_sentence(row: dict) -> str:
    text = clean_source_text(signal_text(row))
    if not text:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", text)
    return parts[0][:500]


def _claim_source_type(row: dict) -> str:
    trust = _trust_category(row)
    if trust == "official":
        return "govt"
    if trust == "media":
        return "media"
    if trust == "citizen":
        return "citizen"
    return "media"


def _doc_type(row: dict) -> str:
    source_key = _source_key(row)
    if "rbi" in source_key:
        return "dataset"
    if "pib" in source_key:
        return "pib"
    if "parliament" in source_key or "sabha" in source_key:
        return "parliament_qa"
    return "dataset"


def _source_key(row: dict) -> str:
    source = row.get("sources") or {}
    return source.get("source_key") or "unknown"


def _trust_category(row: dict) -> str:
    source = row.get("sources") or {}
    return source.get("trust_category") or "unknown"
