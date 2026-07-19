# Tathya

Tathya (तथ्य, “fact”) is an autonomous, non-partisan record of India's Union Government. It does not manually select topics or issue AI verdicts: configured public sources are watched continuously and clustered into sourced case files showing what government, media, and citizens said. You decide.

## Current foundation

This foundation now provides the project layout, typed pipeline models, an immutable snapshot builder, the Supabase/Postgres schema, a source registry, dry-run ingestion, Supabase persistence, source-health metrics, and Telegram test alerts.

## Run locally

Use Python 3.11+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
python -m pipeline.scheduler
```

## Database setup

1. Create a Supabase project.
2. In its SQL Editor, run [`db/schema.sql`](db/schema.sql), [`db/seed_sources.sql`](db/seed_sources.sql), then [`db/seed_entities_core.sql`](db/seed_entities_core.sql).
3. Copy `.env.example` to `.env` and fill in the project URL and service-role key. Keep `.env` private.

The schema makes `snapshots` append-only at the database level; source pages may change or disappear, but a captured source record cannot silently change.

After the database and source seed are in place, persist the enabled watcher output with:

```powershell
python -m pipeline.scheduler --persist
```

This calls the database's atomic `record_signal_snapshot` function. Re-running it is safe: the same source URL does not create a second signal, and exact content duplicates are linked to their first canonical signal.

Each persisted run also records its source count. After three successful historical runs, a run below 20% of its recent median is printed as an alert; Telegram delivery is the remaining deployment integration.

PIB, Lok Sabha, Rajya Sabha, and YouTube now have source-specific adapters. They remain disabled in `shared/config.py` until their live endpoints/channels are validated; enabling a configured source automatically selects its correct adapter.

## Scheduled ingestion

[`ingest.yml`](.github/workflows/ingest.yml) runs enabled sources every six hours after you add `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` as GitHub repository secrets. It can also be run manually from the Actions tab.

Optional source-failure and low-volume alerts need `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` added as GitHub repository secrets (and, for local runs, to `.env`).

Verify that Telegram independently of a source failure with:

```powershell
python -m pipeline.scheduler --test-alert
```

## Source activation

List all configured sources:

```powershell
python -m pipeline.source_audit --list
```

Inspect a disabled candidate source without writing to Supabase:

```powershell
python -m pipeline.source_audit --source hindustan-times-india --limit 10
```

Persist one disabled candidate once for manual Supabase inspection without enabling GitHub Actions polling:

```powershell
python -m pipeline.source_activation --source hindustan-times-india --limit 100
```

If your Supabase project predates the activation command, first run [`db/migrations/001_source_activation.sql`](db/migrations/001_source_activation.sql) in the SQL Editor.

If you want to test `pmindia-news-updates`, first run [`db/migrations/002_official_website_sources.sql`](db/migrations/002_official_website_sources.sql), then rerun [`db/seed_sources.sql`](db/seed_sources.sql). Existing projects need the migration because `official_website` is a new `source_type` enum value.

The scheduler currently polls only enabled sources. Keep candidates disabled until their adapter, timestamp quality, canonical URLs, raw text, snapshots, duplicate behavior, and terms posture are checked. Add sources to `shared/config.py`, never individual stories.

See [`docs/source_research.md`](docs/source_research.md) for the current multi-source activation register and the reason every non-enabled source is held back.

## Phase gates

See [`docs/mission_ethics.md`](docs/mission_ethics.md) and [`docs/phase0_phase1_checklist.md`](docs/phase0_phase1_checklist.md). Do not move to Phase 2 AI/clustering until Phase 1 has several reliable official and independent enabled sources with clean snapshots and source-run metrics.

## Private Phase 2 report

After enabled sources have been persisted, build the first private candidate-topic report:

```powershell
python -m pipeline.topic_report --signals 300 --topics 10
```

This is deterministic entity matching and grouping only. It does not call Gemini and does not publish case files.

Review likely wire-copy or near-duplicate records:

```powershell
python -m pipeline.duplicate_scan --signals 300 --threshold 0.82
```

After running [`db/migrations/003_mark_signal_duplicate.sql`](db/migrations/003_mark_signal_duplicate.sql), clearly reviewed candidates can be marked with:

```powershell
python -m pipeline.duplicate_scan --signals 300 --threshold 0.82 --apply
```

Build private Phase 3 extractive case-file drafts:

```powershell
python -m pipeline.case_file_report --signals 300 --topics 5
python -m pipeline.case_file_report --signals 300 --topics 5 --json
```

These drafts are audit material only: no Gemini, no public publishing, and every claim/event/fact is copied from a source row with a URL.

After running [`db/migrations/004_case_file_persistence.sql`](db/migrations/004_case_file_persistence.sql), persist private extractive drafts:

```powershell
python -m pipeline.case_file_persist --signals 300 --topics 5
```

Use `--promotable-only` when you only want clusters that pass the official-plus-nonofficial significance gate.

## Semantic retrieval

Tathya uses Supabase Postgres with `pgvector`; embeddings are stored in `signals.embedding`. The first model target is `intfloat/multilingual-e5-base`, a 768-dimensional multilingual sentence-transformers model.

Install the optional local embedding dependencies:

```powershell
python -m pip install -e ".[embeddings]"
```

After running [`db/migrations/005_signal_embeddings.sql`](db/migrations/005_signal_embeddings.sql), embed recent signals:

```powershell
python -m pipeline.embed_signals --limit 300 --batch-size 16
```

Search embedded signals:

```powershell
python -m pipeline.semantic_search "Sonam Wangchuk Parliament march" --limit 10
```

## Grounded generation and audit

Install optional Gemini generation dependencies:

```powershell
python -m pip install -e ".[generation]"
```

Generate private grounded JSON drafts:

```powershell
python -m pipeline.gemini_case_file_report --signals 300 --topics 3
```

Export rows for the mandatory Phase 3 manual audit:

```powershell
python -m pipeline.audit_export --target claims --limit 50 > audit_claims.csv
python -m pipeline.audit_export --target events --limit 50 > audit_events.csv
python -m pipeline.audit_export --target facts --limit 50 > audit_facts.csv
```
