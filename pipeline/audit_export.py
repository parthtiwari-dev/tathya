"""Export Phase 3 rows for manual source/audit review."""

import argparse
import csv
import sys
from urllib.parse import urlencode

from pipeline.cli_encoding import ensure_utf8_stdout
from pipeline.storage.supabase_repository import SupabaseRepository


def main(argv: list[str] | None = None) -> int:
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="Export claims/events/facts for manual Phase 3 audit.")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--target", choices=("claims", "events", "facts"), default="claims")
    args = parser.parse_args(argv)

    repository = SupabaseRepository.from_environment()
    rows = _fetch_rows(repository, args.target, args.limit)
    writer = csv.DictWriter(sys.stdout, fieldnames=rows[0].keys() if rows else ["empty"])
    writer.writeheader()
    writer.writerows(rows)
    return 0


def _fetch_rows(repository: SupabaseRepository, target: str, limit: int) -> list[dict]:
    if target == "claims":
        query = urlencode(
            {
                "select": "id,claim_text,quoted_span,source_type,source_signal_id,signals(url,title),topics(title)",
                "limit": str(limit),
                "order": "created_at.desc",
            }
        )
        return repository.get_table_rows(f"claims?{query}")
    if target == "events":
        query = urlencode(
            {
                "select": "id,event_date,description,source_signal_ids,topics(title)",
                "limit": str(limit),
                "order": "created_at.desc",
            }
        )
        return repository.get_table_rows(f"events?{query}")
    query = urlencode(
        {
            "select": "id,fact_text,quoted_span,primary_doc_url,doc_type,topics(title)",
            "limit": str(limit),
            "order": "created_at.desc",
        }
    )
    return repository.get_table_rows(f"verifiable_facts?{query}")


if __name__ == "__main__":
    raise SystemExit(main())
