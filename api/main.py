"""FastAPI bridge for the Tathya frontend.

This is API v1: typed Pydantic responses (api/schemas.py), row->model mapping
(api/mappers.py), real limit/offset/total pagination, and sub-resource routes
under /topics/{id}/... and /sources/... It serves already-persisted,
source-bound Supabase data and accepts correction reports; it does not bypass
the Phase 3 manual audit launch gate.
"""

import os

from pydantic import BaseModel, Field

from api import mappers
from api.schemas import (
    Claim,
    Correction,
    HistoryEntry,
    Ministry,
    Page,
    Source,
    SourceRun,
    TimelineEvent,
    TopicDetail,
    TopicRelation,
    TopicSummary,
    VerifiableFact,
)
from pipeline.processing.embedder import LocalEmbedder, vector_literal
from pipeline.storage.supabase_repository import SupabaseRepository

try:
    from fastapi import Depends, FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
except ImportError as error:  # pragma: no cover - exercised only when api extra is missing
    raise RuntimeError('Install API dependencies with: python -m pip install -e ".[api]"') from error


class CorrectionRequest(BaseModel):
    target_table: str = Field(pattern="^(claims|events|verifiable_facts)$")
    target_row_id: str
    issue_description: str = Field(min_length=5, max_length=2000)


def get_repository() -> SupabaseRepository:
    return SupabaseRepository.from_environment()


def _paginate(limit: int, offset: int, max_limit: int = 100) -> tuple[int, int]:
    safe_limit = max(1, min(limit, max_limit))
    safe_offset = max(0, offset)
    return safe_limit, safe_offset


app = FastAPI(title="Tathya API", version="1.0.0")

# Permissive for now while the frontend is being connected -- tighten to the
# deployed frontend origin(s) before public launch (see roadmap: corrections
# rate-limiting and this are the two items deliberately left for last).
_cors_origins = os.getenv("TATHYA_CORS_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if _cors_origins == "*" else [origin.strip() for origin in _cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Topics
# ---------------------------------------------------------------------------


@app.get("/topics", response_model=Page[TopicSummary])
def topics(
    limit: int = 20,
    offset: int = 0,
    repository: SupabaseRepository = Depends(get_repository),
) -> Page[TopicSummary]:
    safe_limit, safe_offset = _paginate(limit, offset)
    rows, total = repository.list_topics(limit=safe_limit, offset=safe_offset)
    return Page(items=[mappers.to_topic_summary(row) for row in rows], limit=safe_limit, offset=safe_offset, total=total)


@app.get("/topics/{topic_id}", response_model=TopicDetail)
def topic_detail(topic_id: str, repository: SupabaseRepository = Depends(get_repository)) -> TopicDetail:
    detail = mappers.to_topic_detail(repository.topic_detail(topic_id))
    if not detail:
        raise HTTPException(status_code=404, detail="topic not found")
    return detail


@app.get("/topics/slug/{slug}", response_model=TopicDetail)
def topic_detail_by_slug(slug: str, repository: SupabaseRepository = Depends(get_repository)) -> TopicDetail:
    detail = mappers.to_topic_detail(repository.topic_detail_by_slug(slug))
    if not detail:
        raise HTTPException(status_code=404, detail="topic not found")
    return detail


@app.get("/topics/{topic_id}/claims", response_model=list[Claim])
def topic_claims(topic_id: str, repository: SupabaseRepository = Depends(get_repository)) -> list[Claim]:
    return [mappers.to_claim(row) for row in repository.topic_claims(topic_id)]


@app.get("/topics/{topic_id}/events", response_model=list[TimelineEvent])
def topic_events(topic_id: str, repository: SupabaseRepository = Depends(get_repository)) -> list[TimelineEvent]:
    return [mappers.to_event(row) for row in repository.topic_events(topic_id)]


@app.get("/topics/{topic_id}/facts", response_model=list[VerifiableFact])
def topic_facts(topic_id: str, repository: SupabaseRepository = Depends(get_repository)) -> list[VerifiableFact]:
    return [mappers.to_fact(row) for row in repository.topic_facts(topic_id)]


@app.get("/topics/{topic_id}/relations", response_model=list[TopicRelation])
def topic_relations(topic_id: str, repository: SupabaseRepository = Depends(get_repository)) -> list[TopicRelation]:
    return [mappers.to_relation(row) for row in repository.topic_relations_list(topic_id)]


@app.get("/topics/{topic_id}/history", response_model=list[HistoryEntry])
def topic_history(topic_id: str, repository: SupabaseRepository = Depends(get_repository)) -> list[HistoryEntry]:
    return [mappers.to_history_entry(row, index) for index, row in enumerate(repository.topic_history(topic_id))]


@app.get("/ministries", response_model=list[Ministry])
def ministries(repository: SupabaseRepository = Depends(get_repository)) -> list[Ministry]:
    rows = repository.list_ministries()
    return [Ministry(slug=row.get("slug") or "unclassified", name=mappers._ministry_label(row["name"])) for row in rows]


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------


@app.get("/sources", response_model=list[Source])
def sources(repository: SupabaseRepository = Depends(get_repository)) -> list[Source]:
    return [mappers.to_source(row) for row in repository.list_sources()]


@app.get("/sources/{source_key}", response_model=Source)
def source_detail(source_key: str, repository: SupabaseRepository = Depends(get_repository)) -> Source:
    row = repository.get_source(source_key)
    if not row:
        raise HTTPException(status_code=404, detail="source not found")
    return mappers.to_source(row)


@app.get("/sources/{source_key}/signals")
def source_signals(
    source_key: str,
    limit: int = 50,
    offset: int = 0,
    repository: SupabaseRepository = Depends(get_repository),
) -> Page:
    safe_limit, safe_offset = _paginate(limit, offset)
    rows, total = repository.signals_for_source(source_key, limit=safe_limit, offset=safe_offset)
    return Page(items=[mappers.to_signal_summary(row) for row in rows], limit=safe_limit, offset=safe_offset, total=total)


@app.get("/sources/{source_key}/claims", response_model=Page[Claim])
def source_claims(
    source_key: str,
    limit: int = 50,
    offset: int = 0,
    repository: SupabaseRepository = Depends(get_repository),
) -> Page[Claim]:
    safe_limit, safe_offset = _paginate(limit, offset)
    rows, total = repository.claims_for_source(source_key, limit=safe_limit, offset=safe_offset)
    return Page(items=[mappers.to_claim(row) for row in rows], limit=safe_limit, offset=safe_offset, total=total)


@app.get("/source-runs", response_model=Page[SourceRun])
def source_runs(
    source_key: str | None = None,
    limit: int = 50,
    offset: int = 0,
    repository: SupabaseRepository = Depends(get_repository),
) -> Page[SourceRun]:
    safe_limit, safe_offset = _paginate(limit, offset)
    rows, total = repository.source_runs(source_key=source_key, limit=safe_limit, offset=safe_offset)
    return Page(items=[mappers.to_source_run(row) for row in rows], limit=safe_limit, offset=safe_offset, total=total)


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


@app.get("/signals/search")
def search_signals(
    q: str,
    limit: int = 10,
    threshold: float = 0.0,
    repository: SupabaseRepository = Depends(get_repository),
) -> dict:
    if not q.strip():
        raise HTTPException(status_code=400, detail="q is required")
    safe_limit = max(1, min(limit, 50))
    embedder = LocalEmbedder()
    embedding = vector_literal(embedder.encode_queries([q])[0])
    return {
        "query": q,
        "results": repository.match_similar_signals(
            embedding,
            match_count=safe_limit,
            match_threshold=threshold,
        ),
    }


# ---------------------------------------------------------------------------
# Corrections
# ---------------------------------------------------------------------------
# /corrections/public and rate-limiting on POST are deliberately left for
# right before launch -- see docs/roadmap_execution_plan.md.


@app.post("/corrections", status_code=201, response_model=Correction)
def report_correction(
    correction: CorrectionRequest,
    repository: SupabaseRepository = Depends(get_repository),
) -> Correction:
    return mappers.to_correction(
        repository.create_correction(
            target_table=correction.target_table,
            target_row_id=correction.target_row_id,
            issue_description=correction.issue_description,
        )
    )
