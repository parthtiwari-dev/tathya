"""Roadmap Phase 3 structured timeline builder."""

from pipeline.generation.case_file_builder import CaseFileDraft, DraftEvent


def build_timeline(draft: CaseFileDraft) -> tuple[DraftEvent, ...]:
    """Return dated, structured events auditable to source signal ids."""
    return tuple(sorted(draft.events, key=lambda event: (event.event_date, event.description)))
