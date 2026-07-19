# Phase 0 and Phase 1 Completion Checklist

Use this as the operational gate before Phase 2 AI/clustering work.

## Phase 0

- AGPL repository exists.
- Supabase schema has been run.
- `db/seed_sources.sql` has been run after every source registry change.
- `db/seed_entities_core.sql` has been run once.
- Gemini API key exists in local `.env` and GitHub Actions secrets, but is not used yet.
- Telegram secrets exist locally and in GitHub Actions.
- `docs/mission_ethics.md` is reviewed and accepted as the About-page north star.
- Media/IT-law review is still required before public launch or broad public snapshot display.

## Phase 1

- Only validated sources are enabled in `shared/config.py`.
- Disabled candidate sources can be audited with `python -m pipeline.source_audit --source SOURCE_KEY`.
- Every enabled source has at least 10 inspected rows with good timestamps, canonical URLs, raw text, and snapshot hashes.
- `python -m pipeline.scheduler --persist` succeeds locally.
- GitHub Actions scheduled ingestion succeeds.
- Repeated runs add `source_run_metrics` rows and do not duplicate already-seen source URLs.
- Telegram `--test-alert` succeeds.
- Supabase has hundreds to thousands of signals with one snapshot per signal.
- Official sources are represented before AI promotion is trusted.
