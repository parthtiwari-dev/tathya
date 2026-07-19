"""Generate and store embeddings for persisted signals."""

import argparse

from pipeline.processing.embedder import LocalEmbedder, vector_literal
from pipeline.storage.supabase_repository import SupabaseRepository


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Embed recent signals without embeddings.")
    parser.add_argument("--limit", type=int, default=100, help="Maximum unembedded recent signals to process.")
    parser.add_argument("--batch-size", type=int, default=16, help="Embedding batch size.")
    args = parser.parse_args(argv)

    repository = SupabaseRepository.from_environment()
    rows = repository.recent_signals_without_embeddings(limit=args.limit)
    if not rows:
        print("No unembedded signals found")
        return 0

    embedder = LocalEmbedder()
    embedded = 0
    for start in range(0, len(rows), args.batch_size):
        batch = rows[start : start + args.batch_size]
        vectors = embedder.encode_passages(batch)
        for row, vector in zip(batch, vectors, strict=True):
            repository.store_signal_embedding(row["id"], vector_literal(vector))
            embedded += 1
        print(f"Embedded {embedded}/{len(rows)} signals")
    print(f"Total embeddings stored: {embedded}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
