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

### 7.4.1 PIB fixed — real bug, real cause, 24 July 2026
The "PIB returns 403" note from earlier turned out to be wrong. Directly fetching `https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3` returns a valid, live RSS 2.0 feed with no blocking at all. The real problem was a **two-file drift**, exactly the risk this doc warned about in 7.4: `shared/config.py` had already been corrected to `Regid=3` at some point, but `db/seed_sources.sql` still had the old, wrong `Regid=1` and `enabled=false`. Both files are now fixed and in agreement (`Regid=3`, `enabled=true`). Two things to know before trusting this source fully:
- **PIB's RSS is organized by content-type and region, not by ministry.** `ModId=6` ("Releases") under `Regid=3` ("National") already covers every ministry combined in one feed — no per-ministry adapter work needed, which is simpler than originally assumed.
- **Items observed in a sample fetch had title + link only, no description/body text.** If that holds for the real Releases feed (not just the Media Advisories sample checked), PIB signals will be thinner than RBI's or a media outlet's — still useful as official titles + direct source links, just don't expect rich claim text to come out of PIB alone.
- Remember to re-run `db/seed_sources.sql` against Supabase once (it only updates the `sources` table row — the scheduler reads `STARTER_SOURCES` from `config.py` directly, so `enabled=True` there is what actually makes ingestion pick it up).

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
- **Repository / Root Directory:** connect the repo as-is; leave Root Directory **blank** (`.`) — `pyproject.toml` and `api/` live at repo root, not inside `apps/web`. (`apps/web` is the separate Next.js app that goes to Vercel, not Render.)
- **Runtime:** Python 3.
- **Build command:** `pip install ".[api]"` — deliberately **without** the `embeddings` extra by default. Confirmed by reading `pipeline/processing/embedder.py`: the `sentence-transformers` import is deferred inside `LocalEmbedder.__init__`, not at module import time, so without the `embeddings` extra installed, hitting `/signals/search` fails cleanly with a 500 (missing dependency) instead of risking an OOM crash that could take the whole free instance down. Add `,embeddings` (`pip install ".[api,embeddings]"`) only once you've deliberately accepted the RAM risk from 8.2 or moved to a host with more memory.
- **Start command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- **Python version:** add a `runtime.txt` file at repo root containing `3.12.7` (or set the `PYTHON_VERSION` env var to the same) so Render matches the same version as `.github/workflows/*.yml` and local dev, rather than defaulting to whatever Render's platform default is at the time.
- **Instance type:** Free.
- **Env vars needed** (from `.env.example`): `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` — required, the API cannot start meaningfully without these. `TATHYA_CORS_ORIGINS` — set to the deployed Vercel frontend's real URL once it exists (comma-separated if more than one origin); leave unset only for initial testing, since unset defaults to `*` per the code. `GEMINI_API_KEY` — not required for the API process today (no route currently calls Gemini directly), safe to skip unless that changes. `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` — not needed by the API either, those are for the pipeline's health-alert bot only.
- **Health check path (Render setting):** `/health` — lets Render's own dashboard also know the instance is up, independent of the external pinger.

### 8.5 Pipeline automation — workflows added
`.github/workflows/embed.yml` and `.github/workflows/case-file.yml` have been added, following the exact pattern of the existing `ingest.yml` (checkout → setup-python 3.12 → `pip install` with the right extras → run the module with its Supabase secrets). Schedules are offset within the same 2-hour window as ingestion (`:17` ingest → `:35` embed → `:50` case-file) so each stage runs after the previous one has had time to land fresh data, rather than racing it. `case-file.yml` runs `pipeline.case_file_persist --promotable-only` — **this still uses the deterministic extractive builder until the Gemini-generation-persistence gap in Section 7.2 is fixed.** Turning this workflow on before that fix just automates the production of more raw-entity-titled Draft topics on a schedule — fix 7.2 first, then rely on this workflow.

---

## 9. Status check — 24 July 2026, post-deployment

Both site (`tathya-1.vercel.app`) and API (`tathya-zi9p.onrender.com`) are now actually live. Re-confirming what's still open now that "deployed" is real and not hypothetical:

1. **Section 7.2 (Gemini-generation persistence gap) is unchanged and still unfixed as of this check.** This remains the single highest-leverage next task — it is the reason the live, public site currently shows raw cluster titles instead of narrative case files, and every other item below is secondary to it in terms of visible impact.
2. **CORS is not yet locked down against the real deployed origin.** `TATHYA_CORS_ORIGINS` should be set on Render to `https://tathya-1.vercel.app` now that this is a real, known URL — Section 3 item 3 / P1 item 6 previously only said "once a real frontend origin exists," which is now the case. This is a five-minute Render dashboard change, do it regardless of what else is in progress.
3. **Domain is still a subdomain of Vercel/Render, not a custom domain.** Fine for continued testing; the roadmap's Phase 0 checklist still expects a real `.in`/`.org` domain before calling this genuinely public. Not urgent while the Gemini-generation gap is open — nobody should be pointed at this as a finished product yet regardless of domain.
4. **`case-file.yml` remains correctly un-relied-upon** per 8.5 — do not schedule/enable it for real until item 1 above is fixed, same caveat as before, restated here because it's now live infrastructure rather than a draft workflow file.
5. Everything else from Section 7.5's priority list (manual audit pass, sources expansion, corrections rate limiting, lifecycle, contradiction detection) is unchanged since the last update — no new movement on these to log yet.

---

## 10. Independent code review — 25 July 2026 (frontend + backend, no docs read first)

This was a from-source review done *before* re-reading this file or the roadmap, then reconciled against both afterward. Where it confirms something already logged above, that's noted briefly; only genuinely new findings are detailed.

### 10.1 Correction to Section 2.7 / Section 3 P3 #13 — lifecycle is no longer unimplemented
This file's Section 2.7 ("no lifecycle tests exist (matches: no lifecycle code exists)") and Section 3 P3 #13 ("completely unimplemented, no `pipeline/lifecycle/` directory exists") are now **stale**. As of this review, `pipeline/lifecycle/activity_monitor.py` and `pipeline/lifecycle/status_manager.py` both exist, and `.github/workflows/lifecycle.yml` is live (daily cron, `30 3 * * *`, archives stale Live topics per `ARCHIVE_AFTER_DAYS`). The workflow's own header comment confirms reopen (archived → live on new activity) happens inside `case_file_persist.py`'s persist step, not in `status_manager.py`. Net: P3 #13 can be marked done for the archive direction; worth explicitly re-verifying the reopen path once 7.2 is fixed and real narrative topics exist to test it against, since it's currently unexercised by anything but raw-cluster drafts.

### 10.2 NEW — likely-crashing bug in `/signals/search`, independent of the Section 8.2 OOM risk
`api/main.py`'s search endpoint calls `embedder.encode_queries([q])[0]`. `pipeline/processing/embedder.py`'s `LocalEmbedder` only defines `encode_query` (singular) and `encode_passages` — there is no `encode_queries` method anywhere in the repo (confirmed by a full-repo content search). If this reading is right, every call to `/signals/search` — which is both the `/search` page and `lib/api.ts`'s `searchSignals` — raises `AttributeError` **before** the Section 8.2 memory/OOM concern even becomes relevant, on any host, embeddings extra installed or not. This should be verified with one real request (local or against the Render deployment) and, if confirmed, is a one-line fix (rename the call or add an `encode_queries` method). Flagging ahead of 8.2 since it would mean semantic search is currently broken outright, not just fragile on free-tier RAM.

### 10.3 Design-risk flag, not a bug — the `promotable` gate can suppress exactly the kind of story this project exists for
`significance_scorer.py`'s `promotable` (roadmap Section 3, Layer 4) requires **both** an official source and a non-official (media/citizen) source present. This is documented, deliberate design, not an oversight — but it's worth naming the concrete failure mode it creates: a story with heavy independent/citizen/media coverage that the government simply never comments on (declines to respond, stays silent, or the ministry in question isn't watched yet) can never cross the promotion threshold, regardless of how significant it is. Given the project's own origin (a student protest over a paper leak — precisely the kind of story where an official acknowledgment may be slow, partial, or never come), this deserves a second look before wide launch: e.g. promoting on strong independent corroboration alone, with "no official response yet" surfaced explicitly via `open_questions` (which already has the structural machinery for exactly this — see `case_file_builder.py`'s `_open_questions`) rather than the topic never becoming visible at all. Not urgent relative to 7.2/10.2, but worth a deliberate decision either way rather than leaving it as an unexamined side effect of the significance formula.

### 10.4 Frontend hygiene items not previously logged (small, no architecture change needed)
- `components/CommandK.tsx` is dead code: a second, unused Cmd+K handler (navigates to `/search`) that is never imported anywhere (confirmed by repo search) and would conflict with `CommandPalette.tsx` (opens a modal) if it ever were mounted. Safe to delete.
- Translation strings in `lib/i18n.tsx`'s central `dict` are re-declared locally, verbatim, in roughly a dozen components (`ClaimsLedger`, `Timeline`, `Contradictions`, `VerifiableFactsPanel`, `TopicPageBody`, `RelatedTopics`, `TopicHistory`, `SourcePageBody`, `SourcesIndexBody`, `search/page.tsx`, others) instead of importing from `dict`. Works today, but it's a drift risk — an edit to one copy silently leaves the other stale. Worth consolidating into `lib/i18n.tsx` while the string count is still manageable.
- `lib/format.ts`'s `relativeTime()` returns hardcoded English ("just now", "2h ago", "3d ago") regardless of `lang` — the one un-translated string currently visible on every topic card and every claim, in an otherwise fully bilingual UI.
- Every API-facing fetch that can fail (`getTopicBySlug`, `getSourceByKey`, `searchSignals`, `CommandPalette`'s topic fetch) catches all errors uniformly and returns `undefined`/`[]`, which renders identically to a genuine "not found"/"no results." For a platform whose core promise is honesty about what is and isn't known, a real backend outage currently looks exactly like "nothing exists here" — worth a distinct error state before wider launch.
- `db/migrations/008_topic_status_promotion.sql`'s `upsert_topic_cluster` upserts on `topics.title` (unique constraint). Two unrelated clusters that happen to generate the same raw title text will merge into one topic; minor title drift on the same real story forks into duplicate topics instead of merging. Especially collision-prone right now since live titles are still raw `cluster.key` values (per 7.2), not generated narrative titles — worth revisiting once 7.2 lands, since narrative titles will reduce but not eliminate the risk.
- `MinistryPageBody` doesn't call `notFound()` for an unknown ministry slug — it silently renders the raw slug string as the page title with zero topics, instead of a proper 404.

### 10.5 Two small transparency opportunities, not gaps
- `TopicSummary.significanceScore` is computed by the pipeline and returned by the API but never rendered anywhere in the frontend. Given the About page explicitly describes "crosses a fixed significance threshold" as the sole promotion mechanism, surfacing the score (even subtly, e.g. on hover) would make that specific claim independently checkable by a skeptical reader rather than something they have to take on faith.
- `HistoryEntry.id` is synthesized as `f"{type}-{index}"` in `api/mappers.py` rather than a real database row id — fine for the current read-only, single-response rendering, but not a stable identifier if a future feature ever needs to deep-link to one specific history entry.

---

## 11. Two live workflow failures diagnosed and (partially) fixed — 25 July 2026

Both diagnosed from real `ingest.yml` / `case-file.yml` run logs the user pasted in, not from re-reading code cold.

### 11.1 `ingest.yml` — PIB 403, others fine (fixed in code, unverified until next scheduled run)
`pib-press-releases` failed with `HTTP Error 403: Forbidden`; the other three enabled sources (RBI, Indian Express, Hindustan Times) succeeded, 310 signals total persisted. Confirmed via a fresh web search that the exact feed URL (`pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3`) is live and returning content right now from outside the GitHub Actions network — so the feed isn't dead, and this isn't a repeat of the old `Regid=1` drift documented in 7.4.1. Most likely cause: `pib_scraper.py`'s request used `User-Agent: "Tathya/0.1 (+https://github.com/)"`, which openly self-identifies as an automated GitHub-affiliated bot — exactly the kind of signature a NIC-hosted government WAF is likely to pattern-match and block, separately from whatever it does with datacenter/CI IP ranges. **Fix applied:** `pib_scraper.py` now sends a standard browser User-Agent plus `Accept`/`Accept-Language`/`Referer` headers instead. This is a reasonable best-effort fix but **not a confirmed one** — it can only be verified by watching the next scheduled `ingest.yml` run. If PIB still 403s after this change, the block is more likely IP/ASN-based (GitHub Actions runner ranges are widely blocklisted by WAFs) rather than header-based, and the honest next move is to set `enabled=False` on `pib-press-releases` in `shared/config.py` again rather than let a known-unreliable source fail the whole job every 2 hours.

Separately, worth knowing (not changed): `scheduler.py`'s exit code is `1` if *any* enabled source fails, even though the loop is explicitly designed to let other sources keep running (`"A broken source must not stop all other watchers"`). This is arguably correct — a red X in the Actions tab is a legitimate way to surface "something needs attention" on top of the Telegram alert — but it does mean one known-fragile official source can make a fully-successful 310-signal run look like a failed job at a glance. Left as-is rather than silently softened, since loosening a failure signal is a product decision, not a pure bug fix — flagging it here in case that's not the intended visibility.

### 11.2 `case-file.yml` — RPC 404 on `upsert_topic_cluster`, root cause is a DB-side gap this doc already predicted
The traceback shows `HTTP Error 404: Not Found` calling `POST /rest/v1/rpc/upsert_topic_cluster` from `persist_case_file_draft` (`pipeline/storage/supabase_repository.py`). The Python-side call and migration `008_topic_status_promotion.sql`'s function signature match exactly (`p_title, p_signal_ids, p_significance_score, p_summary, p_slug, p_promotable`) — confirmed by direct comparison. A 404 from PostgREST's RPC endpoint (as opposed to a 400/500) specifically means it found no function matching that name *and* argument signature in its schema cache. Given `case-file.yml`'s own header comment already named this exact risk ("without [migration 008] applied to Supabase, `upsert_topic_cluster` still hardcodes `status='raw_cluster'`"), the most likely explanation is that **migration 008 was never actually applied to the live Supabase project** — the code was updated to call the new 6-parameter version, but the database still only has the older signature (or the function exists but PostgREST's schema cache hasn't been reloaded since it was added, which is a separate, common Supabase gotcha with the same symptom).

**This is not fixable from the filesystem** — it requires running SQL against the live Supabase project directly. Concrete steps for whoever has Supabase dashboard access:
1. Open the Supabase project's SQL Editor.
2. Run the full contents of `db/migrations/008_topic_status_promotion.sql` (safe to re-run — it's a `create or replace function`, not a one-time `alter`).
3. If it still 404s after that, reload PostgREST's schema cache explicitly — either via Supabase's dashboard (Database → API → "Reload schema") or by running `NOTIFY pgrst, 'reload schema';` in the SQL Editor. Supabase normally does this automatically on a `create or replace function`, but it's the single most common cause of a stale-schema 404 if the automatic reload didn't fire for some reason.
4. Re-run `case-file.yml` manually (`workflow_dispatch`) once, watch it complete, then trust the scheduled cron again.

Until this is confirmed applied, `case-file.yml` will keep failing every 2 hours on schedule — same underlying gap as Section 7.2's Gemini-persistence finding, but this is the more basic prerequisite underneath it: no topic can be persisted via this function at all right now, grounded or extractive, narrative title or raw cluster key.

### 11.3 Why "the frontend never showed new news even when these used to work"
Worth naming explicitly: even on a run where `case-file.yml` succeeds, every topic it persists today is still a raw-cluster-titled draft per Section 7.2 (no Gemini-grounded generation wired into `case_file_persist.py` yet, `status` only flips to `live` via the `promotable` gate discussed in 10.3). So there are two independent reasons the public site hasn't been visibly updating: (1) `case-file.yml` has been failing outright on the RPC 404 above, and (2) even a successful run wouldn't have produced anything that looks like a finished case file yet. Fixing 11.2 unblocks *a* topic getting persisted; it does not by itself fix what that topic looks like — Section 7.2 is still the next task after that.

---

## 12. Full fresh-start rebuild, all four workflows run clean — 25 July 2026, and a real architectural gap it surfaced

After the DB wipe (Section 11's fix applied, all seeds correctly re-run this time), all four workflows succeeded end to end for the first time: `ingest.yml` persisted 330 signals across all 4 enabled sources (PIB included — the header fix from 11.1 held), `embed.yml` embedded 200/330, `case-file.yml` ran clean with zero RPC errors, and `lifecycle.yml` correctly no-opped ("No stale live topics found"). But `case-file.yml`'s own summary line read `Total case-file drafts persisted: 0 (grounded: 0, extractive fallback: 0, extractive-only: 0)` — so `topics` is still empty, and the frontend correctly shows nothing, because there is genuinely nothing to show yet. Not a bug in the display path.

Digging into *why* nothing was promotable surfaced something worth flagging on its own:

**`pipeline/processing/clusterer.py`'s `cluster_signals()` never touches the `embedding` column at all.** Clustering works entirely by matching a signal's title against the ~34 hand-seeded rows in `entities` (via `match_entities`) — if a title doesn't contain one of those exact names or aliases, the signal falls into `fallback_bucket()`, which groups purely by the first few long words of the title. Two outlets covering the same real event almost never phrase a headline identically, so fallback buckets essentially never merge signals from different sources in practice. The practical consequence: `promotable` (2+ distinct sources, including one official) can currently really only be hit when multiple sources happen to name one of those ~34 known entities in their title — which is a narrow surface across a fresh 330-signal, single-pass ingest. `seed_entities_core.sql`'s own header comment already flags the entity list as a "starter spine only," so this isn't a new problem, but it's now a *confirmed, load-bearing* one: the entity list's completeness directly gates whether anything is ever promotable, not just how well things get tagged for the Ministry pages.

A second-order effect of this: `embed.yml` — which downloads roughly 2GB of PyTorch/CUDA dependencies and takes 3+ minutes every scheduled run — currently has **zero influence on what gets promoted**. It exists solely to power `/signals/search`'s separate semantic search endpoint. Two systems that look connected (both operate on the same `signals` table, both matter for "finding the same story twice") but aren't wired together at all right now.

**Diagnostic added, not yet a fix:** `case_file_persist.py` now prints every cluster it finds — signal count, distinct source count, official/non-official presence, score, and promotable status — before filtering, regardless of `--promotable-only`. Previously the only visible output was a single "0 persisted" number with no way to tell "clustering found nothing" from "clustering found several plausible topics, none crossed the bar yet." Re-running `case-file.yml` now will show which of those two it actually is.

**Two real paths forward, not yet decided between:**
1. Expand `seed_entities_core.sql` meaningfully (schemes, more ministers/MPs/opposition figures, ongoing named controversies/events) so more real stories have a shared anchor entity across sources — the more mechanical, incremental fix.
2. Wire the existing embeddings into `cluster_signals()` as a similarity-based grouping path (e.g. group near-duplicate/high-cosine-similarity signals regardless of shared named entity), so clustering isn't solely dependent on the hand-seeded list — the more structural fix, and the one that would also finally make the embed.yml compute cost pull its weight for something beyond search.

Neither is applied yet; this section is the diagnosis, not the resolution.

---

## 13. Decision: `promotable` gate removed — 25 July 2026

Following from Section 10.3's flag and Section 12's real-data confirmation of it (RBI's own cluster had `official=True` but sat alone with 1 source; four other clusters had 2 sources but `official=False` on all of them — the two vocabularies never overlapped once on a real run), the decision was made to remove the gate rather than keep patching around it.

**Change:** `pipeline/processing/significance_scorer.py`'s `promotable` is now always `True`. Nothing else was touched — `case_file_persist.py`'s `--promotable-only` flag, `upsert_topic_cluster`'s `p_promotable` parameter, and the SQL function's `status = case when p_promotable then 'live' else 'raw_cluster' end` logic are all still wired exactly as before. They just now always evaluate to "live," since the one input that used to sometimes make them false no longer does. No SQL migration, no workflow change, no Supabase action needed for this one.

**Why this over patching the entity list or wiring in embeddings (Section 12's other two options):** those are still worth doing for clustering *quality* (whether two signals about the same real event get grouped together at all), but they don't address the deeper question Section 10.3 raised: should *any* fixed rule about official/non-official presence decide whether a real, adequately-covered story is allowed to exist on the site. Given the project's own founding motivation, the answer landed on no — existence should depend on the story being real and covered, not on whether the government chose to comment on it.

**What this does not remove:** `score`, `canonical_count`, `independent_source_count`, `official_source_present`, and `media_or_citizen_source_present` are all still computed and stored exactly as before — nothing here throws away signal, it only stops that signal from gating existence. The explicit intent (stated by the project owner) is to build a ranking/recommender system on top of these fields later, to decide *display order and prominence*, not *presence*. That system does not exist yet — right now, ordering is whatever `cluster_signals()`'s `limit` and sort (`score` descending, then signal count) naturally produce, same as before this change.

**New honest tradeoff worth watching:** with the gate gone, a thin cluster (e.g. one press release with no independent pickup at all) can now go fully "Live" rather than sitting as a "Draft" the way it would have before. Whether that's the right call long-term is exactly what a future ranking/prominence layer should resolve — for now, existence is unconditional and quality is left entirely to ordering, per the decision above.
