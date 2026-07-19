"""Roadmap Phase 3 neutral summary builder.

The default summary is extractive and deterministic. Gemini generation remains
opt-in because public launch is blocked on the manual audit gate.
"""

from pipeline.generation.case_file_builder import CaseFileDraft
from pipeline.generation.gemini_case_file import generate_grounded_case_file


def build_neutral_summary(
    draft: CaseFileDraft,
    *,
    use_gemini: bool = False,
    model_name: str | None = None,
) -> str:
    """Return a neutral, source-grounded summary for a case-file draft."""
    if not use_gemini:
        return draft.neutral_summary
    return generate_grounded_case_file(draft, model_name=model_name).neutral_summary
