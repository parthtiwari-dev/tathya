# Tathya

Tathya (तथ्य, “fact”) is an autonomous, non-partisan record of India's Union Government. It does not manually select topics or issue AI verdicts: configured public sources are watched continuously and clustered into sourced case files showing what government, media, and citizens said. You decide.

## Current foundation

This foundation now provides the project layout, typed pipeline models, an immutable snapshot builder, the Supabase/Postgres schema, a source registry, and a dry-run ingestion command. It does **not** yet write to Supabase.

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
2. In its SQL Editor, run [`db/schema.sql`](db/schema.sql), then [`db/seed_sources.sql`](db/seed_sources.sql).
3. Copy `.env.example` to `.env` and fill in the project URL and service-role key. Keep `.env` private.

The schema makes `snapshots` append-only at the database level; source pages may change or disappear, but a captured source record cannot silently change.

After the database and source seed are in place, persist the enabled watcher output with:

```powershell
python -m pipeline.scheduler --persist
```

This calls the database's atomic `record_signal_snapshot` function. Re-running it is safe: the same source URL does not create a second signal, and exact content duplicates are linked to their first canonical signal.

Each persisted run also records its source count. After three successful historical runs, a run below 20% of its recent median is printed as an alert; Telegram delivery is the remaining deployment integration.

## Scheduled ingestion

[`ingest.yml`](.github/workflows/ingest.yml) runs enabled sources every six hours after you add `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` as GitHub repository secrets. It can also be run manually from the Actions tab.

## RSS sources

The initial registry records PIB press releases, The Indian Express India feed, and The Wire. The scheduler currently polls only the Indian Express feed: PIB needs its dedicated scraper, while The Wire is disabled because it currently does not return a parseable feed to the transparent watcher user-agent. The scheduler fetches, parses, and snapshots feed entries; it never decides which stories matter. Add sources to `shared/config.py`, never individual stories.

See [`docs/source_research.md`](docs/source_research.md) for the current multi-source activation register and the reason every non-enabled source is held back.

## Before persistence

Run the schema after creating Supabase. The next pipeline slice will use the database function `record_signal_snapshot` to atomically persist each signal with its immutable snapshot.
