"""Row (snake_case, from PostgREST) -> API model (camelCase) mappers.

Kept separate from main.py so the endpoint functions stay readable and the
mapping logic is unit-testable on its own.
"""

from __future__ import annotations

from api.schemas import (
    Claim,
    Contradiction,
    ContradictionStatement,
    Correction,
    HistoryEntry,
    OpenQuestion,
    SignalSummary,
    Source,
    SourceCount,
    SourceRun,
    TimelineEvent,
    TopicDetail,
    TopicRelation,
    TopicSummary,
    VerifiableFact,
)

_MINISTRY_PREFIX = "Ministry of "


def ministry_label(name: str) -> str:
    """Short display label for a ministry entity name ('Ministry of Railways' -> 'Railways')."""
    return name[len(_MINISTRY_PREFIX):] if name.startswith(_MINISTRY_PREFIX) else name


def _taxonomy(row: dict) -> tuple[str, str, list[str]]:
    """Derive (ministry label, ministry slug, entityTags) from an embedded topic_entities list.

    A topic with no linked ministry entity falls back to "Unclassified" rather
    than a null/empty value, since Topic.ministry is a required field on the
    frontend contract.
    """
    links = row.get("topic_entities") or []
    entity_tags: list[str] = []
    ministry_name: str | None = None
    ministry_slug: str | None = None
    for link in links:
        entity = link.get("entities") or {}
        name = entity.get("name")
        if not name:
            continue
        entity_tags.append(name)
        if link.get("is_ministry") and ministry_name is None:
            ministry_name = name
            ministry_slug = entity.get("slug")
    if ministry_name is None:
        return "Unclassified", "unclassified", entity_tags
    return ministry_label(ministry_name), ministry_slug or "unclassified", entity_tags


def _source_count(row: dict) -> SourceCount:
    """Count distinct sources per trust_category from an embedded topic_signals list."""
    buckets: dict[str, set[str]] = {"official": set(), "media": set(), "citizen": set()}
    for link in row.get("topic_signals") or []:
        signal = link.get("signal") or {}
        source = signal.get("source") or {}
        trust = source.get("trust_category")
        key = source.get("source_key")
        if trust in buckets and key:
            buckets[trust].add(key)
    return SourceCount(official=len(buckets["official"]), media=len(buckets["media"]), citizen=len(buckets["citizen"]))


def to_topic_summary(row: dict) -> TopicSummary:
    ministry, ministry_slug, entity_tags = _taxonomy(row)
    return TopicSummary(
        id=row["id"],
        slug=row.get("slug") or row["id"],
        title=row["title"],
        summary=row.get("summary"),
        status=row["status"],
        ministry=ministry,
        ministrySlug=ministry_slug,
        entityTags=entity_tags,
        firstSeen=row.get("first_seen"),
        lastSignalAt=row.get("last_signal_at"),
        significanceScore=row.get("significance_score", 0),
        sourceCount=_source_count(row),
    )


# The DB enum claim_source_type stores 'govt', but the frontend's
# ClaimSourceType (and ClaimsLedger's column-grouping logic) expects
# 'government'. Translate here at the API boundary rather than touching the
# DB enum/RPC functions, which would be a riskier migration for no gain.
_CLAIM_SOURCE_TYPE_DB_TO_API = {"govt": "government"}


def to_claim(row: dict) -> Claim:
    db_source_type = row["source_type"]
    signal = row.get("signal") or {}
    source = signal.get("source") or {}
    topic = row.get("topic") or {}
    return Claim(
        id=row["id"],
        claimText=row["claim_text"],
        sourceType=_CLAIM_SOURCE_TYPE_DB_TO_API.get(db_source_type, db_source_type),
        sourceSignalId=row["source_signal_id"],
        quotedSpan=row["quoted_span"],
        createdAt=row.get("created_at"),
        sourceName=source.get("name"),
        sourceUrl=signal.get("url"),
        sourceKey=source.get("source_key"),
        publishedAt=signal.get("published_at"),
        topicSlug=topic.get("slug"),
        topicTitle=topic.get("title"),
    )


def to_event(row: dict) -> TimelineEvent:
    return TimelineEvent(
        id=row["id"],
        eventDate=row["event_date"],
        description=row["description"],
        sourceSignalIds=row.get("source_signal_ids") or [],
    )


def to_fact(row: dict) -> VerifiableFact:
    return VerifiableFact(
        id=row["id"],
        factText=row["fact_text"],
        primaryDocUrl=row["primary_doc_url"],
        docType=row["doc_type"],
        quotedSpan=row["quoted_span"],
        createdAt=row.get("created_at"),
    )


def to_relation(row: dict) -> TopicRelation:
    """Map one topic_relations row.

    The repository already resolves "the other topic" per-row via an aliased
    `related:topics(...)` embed (topic_id_b for the topic_id_a query and vice
    versa), so this doesn't need to know which topic_id we queried from.
    """
    related = row.get("related") or {}
    return TopicRelation(
        id=row["id"],
        relatedTopicId=related.get("id", ""),
        relatedTopicSlug=related.get("slug"),
        relatedTopicTitle=related.get("title"),
        relationType=row["relation_type"],
    )


def to_open_question(row: dict) -> OpenQuestion:
    return OpenQuestion(id=row["id"], question=row["question"], relatedClaimId=row.get("related_claim_id"))


def to_contradiction(row: dict) -> Contradiction:
    signal_a = row.get("signal_a") or {}
    signal_b = row.get("signal_b") or {}
    source_a = signal_a.get("source") or {}
    source_b = signal_b.get("source") or {}
    return Contradiction(
        id=row["id"],
        entity=row["entity_name"],
        statementA=ContradictionStatement(
            text=row["statement_a_text"],
            date=row["statement_a_date"],
            sourceName=source_a.get("name", ""),
            sourceUrl=signal_a.get("url", ""),
        ),
        statementB=ContradictionStatement(
            text=row["statement_b_text"],
            date=row["statement_b_date"],
            sourceName=source_b.get("name", ""),
            sourceUrl=signal_b.get("url", ""),
        ),
    )


def to_topic_detail(payload: dict) -> TopicDetail | None:
    """Assemble the full nested Topic (matching lib/types.ts) from repository.topic_detail()'s payload."""
    topic_row = payload.get("topic")
    if not topic_row:
        return None
    ministry, ministry_slug, entity_tags = _taxonomy(topic_row)
    return TopicDetail(
        id=topic_row["id"],
        slug=topic_row.get("slug") or topic_row["id"],
        title=topic_row["title"],
        summary=topic_row.get("summary"),
        status=topic_row["status"],
        ministry=ministry,
        ministrySlug=ministry_slug,
        entityTags=entity_tags,
        firstSeen=topic_row.get("first_seen"),
        lastSignalAt=topic_row.get("last_signal_at"),
        sourceCount=_source_count(topic_row),
        claims=[to_claim(row) for row in payload.get("claims", [])],
        events=[to_event(row) for row in payload.get("events", [])],
        facts=[to_fact(row) for row in payload.get("verifiable_facts", [])],
        relations=[to_relation(row) for row in payload.get("relations", [])],
        history=[to_history_entry(row, index) for index, row in enumerate(payload.get("history", []))],
        openQuestions=[to_open_question(row) for row in payload.get("open_questions", [])],
        contradictions=[to_contradiction(row) for row in payload.get("contradictions", [])],
    )


def to_source(row: dict) -> Source:
    return Source(
        sourceKey=row["source_key"],
        name=row["name"],
        type=row["type"],
        trustCategory=row["trust_category"],
        url=row["url"],
        enabled=row["enabled"],
    )


def to_signal_summary(row: dict) -> SignalSummary:
    return SignalSummary(
        id=row["id"],
        publishedAt=row["published_at"],
        title=row.get("title"),
        url=row["url"],
        isDuplicate=row.get("duplicate_of_signal_id") is not None,
    )


def to_source_run(row: dict) -> SourceRun:
    source = row.get("sources") or {}
    return SourceRun(
        id=row["id"],
        sourceKey=source.get("source_key"),
        sourceName=source.get("name"),
        collectedAt=row["collected_at"],
        signalCount=row["signal_count"],
        status=row["status"],
        detail=row.get("detail"),
    )


def to_history_entry(row: dict, index: int) -> HistoryEntry:
    return HistoryEntry(
        id=f"{row['type']}-{index}",
        type=row["type"],
        description=row["description"],
        timestamp=row["timestamp"],
    )


def to_correction(row: dict) -> Correction:
    return Correction(
        id=row["id"],
        targetTable=row["target_table"],
        targetRowId=row["target_row_id"],
        issueDescription=row["issue_description"],
        status=row["status"],
        createdAt=row["created_at"],
        resolvedAt=row.get("resolved_at"),
    )
