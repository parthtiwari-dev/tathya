import os
import sys
import types

from pipeline.generation.case_file_builder import CaseFileDraft
from pipeline.generation.gemini_case_file import GroundedCaseFile, generate_grounded_case_file


def test_generate_grounded_case_file_uses_json_schema(monkeypatch) -> None:
    captured = {}

    class Response:
        text = GroundedCaseFile(
            title="RBI",
            neutral_summary="Neutral summary.",
            events=[],
            claims=[],
            verifiable_facts=[],
        ).model_dump_json()

    class Models:
        def generate_content(self, **kwargs):
            captured.update(kwargs)
            return Response()

    class Client:
        def __init__(self, api_key):
            captured["api_key"] = api_key
            self.models = Models()

    class Config:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    fake_google = types.ModuleType("google")
    fake_genai = types.ModuleType("google.genai")
    fake_types = types.ModuleType("google.genai.types")
    fake_genai.Client = Client
    fake_types.GenerateContentConfig = Config
    fake_genai.types = fake_types
    fake_google.genai = fake_genai
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.genai", fake_genai)
    monkeypatch.setitem(sys.modules, "google.genai.types", fake_types)
    monkeypatch.setenv("GEMINI_API_KEY", "key")

    draft = CaseFileDraft(
        title="RBI",
        slug="rbi",
        neutral_summary="summary",
        significance_score=1,
        promotable=False,
        events=(),
        claims=(),
        verifiable_facts=(),
        related_entities=("RBI",),
        ministry_entity_name="RBI",
    )

    result = generate_grounded_case_file(draft, model_name="model")

    assert result.title == "RBI"
    assert captured["model"] == "model"
    assert captured["api_key"] == "key"
    assert captured["config"].kwargs["response_mime_type"] == "application/json"
