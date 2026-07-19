"""Sentence-transformers embedding utilities for Phase 2 semantic retrieval."""

MODEL_NAME = "intfloat/multilingual-e5-base"
EMBEDDING_DIMENSION = 768


def signal_text(row: dict) -> str:
    return " ".join(part for part in [row.get("title"), row.get("raw_text"), row.get("transcript")] if part).strip()


def passage_text(row: dict) -> str:
    text = signal_text(row)
    return f"passage: {text}" if text else "passage:"


def query_text(value: str) -> str:
    return f"query: {value.strip()}"


class LocalEmbedder:
    """Lazy sentence-transformers wrapper so normal tests do not need torch installed."""

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as error:
            raise RuntimeError('Install embedding dependencies with: python -m pip install -e ".[embeddings]"') from error
        self.model = SentenceTransformer(model_name)

    def encode_passages(self, rows: list[dict]) -> list[list[float]]:
        return self._encode([passage_text(row) for row in rows])

    def encode_query(self, query: str) -> list[float]:
        return self._encode([query_text(query)])[0]

    def _encode(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return [list(map(float, vector)) for vector in embeddings]


def vector_literal(embedding: list[float]) -> str:
    if len(embedding) != EMBEDDING_DIMENSION:
        raise ValueError(f"Expected {EMBEDDING_DIMENSION} embedding values, got {len(embedding)}")
    return "[" + ",".join(f"{value:.8f}" for value in embedding) + "]"
