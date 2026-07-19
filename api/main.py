"""FastAPI bridge for the Tathya frontend.

This is the roadmap's lightweight API layer. It serves already-persisted,
source-bound Supabase data and accepts correction reports; it does not bypass
the Phase 3 manual audit launch gate.
"""

from pydantic import BaseModel, Field

from pipeline.processing.embedder import LocalEmbedder, vector_literal
from pipeline.storage.supabase_repository import SupabaseRepository

try:
    from fastapi import Depends, FastAPI, HTTPException
except ImportError as error:  # pragma: no cover - exercised only when api extra is missing
    raise RuntimeError('Install API dependencies with: python -m pip install -e ".[api]"') from error


class CorrectionRequest(BaseModel):
    target_table: str = Field(pattern="^(claims|events|verifiable_facts)$")
    target_row_id: str
    issue_description: str = Field(min_length=5, max_length=2000)


def get_repository() -> SupabaseRepository:
    return SupabaseRepository.from_environment()


app = FastAPI(title="Tathya API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/topics")
def topics(limit: int = 20, repository: SupabaseRepository = Depends(get_repository)) -> dict:
    safe_limit = max(1, min(limit, 100))
    return {"topics": repository.list_topics(limit=safe_limit)}


@app.get("/topics/{topic_id}")
def topic_detail(topic_id: str, repository: SupabaseRepository = Depends(get_repository)) -> dict:
    detail = repository.topic_detail(topic_id)
    if not detail["topic"]:
        raise HTTPException(status_code=404, detail="topic not found")
    return detail


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


@app.post("/corrections", status_code=201)
def report_correction(
    correction: CorrectionRequest,
    repository: SupabaseRepository = Depends(get_repository),
) -> dict:
    return repository.create_correction(
        target_table=correction.target_table,
        target_row_id=correction.target_row_id,
        issue_description=correction.issue_description,
    )
