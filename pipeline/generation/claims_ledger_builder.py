"""Roadmap Phase 3 claims ledger builder."""

from dataclasses import dataclass

from pipeline.generation.case_file_builder import CaseFileDraft, DraftClaim


@dataclass(frozen=True)
class ClaimsLedger:
    govt: tuple[DraftClaim, ...]
    media: tuple[DraftClaim, ...]
    citizen: tuple[DraftClaim, ...]
    opposition: tuple[DraftClaim, ...]


def build_claims_ledger(draft: CaseFileDraft) -> ClaimsLedger:
    """Group source-bound claims while preserving quoted spans and source URLs."""
    return ClaimsLedger(
        govt=tuple(claim for claim in draft.claims if claim.source_type == "govt"),
        media=tuple(claim for claim in draft.claims if claim.source_type == "media"),
        citizen=tuple(claim for claim in draft.claims if claim.source_type == "citizen"),
        opposition=tuple(claim for claim in draft.claims if claim.source_type == "opposition"),
    )
