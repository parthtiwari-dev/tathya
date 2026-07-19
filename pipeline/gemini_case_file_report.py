"""CLI for private Gemini-grounded case-file JSON drafts."""

import argparse
import json

from pipeline.cli_encoding import ensure_utf8_stdout
from pipeline.generation.case_file_builder import build_case_file_draft
from pipeline.generation.gemini_case_file import generate_grounded_case_file
from pipeline.processing.clusterer import cluster_signals
from pipeline.storage.supabase_repository import SupabaseRepository


def main(argv: list[str] | None = None) -> int:
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="Generate private Gemini-grounded case-file JSON.")
    parser.add_argument("--signals", type=int, default=300)
    parser.add_argument("--topics", type=int, default=3)
    parser.add_argument("--model", help="Override GEMINI_MODEL for this run.")
    args = parser.parse_args(argv)

    rows = SupabaseRepository.from_environment().recent_signals(limit=args.signals)
    clusters = cluster_signals(rows, limit=args.topics)
    outputs = []
    for cluster in clusters:
        draft = build_case_file_draft(cluster)
        outputs.append(generate_grounded_case_file(draft, model_name=args.model).model_dump())
        print(f"{draft.title}: generated grounded JSON")
    print(json.dumps(outputs, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
