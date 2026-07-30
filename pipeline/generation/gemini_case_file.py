"""Grounded Gemini case-file generation.

The model receives extractive evidence rows and must return JSON only. This
module is intentionally private/audit-facing; public launch still requires the
manual Phase 3 audit gate from the roadmap.
"""

import json
import os
from dataclasses import asdict

from pydantic import BaseModel, Field

from pipeline.generation.case_file_builder import CaseFileDraft


DEFAULT_GEMINI_MODEL = "gemini-3.5-flash"


class GroundedClaim(BaseModel):
    source_type: str
    claim_text: str
    claim_text_hi: str = Field(description="Accurate Hindi translation of claim_text. Never translate quoted_span itself -- it stays in its original language, since it's a direct quote, not Gemini's own text.")
    quoted_span: str
    source_url: str


class GroundedEvent(BaseModel):
    event_date: str
    description: str
    description_hi: str = Field(description="Accurate Hindi translation of description.")
    source_urls: list[str]


class GroundedFact(BaseModel):
    fact_text: str
    fact_text_hi: str = Field(description="Accurate Hindi translation of fact_text. Never translate quoted_span itself.")
    primary_doc_url: str
    quoted_span: str


class GroundedCaseFile(BaseModel):
    title: str
    title_hi: str = Field(description="Accurate Hindi translation of `title` -- a real headline, not a literal word-for-word translation, but never adding or dropping facts from the English version.")
    neutral_summary: str = Field(
        description=(
            "A genuine full-picture synthesis of everything in the evidence, not a one-line recap. "
            "Roughly 3-5 short paragraphs covering: what happened and how the story developed over time "
            "(grounded in the events supplied); what each side has actually said, in neutral third-person "
            "framing (government/opposition/media/citizen, whichever are present in the evidence -- never "
            "invent a side that isn't in the evidence); and what remains unresolved or unconfirmed as of the "
            "most recent evidence. Written so a reader who read nothing else on the page would understand "
            "the full current state of the story. Still strictly neutral -- describe positions, never rule on "
            "which one is correct, and never state anything not traceable to the supplied evidence."
        )
    )
    neutral_summary_hi: str = Field(description="Accurate Hindi translation of `neutral_summary`, same facts, same neutrality, same paragraph structure, natural Hindi phrasing.")
    events: list[GroundedEvent]
    claims: list[GroundedClaim]
    verifiable_facts: list[GroundedFact]


def generate_grounded_case_file(draft: CaseFileDraft, model_name: str | None = None) -> GroundedCaseFile:
    try:
        from google import genai
        from google.genai import types
    except ImportError as error:
        raise RuntimeError('Install generation dependencies with: python -m pip install -e ".[generation]"') from error

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY must be set for grounded generation")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name or os.getenv("GEMINI_MODEL") or DEFAULT_GEMINI_MODEL,
        contents=_prompt(draft),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=GroundedCaseFile,
            temperature=0.0,
        ),
    )
    payload = response.text or "{}"
    return GroundedCaseFile.model_validate_json(payload)


def _prompt(draft: CaseFileDraft) -> str:
    return (
        "You build non-partisan civic case files. Use only the supplied evidence. "
        "Do not add facts from memory. Do not decide truth or falsehood. "
        "Every claim, event, and fact must preserve a source URL and quoted span from the evidence. "
        "neutral_summary is the most important field on the page -- it should read as a genuine, complete "
        "account of the story so far, not a teaser. See its schema description for exactly what to cover. "
        "For every _hi field (title_hi, neutral_summary_hi, claim_text_hi, description_hi, fact_text_hi): "
        "produce an accurate, natural Hindi translation of the corresponding English field -- same facts, "
        "same neutral tone, no additions or omissions, no paraphrasing beyond what natural Hindi phrasing "
        "requires. Never translate quoted_span -- it is a direct quote from the source and must stay in "
        "whatever language the source evidence is in, exactly as supplied. "
        "Return valid JSON matching the schema.\n\n"
        f"EVIDENCE_DRAFT:\n{json.dumps(asdict(draft), ensure_ascii=False, indent=2)}"
    )
