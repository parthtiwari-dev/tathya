# Tathya

Tathya (तथ्य, “fact”) is an autonomous, non-partisan record of India's Union Government. It does not manually select topics or issue AI verdicts: configured public sources are watched continuously and clustered into sourced case files showing what government, media, and citizens said. You decide.

## Current foundation

This first implementation slice provides the project layout, typed pipeline models, an immutable snapshot builder, the Supabase/Postgres schema, and an RSS adapter. It does **not** yet contact external sources or write to Supabase.

## Run locally

Use Python 3.11+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
```

## Database setup

1. Create a Supabase project.
2. In its SQL Editor, run [`db/schema.sql`](db/schema.sql).
3. Copy `.env.example` to `.env` and fill in the project URL and service-role key. Keep `.env` private.

The schema makes `snapshots` append-only at the database level; source pages may change or disappear, but a captured source record cannot silently change.

## Before enabling RSS ingestion

The roadmap's source outlets are intentionally not entered with guessed feed URLs. In the next loop, verify each publisher's official RSS endpoint and then add it to `shared/config.py`; no topics will be configured manually.
