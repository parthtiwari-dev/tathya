"""Extractive Phase 3 case-file draft builder.

These drafts are intentionally plain and source-bound. They are audit artifacts,
not public case files and not LLM prose.
"""

from dataclasses import dataclass
import re

from pipeline.processing.clusterer import TopicCluster, signal_text
from pipeline.processing.text_cleaner import clean_source_text


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
class CaseFileDraft:
    title: str
    neutral_summary: str
    significance_score: float
    promotable: bool
    events: tuple[DraftEvent, ...]
    claims: tuple[DraftClaim, ...]
    verifiable_facts: tuple[DraftFact, ...]
    related_entities: tuple[str, ...]


def build_case_file_draft(cluster: TopicCluster) -> CaseFileDraft:
    rows = list(cluster.rows)
    return CaseFileDraft(
        title=cluster.key,
        neutral_summary=_summary(rows),
        significance_score=cluster.significance.score,
        promotable=cluster.significance.promotable,
        events=tuple(_events(rows)),
        claims=tuple(_claims(rows)),
        verifiable_facts=tuple(_facts(rows)),
        related_entities=cluster.entities,
    )


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
