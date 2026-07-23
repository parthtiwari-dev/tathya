# Tathya

Tathya (तथ्य, “fact”) is an autonomous, non-partisan record of India's Union Government. It does not manually select topics or issue AI verdicts: configured public sources are watched continuously and clustered into sourced case files showing what government, media, and citizens said. You decide.

## Live

- **Site:** [tathya-1.vercel.app](https://tathya-1.vercel.app/)
- **API docs (Swagger UI):** [tathya-zi9p.onrender.com/docs](https://tathya-zi9p.onrender.com/docs)

The API runs on Render's free tier and sleeps after 15 minutes of inactivity (cold start ~30–60s on the next request); an external uptime pinger keeps it warm during normal use. Frontend topics currently reflect Phase 2 clustering output, not final Phase 3 generation — see `docs/audit_and_next_steps.md` Section 7.2 for why titles/summaries look raw right now.

## Current foundation

The pipeline (ingestion → snapshotting → clustering → extractive/Gemini-grounded generation → persistence) and API v1 (`api/main.py`, typed against `apps/web/lib/types.ts`) are both built and deployed. The Next.js frontend (`apps/web/`) is fully wired to the real API — no mock data. What's still incomplete: `pipeline/case_file_persist.py` only calls the deterministic extractive builder, not the Gemini-grounded path, so live topics currently show raw cluster titles/templated summaries rather than final generated case files; the manual Phase 3 audit gate hasn't run yet either. See `docs/audit_and_next_steps.md` for the up-to-date gap list — it is more current than this file for "what's actually left."

## Frontend (apps/web)

```powershell
cd apps/web
npm install
npm run dev
```

Runs at `http://localhost:3000`. Set `NEXT_PUBLIC_TATHYA_API_URL` in `apps/web/.env.local` to point at a running API (defaults to `http://localhost:8000` if unset — see `apps/web/lib/api.ts`). In production this points at the deployed Render API instead.

## Deployment

- **Frontend → Vercel:** connect the repo, set Root Directory to `apps/web`, set `NEXT_PUBLIC_TATHYA_API_URL` to the deployed API URL. Currently live at [tathya-1.vercel.app](https://tathya-1.vercel.app/).
- **API → Render (free tier):** Root Directory blank (repo root), Build Command `pip install ".[api]"`, Start Command `uvicorn api.main:app --host 0.0.0.0 --port $PORT`, Health Check Path `/health`, env vars `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` / `TATHYA_CORS_ORIGINS`. Currently live at [tathya-zi9p.onrender.com/docs](https://tathya-zi9p.onrender.com/docs) — sleeps after 15 minutes of inactivity on the free tier, kept warm with an external ping (e.g. cron-job.org) hitting `/health` every ~10 minutes rather than Render's own (paid) Cron Jobs product.
- Full reasoning, RAM caveats for `/signals/search` on the free tier, and the Oracle Cloud always-on alternative are documented in `docs/audit_and_next_steps.md` Section 8.

## Run locally (pipeline/API)

Use Python 3.11+ (repo pins `3.12.7` via `runtime.txt` for hosted deploys).

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

Three GitHub Actions workflows run on a schedule once `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are added as repository secrets (offset within the same 2-hour window so each stage runs after the previous one has fresh data):

- [`ingest.yml`](.github/workflows/ingest.yml) — fetches enabled sources (`:17`).
- [`embed.yml`](.github/workflows/embed.yml) — embeds newly persisted signals (`:35`), installs the `embeddings` extra.
- [`case-file.yml`](.github/workflows/case-file.yml) — persists promotable case-file drafts (`:50`). **Currently uses the deterministic extractive builder only** — it is not yet wired to the Gemini-grounded generation path, so enabling it produces the same raw-titled Draft topics described in `docs/audit_and_next_steps.md` Section 7.2, just on a schedule. Fix that gap before leaning on this workflow for real published output.

All three can also be run manually from the Actions tab (`workflow_dispatch`).

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
