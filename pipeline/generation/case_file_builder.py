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
    # None from the extractive path: `description` here is a raw excerpt of
    # source text (see _first_sentence), not a paraphrase -- there's no
    # honest mechanical translation of arbitrary extracted text. Only the
    # grounded (Gemini) path, where description is Gemini's own composed
    # text rather than a raw excerpt, can populate this.
    description_hi: str | None = None


@dataclass(frozen=True)
class DraftClaim:
    source_type: str
    claim_text: str
    quoted_span: str
    source_signal_id: str
    source_url: str
    # None from the extractive path: claim_text IS quoted_span here (the same
    # `span` variable, see _claims below) -- translating claim_text without
    # touching quoted_span would misrepresent a direct quote as a paraphrase.
    claim_text_hi: str | None = None


@dataclass(frozen=True)
class DraftFact:
    fact_text: str
    primary_doc_url: str
    doc_type: str
    quoted_span: str
    # Same reasoning as DraftClaim.claim_text_hi -- fact_text IS quoted_span
    # on the extractive path.
    fact_text_hi: str | None = None


@dataclass(frozen=True)
class DraftOpenQuestion:
    question: str
    related_claim_source_signal_id: str
    # Unlike claims/events/facts, this is a fixed, hand-authored template
    # sentence (see _open_questions), not extracted source text -- so a
    # plain-template Hindi mirror is honest here, same reasoning as
    # _summary_hi.
    question_hi: str | None = None


@dataclass(frozen=True)
class DraftContradiction:
    entity_name: str
    statement_a_text: str
    statement_a_date: str
    statement_a_source_signal_id: str
    statement_b_text: str
    statement_b_date: str
    statement_b_source_signal_id: str
    statement_a_text_hi: str | None = None
    statement_b_text_hi: str | None = None


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
    # Hindi versions of title/neutral_summary only -- the highest-visibility
    # display text (feed cards, topic page headline). Claims/events/facts
    # deliberately stay English-only for now; see db/migrations/010 for why.
    # title_hi is None from the extractive path (a real headline can't be
    # honestly machine-translated without an LLM); summary_hi is always
    # populated here since it's built from a fixed template (_summary_hi).
    title_hi: str | None = None
    summary_hi: str | None = None


def build_case_file_draft(cluster: TopicCluster) -> CaseFileDraft:
    rows = list(cluster.rows)
    claims = tuple(_claims(rows))
    return CaseFileDraft(
        title=_representative_title(rows, fallback=cluster.key),
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
        title_hi=None,
        summary_hi=_summary_hi(rows),
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
    has_citizen = any(c.source_type == "citizen" for c in claims)
    return [
        DraftOpenQuestion(
            question=(
                "No official government statement on this has been recorded as a "
                "verifiable fact yet -- only "
                + ("citizen and " if has_citizen else "")
                + "media reporting exists so far."
            ),
            related_claim_source_signal_id=first.source_signal_id,
            question_hi=(
                "इस बारे में अभी तक कोई आधिकारिक सरकारी बयान वेरिफ़ायक तथ्य के रूप में दर्ज नहीं किया गया है — अभी तक केवल "
                + ("नागरिक और " if has_citizen else "")
                + "मीडिया रिपोर्टिंग ही मौजूद है।"
            ),
        )
    ]


def _representative_title(rows: list[dict], fallback: str) -> str:
    """Pick a real headline for display.

    `cluster.key` (the fallback) is the internal anchor -- an entity name
    like "Reserve Bank of India" -- accurate as a stable topic identity but
    not something anyone would recognize as a headline. Prefer the most
    recent signal's own title instead, since RSS/press-release titles are
    already real, human-written headlines. This is display-only: `slug`
    stays derived from `cluster.key` regardless (see build_case_file_draft),
    so this never affects topic identity/deduplication, only what's shown.
    """
    dated_titles = [(row.get("published_at") or "", row.get("title")) for row in rows if row.get("title")]
    if not dated_titles:
        return fallback
    dated_titles.sort(key=lambda pair: pair[0], reverse=True)
    return dated_titles[0][1]


def _summary(rows: list[dict]) -> str:
    source_count = len({_source_key(row) for row in rows})
    signal_count = len(rows)
    titles = [row.get("title") for row in rows if row.get("title")]
    representative = titles[0] if titles else "source material"
    return f"{signal_count} canonical signals from {source_count} source(s) currently cluster around: {representative}"


def _summary_hi(rows: list[dict]) -> str:
    """Hindi mirror of _summary(). Plain template substitution, no LLM --
    the sentence structure is fixed, only the numbers and the (English)
    representative title are inserted, so this is honest to translate
    mechanically. The representative title itself is left in its original
    language rather than mistranslated word-for-word.
    """
    source_count = len({_source_key(row) for row in rows})
    signal_count = len(rows)
    titles = [row.get("title") for row in rows if row.get("title")]
    representative = titles[0] if titles else "स्रोत सामग्री"
    return f"{signal_count} प्रामाणिक संकेत {source_count} स्रोत(स्रोतों) से इस विषय पर केंद्रित हैं: {representative}"


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
