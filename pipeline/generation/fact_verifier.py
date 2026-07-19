"""Roadmap Phase 3 verifiable-fact extraction and critique helpers.

This module keeps the high-stakes verification lane separate from ordinary
case-file generation. It does not declare facts true/false; it checks whether a
fact row is actually anchored to a primary/official source and has a quote.
"""

from dataclasses import dataclass

from pipeline.generation.case_file_builder import CaseFileDraft, DraftFact


PRIMARY_DOC_TYPES = {"pib", "parliament_qa", "gazette", "dataset"}


@dataclass(frozen=True)
class FactCritique:
    fact_text: str
    primary_doc_url: str
    status: str
    reason: str


def build_verifiable_facts(draft: CaseFileDraft) -> tuple[DraftFact, ...]:
    """Return facts already extracted from official/primary-source rows."""
    return draft.verifiable_facts


def critique_verifiable_facts(draft: CaseFileDraft) -> tuple[FactCritique, ...]:
    """Second-pass deterministic critique before any fact is trusted publicly."""
    critiques: list[FactCritique] = []
    for fact in draft.verifiable_facts:
        if not fact.primary_doc_url:
            critiques.append(FactCritique(fact.fact_text, fact.primary_doc_url, "fail", "missing primary_doc_url"))
        elif not fact.quoted_span:
            critiques.append(FactCritique(fact.fact_text, fact.primary_doc_url, "fail", "missing quoted_span"))
        elif fact.doc_type not in PRIMARY_DOC_TYPES:
            critiques.append(FactCritique(fact.fact_text, fact.primary_doc_url, "review", f"unexpected doc_type {fact.doc_type}"))
        else:
            critiques.append(FactCritique(fact.fact_text, fact.primary_doc_url, "pass", "primary source and quoted span present"))
    return tuple(critiques)
