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

---

## 7. Update — 24 July 2026 (post frontend-wiring review + real-data screenshot review)

This section supersedes Sections 3, 5, 6 above where they conflict — read this first, then the rest for detail on what's still true.

### 7.1 Confirmed done since the last pass
- `apps/web/lib/api.ts` exists: a typed fetch client (`getAllTopics`, `getTopicBySlug`, `getAllMinistries`, `getTopicsByMinistry`, `getAllSources`, `getSourceByKey`, `getClaimsBySourceKey`, `searchSignals`, `submitCorrection`) against `NEXT_PUBLIC_TATHYA_API_URL`. Every page now calls this, not `mock-data.ts`. **P0 item #1 from Section 3 is done.**
- `CorrectionReportButton` posts to a real `POST /corrections` now (via `submitCorrection`), no more fake `setTimeout`.

### 7.2 NEW critical finding — this is *why* real topics don't look like the mock data
Confirmed by reading `pipeline/case_file_persist.py`, `pipeline/generation/case_file_builder.py`, and `pipeline/gemini_case_file_report.py` directly:

- `case_file_persist.py` — the **only** script that writes topics/claims/events/facts into Supabase — calls `build_case_file_draft()`, the deterministic **extractive** builder. It never calls `generate_grounded_case_file()` (the Gemini-grounded path in `pipeline/generation/gemini_case_file.py`).
- `gemini_case_file_report.py` **does** call the Gemini path, but only prints the JSON to stdout for inspection. It has no persistence call at all — it's a preview CLI, not a pipeline stage.
- Net effect, confirmed against the screenshot: every topic in the DB right now has `title = cluster.key` (a raw entity/keyword bucket — literally why you're seeing "Reserve Bank of India" and "Narendra Modi" as headlines instead of narrative titles), and `neutral_summary` is the literal f-string from `case_file_builder.py`: `f"{signal_count} canonical signals from {source_count} source(s) currently cluster around: {representative_title}"`. Nothing sets ministry or flips `status` from `raw_cluster`/draft to `live`, so every card renders Draft / Unclassified.
- **This is not a mock-data problem or a frontend bug.** It's a real pipeline stage — Phase 3 generation — that was built (both the extractive fallback and the Gemini path exist and are tested) but never wired into the one script that actually persists to the database. What the mock data shows is what a topic looks like *after* Phase 3 generation + promotion; what's live is Phase 2 clustering output, displayed as if it were a finished case file.
- **Fix (this is now the single highest-leverage next step, above sources work):**
  1. Give `case_file_persist.py` a path that calls `generate_grounded_case_file()` per cluster and persists *that* draft's title/summary/claims/events/facts, with the existing extractive builder kept as an explicit fallback if the Gemini call fails (never silently — log which path produced each topic).
  2. Wire `significance_scorer`'s `promotable` flag to actually set `topics.status = "live"` (right now `--promotable-only` only filters *which clusters get persisted*, not the status column itself — confirm this and fix if so).
  3. Set `ministry` on persist from entity resolution (a topic's dominant `ministry`-typed entity), not left null/"Unclassified".
  4. Re-run `case_file_persist.py` against current signals once this is fixed and manually compare 5–10 resulting topics against the mock data's shape before trusting the feed.

### 7.3 24/7 operation — nothing runs continuously today, confirmed
Only `.github/workflows/ingest.yml` is scheduled (every 2 hours). Embedding, clustering, case-file persistence, and Gemini generation are **all manual, run-from-your-terminal-only** right now (`pipeline/embed_signals.py`, `pipeline/case_file_persist.py`, `pipeline/gemini_case_file_report.py` — none have a workflow). This means: even with 7.2 fixed, the site will stay frozen the moment you close your laptop, because nothing regenerates topics without you typing a command.
See the "Deployment" section of the chat reply for the concrete fix (new GitHub Actions workflows + hosting the API and frontend somewhere other than localhost).

### 7.4 Sources — planned overhaul (per your instruction, 24 Jul 2026)
Current state: 14 sources defined in `shared/config.py`, only 3 enabled (RBI, Indian Express, Hindustan Times). Target: 100+, spanning the full spectrum, before the significance scorer and Claims Ledger have enough independent signal density to be credible.

**Target source categories (extends `docs/source_research.md` — read that alongside this):**
1. **Official** (`trust_category=official`): PIB, PMO, every central ministry's own RSS/press page, Lok Sabha/Rajya Sabha Q&A, PRS Legislative Research, data.gov.in, gazette notifications. Currently blocked: PIB/PMIndia/Income Tax RSS all return 403 — need a compliant fetch approach (proper User-Agent, rate limiting, or an official API/bulk-data route) before re-enabling, not a scraping workaround that risks a ban.
2. **Mainstream media, deliberately spanning the spectrum** (`trust_category=media`): The Hindu, Indian Express, Hindustan Times, Times of India, NDTV — alongside Republic, Times Now, News18, Zee News, Aaj Tak, ABP News — alongside The Wire, Scroll.in, Newslaundry, Article 14, The Caravan, Frontline — alongside OpIndia, Swarajya. The point per non-negotiable #3 is that *all* of these get the same Claims Ledger treatment, none gets a quality/trust weighting based on your own read of their politics — only `trust_category` (official/media/citizen/foreign) and whether a claim is a verified duplicate matter.
3. **Foreign** (`trust_category=foreign`, higher credibility weight per the roadmap): Reuters, AP, BBC, Al Jazeera, The Guardian.
4. **Hindi & regional**: Dainik Bhaskar, Amar Ujala, Jansatta (RSS), plus Aaj Tak/ABP/Zee as YouTube channels transcribed the same way as English video — do not skip, roadmap flags rural/regional stories often break here first or exclusively.
5. **Independent YouTube commentary/analysis** (new bucket, `trust_category=citizen` — these are individual voices, not institutions, so this is the correct existing bucket rather than a new enum value): channels that do long-form (20–40 min) researched commentary across the spectrum — you named Samdish (Bhatia) and Think School as examples of what you want; the same tier includes channels like Dhruv Rathee, Akash Banerjee/The Deshbhakt, Ravish Kumar's own channel on one end, and channels with an opposite lean on the other (verify current politics/tone yourself before adding any — labels drift over time and I'm not going to assert a specific person's politics as fact in your source config; treat this as a starting list to check, not a finished one). Ingested the same way as any YouTube source: `youtube-transcript-api`, transcript stored in the signal's `transcript` field, language tag kept (Hindi/English) so nothing needs translation to be ingested — only translated later if you build the Hindi-generation phase.
6. **"What ordinary people are saying"** — until X API is affordable, don't build a new ingestion path for this. Extract it from what already exists in signals you're ingesting: vox-pop segments inside news video transcripts, citizen-journalism YouTube channels, and reader-comment/reaction roundups that outlets like the ones above already publish as their own articles or segments. This keeps you inside non-negotiable #7 (ordinary bystanders aren't identified beyond what they made public) almost for free, because you're taking it from an already-published third-party account of public reaction rather than scraping individuals directly.

**Mechanically, adding 100+ sources is small, repeated work, not new architecture:** every entry is a `SourceDefinition` in `shared/config.py` (or better, move this list to a seed SQL/CSV once it's this large, so adding a source doesn't require a code change + redeploy — worth doing now given the scale you want). The real cost is per-source verification: confirm the RSS/YouTube feed URL is correct, confirm no 403/robots block, confirm timestamps parse correctly, run it once, spot-check the signals it produces — the "one source → audit → inspect → enable" loop the audit already recommends in P2. At 100+ sources this loop is the actual bottleneck, not the code.

**Do not enable a source faster than you can verify it.** A bad feed URL that silently 403s or returns stale data is worse than not having the source, because it can create a false "no signal" reading that skews significance scoring. Batch this in groups of ~10, verify, then move to the next batch.

### 7.5 Updated priority order (replaces Section 3's list where they overlap)
1. **Fix the Gemini-generation persistence gap (7.2).** Nothing else matters if every topic looks like a raw cluster.
2. **Automate what's currently manual (7.3):** `embed.yml`, `case-file.yml` workflows so the pipeline runs without you.
3. **Deploy the API and frontend off your machine** (see chat reply) — required for both #2 and for "24/7" to mean anything.
4. **Manual audit pass** on real (post-fix) generated claims/events — this was blocked before because there was nothing Gemini-grounded to audit; now there will be.
5. **Sources expansion (7.4)** — batched, verified, not all at once.
6. Everything from Section 3's P1–P4 (corrections rate limiting, CORS lockdown, lifecycle automation, contradiction detection) — unchanged, still valid, still after the above.

---

## 8. Deployment & keep-alive (24 July 2026)

### 8.1 Render free tier — what's actually free and what isn't
Confirmed via research (pricing changes, so re-verify before relying on this): Render's **free web service tier is still real** as of mid-2026 — no credit card required, 750 free instance-hours/month, but it **sleeps after 15 minutes of no HTTP traffic** and cold-starts in 30–60s. Render's **Cron Jobs are a separate, paid product** — billed per second with a **$1/month minimum** — so "set up a Render cron job to ping the Render API" is not actually the free option it sounds like; it just moves the cost from "web service" to "cron job" on the same platform.

**Correct free approach:** keep the web service on Render's free tier, and ping it from an *external* free service, not from Render itself:
- **cron-job.org** — free, no card, intervals down to 1 minute.
- **UptimeRobot** — free tier, 5-minute intervals, plus real uptime alerts as a side benefit.

Point either at `GET https://<your-service>.onrender.com/health` (already returns `{"status": "ok"}`, confirmed in `api/main.py`) on a **10-minute** schedule — safely inside Render's 15-minute sleep window, so the instance never goes fully idle and never has to cold-start for a real visitor.

### 8.2 A real memory risk on Render free tier, specific to this API
`GET /signals/search` in `api/main.py` instantiates `LocalEmbedder()` **per request** (not at startup — confirmed by reading the route), which loads `intfloat/multilingual-e5-base` (~278M params) via `sentence-transformers`/torch. That's roughly 1GB+ in memory. **Render's free tier caps RAM at 512MB.** Every other endpoint (`/topics`, `/sources`, `/ministries`, etc.) doesn't touch this and will run fine. But the first real hit to `/signals/search` on this tier will very likely **OOM and crash the instance**, which then cold-starts again on the next request. This is not solved by the keep-alive ping — it's a separate, code-level constraint. Options, cheapest first:
1. Accept degraded/absent semantic search on this deployment for now; keep it working locally/in a dev environment only.
2. Cache `LocalEmbedder` as a module-level singleton so the model loads once per instance-lifetime instead of per-request — reduces *repeated* load cost but does not raise the 512MB ceiling, so this alone doesn't fully fix it.
3. Move to a host with more RAM once semantic search needs to work in production (see 8.3).

### 8.3 The actually-free, no-pinging alternative: Oracle Cloud "Always Free"
Oracle's Always Free tier includes a real Ampere A1 VM (up to 4 OCPUs / 24GB RAM) that runs forever at no cost — a real always-on machine, not a scale-to-zero container, so there's no 15-minute sleep and no 512MB ceiling to worry about. Requires a card on file for identity verification but does not charge it for Always Free resources. Setup is more manual than Render (provision the instance, install Python, run the API via a `systemd` service, put Caddy or Nginx in front for free automatic HTTPS, point the domain at it) but solves both the uptime problem and the memory problem in one move. Recommended path: launch on Render + external ping now to get unblocked, move to Oracle once the semantic search feature needs to actually work for real users.

### 8.4 Render deploy settings (for the API specifically)
- **Build command:** `pip install ".[api]"` — add `,embeddings` (`pip install ".[api,embeddings]"`) only once you've made a call on 8.2, since it's the extra that pulls in torch/sentence-transformers.
- **Start command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- **Env vars needed:** `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `TATHYA_CORS_ORIGINS` (set to the real Vercel frontend URL once deployed, not `*`), `GEMINI_API_KEY` if any generation-related code path is reachable from the API process.
- **Health check path (Render setting):** `/health` — lets Render's own dashboard also know the instance is up, independent of the external pinger.

### 8.5 Pipeline automation — workflows added
`.github/workflows/embed.yml` and `.github/workflows/case-file.yml` have been added, following the exact pattern of the existing `ingest.yml` (checkout → setup-python 3.12 → `pip install` with the right extras → run the module with its Supabase secrets). Schedules are offset within the same 2-hour window as ingestion (`:17` ingest → `:35` embed → `:50` case-file) so each stage runs after the previous one has had time to land fresh data, rather than racing it. `case-file.yml` runs `pipeline.case_file_persist --promotable-only` — **this still uses the deterministic extractive builder until the Gemini-generation-persistence gap in Section 7.2 is fixed.** Turning this workflow on before that fix just automates the production of more raw-entity-titled Draft topics on a schedule — fix 7.2 first, then rely on this workflow.
