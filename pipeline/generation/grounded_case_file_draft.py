"""Bridges Gemini-grounded generation into the same CaseFileDraft shape the
extractive builder produces, so persist_case_file_draft() and every caller
downstream of it doesn't need to know which path produced a given topic.

See docs/audit_and_next_steps.md Section 7.2 for why this module exists:
case_file_persist.py previously only ever called the deterministic extractive
builder, and gemini_case_file.py's grounded path was never wired to
persistence at all -- this closes that gap.

Reconciliation: GroundedCaseFile carries only text + source_url per
claim/event/fact (no internal signal id, no doc_type), because the Gemini
schema is evidence-grounded but doesn't know about our internal ids. This
module maps each returned source_url back to the original signal row (by
exact URL match against the cluster's rows) to recover source_signal_id and
doc_type. An item whose URL can't be matched is dropped rather than persisted
with a guessed/broken signal reference -- silently inventing a link back to
the wrong signal would violate the same "grounded only" rule the generation
step itself is supposed to follow.
"""

from pipeline.generation.case_file_builder import (
    CaseFileDraft,
    DraftClaim,
    DraftEvent,
    DraftFact,
    _doc_type,
    build_case_file_draft,
)
from pipeline.generation.gemini_case_file import generate_grounded_case_file
from pipeline.processing.clusterer import TopicCluster
from shared.slugify import slugify

# Must match the claim_source_type values append_topic_claim's SQL enum
# accepts (db/schema.sql) -- "opposition" exists in that enum too but the
# extractive builder never emits it either, so Gemini output is normalized
# down to this same three-value set for consistency between both paths.
_VALID_CLAIM_SOURCE_TYPES = {"govt", "media", "citizen"}

GenerationPath = str  # "grounded" | "extractive_fallback" -- kept as a plain
# str rather than an enum so callers can print it directly without an import.


def build_grounded_case_file_draft(cluster: TopicCluster) -> tuple[CaseFileDraft, GenerationPath]:
    """Try Gemini-grounded generation; fall back to the extractive draft on
    any failure. Callers should log the returned path, not swallow it -- see
    case_file_persist.py, which prints it per topic.
    """
    extractive = build_case_file_draft(cluster)

    try:
        grounded = generate_grounded_case_file(extractive)
    except Exception:
        # Covers: missing GEMINI_API_KEY, missing generation extra installed,
        # network/API failure, or the model returning JSON that fails
        # GroundedCaseFile validation. All of these should degrade to the
        # deterministic draft, never crash the persist run for one topic.
        return extractive, "extractive_fallback"

    url_to_row = {row.get("url"): row for row in cluster.rows if row.get("url")}

    events: list[DraftEvent] = []
    for event in grounded.events:
        matched_ids: list[str] = []
        matched_urls: list[str] = []
        for url in event.source_urls:
            row = url_to_row.get(url)
            if row and row.get("id"):
                matched_ids.append(row["id"])
                matched_urls.append(url)
        if not matched_ids:
            continue
        events.append(
            DraftEvent(
                event_date=event.event_date,
                description=event.description,
                source_signal_ids=tuple(matched_ids),
                source_urls=tuple(matched_urls),
            )
        )

    claims: list[DraftClaim] = []
    for claim in grounded.claims:
        row = url_to_row.get(claim.source_url)
        if not row or not row.get("id"):
            continue
        source_type = claim.source_type if claim.source_type in _VALID_CLAIM_SOURCE_TYPES else "media"
        claims.append(
            DraftClaim(
                source_type=source_type,
                claim_text=claim.claim_text,
                quoted_span=claim.quoted_span,
                source_signal_id=row["id"],
                source_url=claim.source_url,
            )
        )

    facts: list[DraftFact] = []
    for fact in grounded.verifiable_facts:
        row = url_to_row.get(fact.primary_doc_url)
        if not row or not row.get("id"):
            continue
        facts.append(
            DraftFact(
                fact_text=fact.fact_text,
                primary_doc_url=fact.primary_doc_url,
                doc_type=_doc_type(row),
                quoted_span=fact.quoted_span,
            )
        )

    if not events and not claims and not facts:
        # Every returned URL failed to match a real signal (e.g. Gemini
        # altered/normalized a URL). Trust the deterministic extractive draft
        # rather than persist an effectively-empty "grounded" topic.
        return extractive, "extractive_fallback"

    grounded_draft = CaseFileDraft(
        title=grounded.title,
        slug=slugify(grounded.title),
        neutral_summary=grounded.neutral_summary,
        significance_score=extractive.significance_score,
        promotable=extractive.promotable,
        events=tuple(events),
        claims=tuple(claims),
        verifiable_facts=tuple(facts),
        related_entities=extractive.related_entities,
        ministry_entity_name=extractive.ministry_entity_name,
        open_questions=extractive.open_questions,
        # Same reasoning as case_file_builder.py: contradiction detection
        # needs cross-signal semantic comparison neither path does yet.
        contradictions=(),
    )
    return grounded_draft, "grounded"
