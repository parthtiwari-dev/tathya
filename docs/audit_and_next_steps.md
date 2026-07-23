# Tathya — Deep Audit & Next Steps (as of 23 July 2026)

This is a from-source audit of the actual repo (not the execution-plan doc, which is now stale in places — mostly in the *positive* direction: the backend has moved past what it describes). Read this alongside `docs/tathya_roadmap.md` (vision) and `docs/roadmap_execution_plan.md` (older plan, now superseded by this file for "what's left").

No tests, servers, or builds were run to produce this. Everything below is from reading code directly.

---

## 1. Headline finding

**Backend (API v1 + pipeline) is materially ahead of the execution-plan doc. Frontend is materially behind it.**

- API v1 is fully built: typed Pydantic models, camelCase mapping to match `lib/types.ts` exactly, pagination, sub-resource routes, ministry/entity taxonomy, `topic_entities`, `open_questions`, `contradictions` schema support. This is beyond what `roadmap_execution_plan.md` §10 described as "target."
- DB has migrations 001–007 (doc only mentions up to 006). Migration 007 adds slugs, `topic_entities`, `open_questions`, `contradictions` tables — a real taxonomy layer the doc doesn't know about.
- The frontend (`apps/web`) is a fully built, polished component set — feed, topic page, claims ledger, timeline, verifiable facts, contradictions, open questions, trust breakdown, source pages, ministry pages, command palette, i18n (English/Hindi) — **all of it still wired to `lib/mock-data.ts` / `lib/mock-sources.ts`, not the FastAPI backend.** There is no `lib/api.ts`, no fetch client, no `NEXT_PUBLIC_TATHYA_API_URL` usage anywhere in `apps/web`.
- `CorrectionReportButton.tsx` explicitly fakes success with a `setTimeout` — it posts nowhere.
- **This means: the single highest-leverage next step is frontend↔API integration, not new features.** Everything downstream (manual audit, launch gate, lifecycle) is blocked less by missing pipeline work and more by the fact nothing in the browser touches real data yet.

---

## 2. What's actually implemented (verified by reading source)

### 2.1 Database (`db/`)
- `schema.sql` + migrations 001–007, applied in sequence.
- Tables: `sources`, `signals`, `snapshots`, `entities`, `topics`, `topic_signals`, `events`, `claims`, `verifiable_facts`, `topic_relations`, `corrections`, `source_run_metrics`, plus (007) `topic_entities`, `open_questions`, `contradictions`.
- `topics.slug` and `entities.slug` exist with unique indexes, backfilled.
- `upsert_topic_cluster` RPC now takes `p_slug` (idempotent, coalesces existing slug).
- `contradictions` table exists but **nothing writes to it yet** — confirmed in `case_file_builder.py`, which hardcodes `contradictions=()` with a comment explaining cross-signal semantic detection isn't implemented.
- `open_questions` **is** populated, but only via a deterministic structural rule (no official/govt claim present yet) — not semantic detection either. This is honest and roadmap-compliant (no fabrication), just narrower than the UI (`Contradictions.tsx`, `OpenQuestions.tsx`) might imply to a reader.

### 2.2 Ingestion (`pipeline/ingestion/` + `shared/config.py`)
- Watchers exist for RSS, YouTube, PIB, parliament, official website.
- `shared/config.py` STARTER_SOURCES: **14 sources defined, only 3 enabled** (`rbi-press-releases`, `indian-express-india`, `hindustan-times-india`). Disabled: PIB (403 issue per doc), PMO YouTube, PMIndia official site (403), Income Tax RSS, The Wire, Scroll.in, NDTV, Times of India, Guardian, BBC, both Parliament Q&A sources.
- `ARCHIVE_AFTER_DAYS = 60` constant already exists in config — lifecycle logic has its threshold defined but no consumer.

### 2.3 Processing (`pipeline/processing/`)
- Entity matching, near-duplicate scan, embeddings (`intfloat/multilingual-e5-base`, 768-dim), clustering, significance scoring, semantic search — all present and covered by tests (`test_clusterer.py`, `test_embedder.py`, `test_entity_matcher.py`, `test_near_duplicate.py`, `test_significance_scorer.py`).

### 2.4 Generation (`pipeline/generation/`)
- `case_file_builder.py`: deterministic extractive draft builder. Builds events, claims, facts, open_questions from signal rows. No LLM call. This is the "safe" path referenced by the roadmap as fallback.
- `gemini_case_file.py`: LLM-grounded generation path exists separately (structured JSON via Gemini).
- `claims_ledger_builder.py`, `timeline_builder.py`, `relations_builder.py`, `fact_verifier.py`, `summarizer.py` — all present.
- Contradiction detection: **not implemented anywhere** (confirmed above).

### 2.5 API (`api/`)
- `main.py`: full API v1. Endpoints:
  - `GET /health`
  - `GET /topics`, `GET /topics/{id}`, `GET /topics/slug/{slug}`
  - `GET /topics/{id}/claims|events|facts|relations|history`
  - `GET /ministries`
  - `GET /sources`, `GET /sources/{key}`, `GET /sources/{key}/signals`, `GET /sources/{key}/claims`
  - `GET /source-runs`
  - `GET /signals/search` (pgvector semantic search, embeds the query live via `LocalEmbedder`)
  - `POST /corrections`
- `schemas.py` / `mappers.py`: clean separation, camelCase contract matches `apps/web/lib/types.ts` field-for-field (confirmed by direct comparison).
- CORS is currently wide open (`allow_origins=["*"]` unless `TATHYA_CORS_ORIGINS` env var set) — flagged in-code as deliberately deferred, not forgotten.
- Rate limiting on `POST /corrections`: not implemented (also flagged in-code as deferred).
- `GET /corrections/public` (listed as target in the execution-plan doc): **not implemented.**

### 2.6 Frontend (`apps/web/`)
Fully built pages: `/` (feed), `/topic/[slug]`, `/search`, `/ministry/[slug]`, `/source/[key]`, `/sources`, `/about`.
Fully built components: FeedExplorer, FeedItem, ClaimsLedger, Timeline, VerifiableFactsPanel, RelatedTopics, TopicHistory, Contradictions, OpenQuestions, TrustBreakdown, SourcesUsed, SourcePageBody, MinistryPageBody, CorrectionReportButton, CommandK/CommandPalette, LanguageToggle (i18n English/Hindi via `lib/i18n.tsx`), ThemeToggle, IntroAnimation, FilterSidebar, SiteHeader/SiteFooter.

This is **more UI than the roadmap's Phase 4 minimum** (roadmap didn't ask for a command palette, ministry pages, or a dedicated sources explorer — those come from the "Backlog" section, §13 of the roadmap, and they're already built). Genuinely good progress.

**But every single one of these reads from `lib/mock-data.ts` / `lib/mock-sources.ts`.** Confirmed directly in `app/page.tsx`, `app/topic/[slug]/page.tsx`, `app/search/page.tsx`. No component or page fetches from the FastAPI backend. `next.config.ts` has no API rewrite/proxy config beyond default.

There is Hindi i18n scaffolding (`lib/i18n.tsx`, `LanguageToggle.tsx`) already built into the frontend — this gets you partway into roadmap Phase 6 (Hindi reach) for UI strings, though **not** for Hindi *generated* content (summaries/claims), which is a separate, unstarted backend task.

### 2.7 Tests
22 test files under `tests/`, covering API, audit export, case file builder/persist, clusterer, embedder (+ CLI), entity matcher, Gemini case file, generation builders, health check, near-duplicate, RSS watcher, significance scorer, snapshotter, source activation/adapters/audit, Supabase repository, Telegram, text cleaner, topic report.
No lifecycle tests exist (matches: no lifecycle code exists).

### 2.8 CI/CD (`.github/workflows/`)
Only `ingest.yml` exists — runs `pipeline.scheduler --persist` every 2 hours (cron `17 */2 * * *`). No embedding workflow, no case-file-persist workflow, no lifecycle workflow, no health-check-only workflow, no frontend deploy workflow. Embedding/clustering/case-file-persist currently only run manually from a terminal.

---

## 3. Gap list — what's not done, in priority order

### P0 — Blocks everything downstream
1. **Frontend ↔ API wiring.** Build `apps/web/lib/api.ts` as a typed fetch client against the 15 existing endpoints, add `NEXT_PUBLIC_TATHYA_API_URL`, and swap every `mock-data`/`mock-sources` import for real fetches:
   - `app/page.tsx` → `GET /topics` (+ `GET /ministries` for the sidebar)
   - `app/topic/[slug]/page.tsx` → `GET /topics/slug/{slug}`
   - `app/search/page.tsx` → `GET /signals/search?q=...` (currently client-side substring match over mock data — the comment in that file already says exactly what to do)
   - `app/source/[key]`, `app/sources` → `GET /sources`, `GET /sources/{key}`, `GET /sources/{key}/signals|claims`
   - `app/ministry/[slug]` → needs either a new `GET /ministries/{slug}/topics` endpoint or client/server-side filtering of `GET /topics` by `ministrySlug`
   - `CorrectionReportButton.tsx` → real `POST /corrections`
   - Decide fetch strategy per page: server-side fetch/ISR for feed and topic pages (matches roadmap's "static but discretely updated" philosophy, §3.1), small client fetch only for search/corrections.
2. **`lib/mock-data.ts` / `lib/mock-sources.ts` retirement plan.** Keep for local dev without a live backend, but mark clearly as dev-only fallback.
3. **CORS**: once a real frontend origin exists, set `TATHYA_CORS_ORIGINS` explicitly instead of `*`.

### P1 — Needed before any public launch, per roadmap non-negotiables
4. **Manual audit pass** (roadmap Phase 3 gate). Not yet done. `pipeline.audit_export` exists and `audit_claims.csv` / `audit_events.csv` / `audit_facts.csv` already sit in the repo root — check whether these are real exports or stale/empty. If real: add `audit_status`/`audit_issue_type`/`audit_notes` columns and review 30–50 rows each against source snapshots. **This has to happen before public launch regardless of frontend progress.**
5. **`GET /corrections/public`** — listed as target, not built. Needed for History view's correction visibility.
6. **Rate limiting on `POST /corrections`** — needed before public exposure.
7. **Legal consult** (IT Rules 2021 intermediary-vs-publisher status) — external task, still open, roadmap calls it non-optional.
8. **Domain + public repo confirmation** — external/administrative, can't verify from filesystem.

### P2 — Source & data quality
9. **Official source unblocking:** PIB (403), PMIndia (403), Income Tax RSS (403) still disabled. Parliament Q&A still disabled. Currently only RBI is a working official source — Verifiable Facts panel is thin right now.
10. Only 3 of 14 sources enabled. 8 more (Wire, Scroll, NDTV, ToI, Guardian, BBC) sit disabled pending the "one source → audit → inspect → enable" loop.
11. Hindi/regional media sources: none configured yet (Dainik Bhaskar, Amar Ujala, ABP News, Aaj Tak) — separate from the UI-language toggle already built.
12. Wikidata-backed full entity seed (ministries/ministers/MPs/schemes) — still seed-based, not full import.

### P3 — Pipeline automation gaps
13. **Lifecycle (roadmap Layer 6 / Phase 5): completely unimplemented.** No `pipeline/lifecycle/` directory exists. `ARCHIVE_AFTER_DAYS = 60` is defined but unused. Needed: `activity_monitor.py`, `status_manager.py`, SQL/RPC for status transitions, `.github/workflows/lifecycle.yml`, tests for live→archived→live with same topic ID.
14. **Contradiction detection: schema exists, generation doesn't.** `contradictions` table + full frontend component (`Contradictions.tsx`) + API route + mapper all exist and are ready. Only missing piece: a generation step doing cross-signal semantic comparison. High-value next feature since everything around it is already built and tested.
15. **GitHub Actions is single-workflow.** Only ingestion runs on schedule. Needed: `embed.yml`, `case-file.yml` (`--promotable-only` once public), `health.yml` (confirm if already folded into ingest), `lifecycle.yml`.
16. **Topic promotion / status manager:** confirm whether `case_file_persist.py` already flips `raw_cluster → live`, or whether a dedicated promotion step is still needed.

### P4 — Phase 6 / hardening (correctly deferred)
17. Hindi **generated content** (summaries/claims) — separate from UI i18n already built.
18. Telegram mirror of public updates (distinct from the existing operator health-alert bot in `pipeline/monitoring/telegram.py`).
19. Backups / mirror deployment / IPFS archival — correctly deferred per roadmap.

---

## 4. Suggestions beyond the roadmap

- Wire the frontend against a staging Supabase branch first, not the live ingestion DB, so schema edits don't risk the running pipeline.
- Document the open-questions rule (and later, contradictions) directly in the UI copy — a small "why is this shown" note protects against readers assuming LLM inference when it's a deterministic check.
- Turn the two in-code TODO comments (CORS, corrections rate-limit) into tracked issues now so they don't get lost during frontend integration work.
- Check `audit_claims.csv` / `audit_events.csv` / `audit_facts.csv` in repo root — if real, the manual audit could start in parallel with frontend wiring since it's a spreadsheet-review task, not a coding task.

---

## 5. Open questions for you

1. Should `/ministry/[slug]` hit a new `GET /ministries/{slug}/topics` endpoint, or filter over `GET /topics`? Affects whether this is frontend-only or needs an API addition.
2. Are the three audit CSVs in repo root live exports or stale placeholders?
3. For data fetching: server-side fetch/RSC for feed+topic pages, client fetch only for search/corrections — confirm before I build it that way.
4. Priority: frontend wiring first (recommended — proves the whole stack end-to-end), or lifecycle/contradictions first? They don't block each other.

---

## 6. Suggested immediate sprint

1. `apps/web/lib/api.ts` typed client + env var.
2. Wire feed page + topic page to real API.
3. Wire search page to `GET /signals/search`.
4. Wire sources/source pages.
5. Wire `CorrectionReportButton` to real `POST /corrections`, add basic rate limiting.
6. Set `TATHYA_CORS_ORIGINS` for real.
7. Run manual audit pass on existing CSVs (or regenerate first if stale).
8. Then: lifecycle automation, contradiction detection, more workflows.
