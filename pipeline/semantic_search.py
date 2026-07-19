"""Semantic search over embedded signals."""

import argparse

from pipeline.cli_encoding import ensure_utf8_stdout
from pipeline.processing.embedder import LocalEmbedder, vector_literal
from pipeline.storage.supabase_repository import SupabaseRepository


def main(argv: list[str] | None = None) -> int:
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="Search embedded signals semantically.")
    parser.add_argument("query", help="Search query text.")
    parser.add_argument("--limit", type=int, default=10, help="Results to show.")
    parser.add_argument("--threshold", type=float, default=0.0, help="Minimum cosine similarity.")
    args = parser.parse_args(argv)

    embedding = LocalEmbedder().encode_query(args.query)
    rows = SupabaseRepository.from_environment().match_similar_signals(
        vector_literal(embedding),
        match_count=args.limit,
        match_threshold=args.threshold,
    )
    print(f"Semantic results: {len(rows)}")
    for index, row in enumerate(rows, start=1):
        print(f"\n{index}. {row.get('title') or row.get('raw_text', '')[:80]}")
        print(f"   similarity: {row.get('similarity'):.3f}")
        print(f"   source: {row.get('source_key')} ({row.get('trust_category')})")
        print(f"   url: {row.get('url')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
