# Phase 2 Entry Gate

Do not start AI clustering just because ingestion code runs. Start Phase 2 only after this gate is true.

- At least two independent media sources are enabled and stable across scheduled runs.
- At least one official source produces meaningful body text, not only titles.
- Every enabled source has one snapshot per signal.
- Repeated `--persist` runs do not create duplicate signals for already-seen URLs.
- `source_run_metrics` has multiple successful runs per enabled source.
- Telegram test alerts work.
- A manual Supabase sample of 10-20 rows per enabled source has clean timestamps, canonical URLs, raw text, and source attribution.
- Disabled sources remain disabled in `shared/config.py` and Supabase unless they passed the one-shot activation workflow.

Once this gate passes, Phase 2 should start with local deterministic processing first:

1. Entity matching against the seeded `entities` table.
2. Exact and near-duplicate grouping.
3. Embedding generation.
4. Topic clustering.
5. Significance scoring that counts only canonical signals.

The first Phase 2 deliverable is not a public case file. It is a private report showing 5-10 automatically discovered candidate topics with source counts, top entities, and representative signal URLs.
