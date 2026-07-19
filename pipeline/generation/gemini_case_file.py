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


DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


class GroundedClaim(BaseModel):
    source_type: str
    claim_text: str
    quoted_span: str
    source_url: str


class GroundedEvent(BaseModel):
    event_date: str
    description: str
    source_urls: list[str]


class GroundedFact(BaseModel):
    fact_text: str
    primary_doc_url: str
    quoted_span: str


class GroundedCaseFile(BaseModel):
    title: str
    neutral_summary: str = Field(description="One neutral paragraph grounded only in supplied evidence.")
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
        "Return valid JSON matching the schema.\n\n"
        f"EVIDENCE_DRAFT:\n{json.dumps(asdict(draft), ensure_ascii=False, indent=2)}"
    )
