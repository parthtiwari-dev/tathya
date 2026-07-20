# Tathya Roadmap Execution Plan

Last updated: 20 July 2026.

This document is the single working plan from the current backend state to Phase 6 completion. The canonical product vision remains `docs/tathya_roadmap.md`; this file translates that roadmap into the exact implementation sequence, current progress, remaining gaps, verification commands, and engineering choices.

The core principle is unchanged:

> Tathya configures sources, not stories. It records sourced claims, events, facts, and corrections without verdicts, bias scores, or manual topic selection.

If a future implementation choice conflicts with this principle, the implementation is wrong.

---

## 1. Current State Summary

Tathya is no longer just a scaffold. The backend has a working end-to-end private pipeline:

```text
configured sources
  -> ingestion watchers
  -> immutable snapshots
  -> Supabase signals
  -> duplicate handling
  -> embeddings
  -> clustering/significance
  -> case-file draft rows
  -> FastAPI read endpoints
```

The latest local/API proof was:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/topics?limit=5"
```

That returned persisted Supabase topics, which proves this path is working:

```text
Supabase topics/events/claims/facts -> FastAPI -> local client
```

This does not mean public launch is ready. It means the private backend is mature enough to begin the frontend while simultaneously closing the audit/source-quality gaps.

---

## 2. What Is Already Implemented

### 2.1 Repository and foundation

Implemented:

- AGPL-3.0 license.
- Python package structure.
- Supabase schema.
- Source seed SQL.
- Core entity seed SQL.
- Mission/ethics document.
- Roadmap and phase audit docs.
- GitHub Actions ingestion workflow.
- `.env`-driven local/Supabase/Gemini/Telegram configuration.

Important files:

- `LICENSE`
- `pyproject.toml`
- `README.md`
- `docs/tathya_roadmap.md`
- `docs/mission_ethics.md`
- `db/schema.sql`
- `db/seed_sources.sql`
- `db/seed_entities_core.sql`
- `.github/workflows/ingest.yml`

### 2.2 Database

Implemented tables include:

- `sources`
- `signals`
- `snapshots`
- `entities`
- `topics`
- `topic_signals`
- `events`
- `claims`
- `verifiable_facts`
- `topic_relations`
- `corrections`
- `source_run_metrics`

Implemented RPC/migration capabilities include:

- Atomic signal + immutable snapshot write.
- Source-run metric recording.
- Source activation/deactivation support.
- Duplicate marking.
- Topic/case-file draft persistence.
- Embedding storage.
- pgvector similarity search.
- Topic relation persistence.

Current migration list:

- `001_source_activation.sql`
- `002_official_website_sources.sql`
- `003_mark_signal_duplicate.sql`
- `004_case_file_persistence.sql`
- `005_signal_embeddings.sql`
- `006_topic_relations_api.sql`

### 2.3 Ingestion

Implemented:

- RSS watcher.
- YouTube watcher.
- PIB scraper attempt.
- Parliament scraper attempt.
- Official website adapter.
- Dispatcher.
- Source audit command.
- One-shot source activation command.
- Scheduler.
- Snapshotter.
- Text cleaner.
- Health check.
- Telegram alert support.

Currently validated/enabled sources are conservative:

- `rbi-press-releases`
- `indian-express-india`
- `hindustan-times-india`

Known source issues:

- PIB currently hits 403.
- PMIndia official website currently hits 403.
- Income Tax press releases currently hit 403.
- Parliament pages need a better structured endpoint solution.
- PMO YouTube is currently title-only when transcripts are unavailable.
- RSS-heavy ingestion is useful but not sufficient for roadmap-quality official coverage.

### 2.4 Phase 2 processing

Implemented:

- Entity matching.
- Near-duplicate scan.
- Embedding generation.
- pgvector semantic search.
- Candidate topic clustering.
- Significance scoring.
- Topic report CLI.

Current design:

- Vector DB: Supabase Postgres with `pgvector`.
- Embedding model: `intfloat/multilingual-e5-base`.
- Embedding dimension: 768.
- Retrieval style: evidence retrieval, not chatbot RAG.
- Reranking: not implemented yet; should be added only if audit/search quality demands it.

Important commands:

```powershell
python -m pipeline.embed_signals --limit 300 --batch-size 16
python -m pipeline.semantic_search "RBI monetary penalty" --limit 10
python -m pipeline.topic_report --signals 300 --topics 10
python -m pipeline.duplicate_scan --signals 300 --threshold 0.82 --limit 20
```

### 2.5 Phase 3 generation

Implemented:

- Extractive case-file draft builder.
- Roadmap-named summary builder.
- Claims ledger builder.
- Timeline builder.
- Relations builder.
- Fact verifier/critique scaffold.
- Gemini structured JSON generation.
- Case-file persistence.
- Manual audit export.

Important files:

- `pipeline/generation/case_file_builder.py`
- `pipeline/generation/summarizer.py`
- `pipeline/generation/claims_ledger_builder.py`
- `pipeline/generation/timeline_builder.py`
- `pipeline/generation/relations_builder.py`
- `pipeline/generation/fact_verifier.py`
- `pipeline/generation/gemini_case_file.py`
- `pipeline/case_file_report.py`
- `pipeline/case_file_persist.py`
- `pipeline/gemini_case_file_report.py`
- `pipeline/audit_export.py`

Important commands:

```powershell
python -m pipeline.case_file_report --signals 300 --topics 5
python -m pipeline.case_file_persist --signals 300 --topics 5
python -m pipeline.gemini_case_file_report --signals 300 --topics 3
python -m pipeline.audit_export --target claims --limit 50 > audit_claims.csv
python -m pipeline.audit_export --target events --limit 50 > audit_events.csv
python -m pipeline.audit_export --target facts --limit 50 > audit_facts.csv
```

### 2.6 API

Implemented:

- FastAPI app.
- Health endpoint.
- Topic list endpoint.
- Topic detail endpoint.
- Semantic signal search endpoint.
- Correction report endpoint.

Current endpoints:

```text
GET  /health
GET  /topics
GET  /topics/{topic_id}
GET  /signals/search?q=...
POST /corrections
```

Current API status:

- Good enough to begin frontend scaffolding.
- Not yet complete for public v1.
- Needs better response models, frontend-oriented payloads, CORS, pagination, history, source-health endpoints, public-safe deployment configuration, and correction review/history support.

### 2.7 Tests

Current test state after the latest pass:

```text
62 passed
```

This matters. Keep this number moving upward, not downward. Every future phase should add tests for new behavior before relying on it.

---

## 3. What Is Not Done Yet

This is the uncomfortable but useful list. If these are not closed, Tathya is not roadmap-complete.

### 3.1 External/product obligations

Still required:

- Register and connect a domain.
- Make the GitHub repository public if it is not already public.
- Complete the one-time media/IT-law consult.
- Decide public snapshot display policy after legal advice.
- Decide acceptable Phase 3 audit error threshold.

The legal consult is not decorative. The roadmap explicitly says it is not optional because Tathya synthesizes source material through an LLM. That changes exposure compared with merely linking to articles.

### 3.2 Source breadth

Still required:

- Strong official coverage:
  - Parliament Q&A.
  - PIB or lawful alternate official press endpoint.
  - Gazette/eGazette.
  - Ministry-specific official release pages.
  - PMO official updates.
  - Official transcripts where available.
- More independent media only after quality inspection.
- Hindi/regional sources.
- Citizen/social sources later and carefully.

Current source quality is enough for private development, but not enough for the roadmap’s promise of broad civic coverage.

### 3.3 Entity spine

Still required:

- Full Wikidata-backed ministries.
- Current ministers.
- MPs.
- Major schemes.
- Laws.
- Common aliases.
- Actor categories that distinguish official, opposition, citizen/protester, journalist, institution.

Current entity matching is seed-based. That is fine for early validation, not sufficient for Phase 6 maturity.

### 3.4 Topic lifecycle

Still required:

- `activity_monitor.py`
- `status_manager.py`
- 60-day archive logic.
- Reopen logic when new signals arrive.
- Tests for Live -> Archived -> Live.
- Workflow schedule for lifecycle checks.

The roadmap’s Layer 6 is not implemented yet.

### 3.5 Public frontend

Still required:

- `apps/web` Next.js app.
- Main feed page.
- Case file page.
- Timeline component.
- Claims Ledger component.
- Verifiable Facts panel.
- Related topics section.
- Source/history section.
- Search page.
- About page from mission/ethics doc.
- Report extraction issue UI.
- Theme toggle.
- Intro animation.
- Deployment to Vercel or equivalent.

### 3.6 Public API completeness

Still required:

- Stable response schemas.
- CORS.
- Pagination.
- Topic history endpoint.
- Claims/events/facts endpoints.
- Source explorer endpoints.
- Source health endpoints.
- Correction review/history endpoints.
- Snapshot/evidence endpoint or safe evidence display policy.
- Read-only public mode.
- Avoid exposing service-role credentials outside server environments.

### 3.7 Manual audit

Still required:

- Audit 30-50 AI/extractive claims/events/facts.
- Check each row against the source URL and snapshot.
- Record error rate.
- Fix extraction defects.
- Repeat until the error rate is low enough to launch.

The roadmap says do not proceed to public Phase 4 launch before this. Build frontend privately if needed, but do not publicly launch.

---

## 4. Roadmap Compliance Matrix

### Phase 0 — Foundation

Status: mostly complete, with external gates still open.

Done:

- AGPL license.
- Repository structure.
- Supabase schema.
- Starter source config.
- Gemini key support.
- GitHub Actions secret path.
- Mission/ethics doc.
- Seed entity base.

Left:

- Domain.
- Confirm public repo status.
- Full Wikidata entity seed.
- Legal consult.

Completion criteria:

- Domain exists.
- Repo is public under AGPL-3.0.
- Supabase schema and migrations are reproducible from scratch.
- `db/seed_sources.sql` and `db/seed_entities_core.sql` run cleanly.
- Legal advice is documented privately and reflected in public snapshot policy.

### Phase 1 — Raw Ingestion Pipeline

Status: functionally implemented, source breadth incomplete.

Done:

- RSS ingestion.
- YouTube ingestion.
- PIB/parliament adapter attempts.
- Official website adapter.
- Snapshotting.
- Source metrics.
- Telegram alerting.
- GitHub Actions scheduled ingest.
- Supabase contains real signals/snapshots.

Left:

- Official-source reliability.
- Parliament structured endpoint.
- PIB/PMIndia/Income Tax 403 solution.
- More source activation cycles.
- Health workflow polish.

Completion criteria:

- Several reliable official and independent sources enabled.
- Hundreds/thousands of clean real signals.
- Every signal has a snapshot.
- Repeated ingestion does not create duplicate source URL rows.
- Health alerts work.
- At least 10 manually inspected rows per enabled source.

### Phase 2 — Clustering & Significance Engine

Status: implemented, quality iteration still needed.

Done:

- Entity matching.
- Embeddings.
- Clustering.
- Duplicate review.
- Significance scoring.
- Semantic search.

Left:

- Full `ner_extractor.py` or stronger entity pipeline.
- Better semantic clustering beyond title/entity bucketing.
- Optional reranking if audit shows poor retrieval.
- Automated duplicate application for high-confidence duplicates, with safety.
- More official/nonofficial source balance so topics can become `live`.

Completion criteria:

- System identifies 5-10 real current topics without manual input.
- Clusters are not polluted by unrelated feed noise.
- Independent source count excludes duplicates.
- Topics that lack official/nonofficial diversity remain draft/private.

### Phase 3 — Case File Generation

Status: machinery implemented; launch gate incomplete.

Done:

- Extractive draft generation.
- RAG-grounded Gemini scaffold.
- Claims Ledger.
- Structured timeline.
- Relation detection.
- Fact verification scaffold.
- Persistence.
- Audit export.

Left:

- Real manual audit.
- Improve extraction based on audit findings.
- Strengthen fact verification against official documents.
- Better relation labels if needed.
- Decide whether Gemini output is reliable enough or whether extractive-only v1 is safer.

Completion criteria:

- JSON/object case files exist per promoted topic.
- Claims/events/facts have source references.
- Claims have `quoted_span`.
- Events are structured rows, not prose.
- Facts come from official/primary rows.
- Manual audit finds acceptable error rate.

### Phase 4 — Public Frontend Launch

Status: not started except API v0.

Done:

- API v0 exists.
- Correction POST endpoint exists.
- Supabase data shape exists.

Left:

- Next.js frontend.
- API v1.
- Search UI.
- History UI.
- Correction UI.
- Deployment.
- Launch gate.

Completion criteria:

- Public v1 live.
- No login.
- No social engagement mechanics.
- Main feed renders live topics.
- Case file page renders sourced claims/events/facts.
- Every claim links to source/evidence.
- Public launch occurs only after Phase 3 audit.

### Phase 5 — Lifecycle Automation + X Coverage

Status: not implemented.

Left:

- `pipeline/lifecycle/activity_monitor.py`
- `pipeline/lifecycle/status_manager.py`
- Lifecycle SQL/RPC methods.
- GitHub Actions lifecycle workflow.
- Archive after 60 days of inactivity.
- Reopen same topic when a new signal arrives.
- X coverage strategy.

Important caution:

X is not a free, reliable ingestion source anymore. The roadmap’s honest approach should be followed:

1. Capture many important X statements indirectly through journalism/RSS.
2. If direct X monitoring is added, keep it small and accept fragility.
3. Do not make public reliability claims around unofficial scraping.

Completion criteria:

- Topic transitions Live -> Archived -> Live are tested.
- Reopening uses the same topic ID.
- No duplicate page is created for revived topics.

### Phase 6 — Hardening & Reach

Status: not implemented.

Left:

- Hindi-language generation.
- Hindi UI path.
- Telegram bot mirroring key updates.
- Automated backups.
- Mirror deployment consideration.
- Operational documentation.

Completion criteria:

- English and Hindi summaries/claims can be generated and audited.
- Telegram updates mirror public case-file changes.
- Supabase backup strategy is active.
- Basic resilience exists if one deployment is unavailable.

---

## 5. Target Backend Architecture From Here

The backend should evolve into six scheduled jobs plus one API service.

### 5.1 Job 1 — Ingestion

Purpose:

- Fetch enabled sources.
- Normalize signals.
- Store immutable snapshots.
- Record source-run metrics.
- Alert on failures/drop-offs.

Entry point:

```powershell
python -m pipeline.scheduler --persist
```

GitHub Actions:

```yaml
name: Ingest configured sources
schedule: every 6 hours
```

Future improvements:

- Split source classes into separate jobs if runtime grows.
- Add retry logic per source.
- Add source-specific failure classification.
- Store last successful fetch metadata.

### 5.2 Job 2 — Embeddings

Purpose:

- Generate embeddings for signals missing `embedding`.
- Store vectors in Supabase.
- Enable semantic search and future clustering.

Entry point:

```powershell
python -m pipeline.embed_signals --limit 500 --batch-size 16
```

GitHub Actions:

- Run after ingestion.
- Install `.[embeddings]`.
- Cache model downloads if possible.

Concern:

`intfloat/multilingual-e5-base` is large. GitHub Actions can run it, but cold starts may be slow. If this becomes painful, move embedding generation to:

- a persistent API worker,
- a scheduled Render/Railway job,
- or a smaller model only if quality remains acceptable.

### 5.3 Job 3 — Duplicate scan

Purpose:

- Prevent wire-copy from inflating independent source count.
- Keep duplicate rows stored but non-canonical.

Entry point:

```powershell
python -m pipeline.duplicate_scan --signals 500 --threshold 0.82 --limit 50
```

Future improvement:

- Keep manual review by default.
- Add an `--auto-apply-threshold` only for very high confidence, e.g. 0.94+, and only after testing.

### 5.4 Job 4 — Topic clustering and promotion

Purpose:

- Cluster recent canonical signals.
- Score significance.
- Promote eligible clusters from `raw_cluster` to `live`.

Current entry points:

```powershell
python -m pipeline.topic_report --signals 300 --topics 10
python -m pipeline.case_file_persist --signals 300 --topics 5
```

Needed:

- `pipeline/promotion.py` or equivalent.
- SQL/RPC to update topic status.
- Explicit thresholds in `shared/config.py`.

Promotion should require:

- canonical source count,
- velocity,
- at least one official source,
- at least one non-official source,
- no duplicate inflation.

It must not include:

- manual story importance,
- political side,
- subjective severity,
- bias or truth judgment.

### 5.5 Job 5 — Case-file generation

Purpose:

- Build/update summaries, claims, events, facts, relations.
- Persist rows append-only.

Current entry point:

```powershell
python -m pipeline.case_file_persist --signals 300 --topics 5
```

Future design:

- For every live/promotable cluster:
  1. Retrieve canonical signals.
  2. Retrieve snapshots/evidence.
  3. Build extractive draft.
  4. Optionally run Gemini single-pass for summary/organization.
  5. Run fact critique only for high-stakes fact rows.
  6. Persist append-only rows.
  7. Trigger frontend revalidation.

Gemini should never be treated as a source. It may only transform evidence already retrieved.

### 5.6 Job 6 — Lifecycle

Purpose:

- Archive inactive topics.
- Reopen archived topics when new signals arrive.

Needed files:

```text
pipeline/lifecycle/activity_monitor.py
pipeline/lifecycle/status_manager.py
.github/workflows/lifecycle.yml
```

Rules:

- If `topics.status = live` and no new linked signal for 60 days: set `archived`.
- If an archived topic gets a new matching signal: set `live`.
- Reopened topics keep the same topic ID.
- History remains visible.

### 5.7 API service

Purpose:

- Serve frontend data.
- Accept correction reports.
- Provide semantic search.
- Provide source/history/evidence views.

Current:

```text
GET  /health
GET  /topics
GET  /topics/{topic_id}
GET  /signals/search
POST /corrections
```

Target API v1:

```text
GET  /health
GET  /topics
GET  /topics/{topic_id}
GET  /topics/{topic_id}/claims
GET  /topics/{topic_id}/events
GET  /topics/{topic_id}/facts
GET  /topics/{topic_id}/relations
GET  /topics/{topic_id}/history
GET  /topics/{topic_id}/sources
GET  /sources
GET  /sources/{source_key}
GET  /sources/{source_key}/signals
GET  /source-runs
GET  /signals/search
POST /corrections
GET  /corrections/public
```

Target API rules:

- Use stable Pydantic response models.
- Keep service-role key server-side only.
- Add CORS for frontend domain.
- Add pagination.
- Add deterministic ordering.
- Return citations/evidence URLs with every claim/event/fact.
- Never expose private environment values.

---

## 6. Target Generation Design

Tathya’s generation is not a chatbot. It is a structured evidence compiler.

### 6.1 Retrieval

The retrieval layer should gather:

- Canonical signals linked to the topic.
- Source metadata.
- Snapshots.
- Existing claims/events/facts.
- Official/primary-source rows for fact verification.
- Semantically similar signals for context expansion.

Retrieval should avoid:

- web search at generation time,
- model memory,
- unsupported claims,
- generalized political commentary.

### 6.2 Summary

The summary should:

- be neutral,
- be one paragraph,
- mention what the cluster is about,
- avoid verdicts,
- avoid loaded adjectives,
- cite or be traceable to supporting evidence,
- be regenerated when the case file grows.

Recommended v1 approach:

- Keep extractive deterministic summaries as fallback.
- Use Gemini only after manual audit demonstrates acceptable quality.
- Store `summary_generated_at`.
- Keep prior rows intact; only summary is superseded.

### 6.3 Claims Ledger

The Claims Ledger should group claims by source type:

- Government says.
- Independent media reports.
- Citizens/protesters say.
- Opposition says.

Every claim must have:

- `claim_text`
- `source_type`
- `source_signal_id`
- `quoted_span`
- source URL
- snapshot/evidence path or reference

Never include:

- truth labels,
- bias labels,
- system opinion,
- unsupported synthesis.

### 6.4 Timeline

Timeline rows must be structured:

- `event_date`
- `description`
- `source_signal_ids`

The timeline is not prose. It is queryable data.

Audit checks:

- Is the date supported by the source?
- Is the description supported by the quote/body?
- Is the event distinct from prior rows?

### 6.5 Verifiable Facts

Facts are special. They should come from primary/official sources:

- Parliament Q&A.
- PIB.
- Gazette.
- Official datasets.
- Regulator releases such as RBI, where relevant.

Fact verification should use two passes:

1. Generate/extract candidate facts from official rows.
2. Critique each candidate against the primary quote/source.

Only facts passing critique should appear publicly.

### 6.6 Relations

Relations should link topics via:

- shared entities,
- shared policy area,
- direct reference,
- escalation from one case into another,
- court/policy references.

Current relation builder is deterministic and conservative. Future relation labeling may use Gemini, but only to label already-detected relation candidates, not invent links freely.

---

## 7. Target Source and Ingestion Strategy

Source quality is the single most important next backend problem.

### 7.1 Source activation workflow

Every source must follow this loop:

```text
1. Add disabled in shared/config.py.
2. Seed it into Supabase.
3. Audit locally.
4. Persist once with source_activation.
5. Inspect Supabase rows manually.
6. Check timestamps, canonical URLs, text quality, snapshots.
7. Enable locally.
8. Run scheduler --persist.
9. Confirm no duplicate explosion.
10. Only then allow GitHub Actions to poll it regularly.
```

Commands:

```powershell
python -m pipeline.source_audit --list
python -m pipeline.source_audit --source SOURCE_KEY --limit 10
python -m pipeline.source_activation --source SOURCE_KEY --limit 50
python -m pipeline.scheduler --persist
```

### 7.2 Official source priority

Priority order:

1. Parliament Q&A.
2. PIB or lawful alternate PIB feed/path.
3. Gazette/eGazette.
4. Ministry-level releases.
5. PMO official updates.
6. Official YouTube transcripts.
7. Regulator datasets/releases.

Why official sources matter:

- They unlock the Verifiable Facts panel.
- They let significance scoring require cross-institutional confirmation.
- They prevent the product from becoming a media-summary site.

### 7.3 Media source priority

Media sources are useful, but they should be added carefully.

Good source traits:

- clean RSS/Atom,
- stable canonical URLs,
- useful summaries/content,
- clear timestamps,
- low duplicate/wire-copy noise,
- reasonable terms.

Avoid adding many sources at once. The correct pace is slow:

```text
one source -> audit -> inspect -> enable -> monitor -> repeat
```

### 7.4 YouTube source strategy

YouTube sources are useful only when transcripts are available.

For channels:

- keep title-only rows as low-information signals,
- prefer channels with captions/transcripts,
- store transcript when available,
- do not overcount title-only videos as rich evidence.

Needed improvement:

- Add transcript availability metrics.
- Add source health warning when a YouTube source becomes title-only for too long.

### 7.5 Social/X strategy

Do not make X central to v1.

X is expensive/unreliable for official API access and fragile via unofficial scraping. The roadmap’s honest plan should stand:

- Let RSS/news capture many quoted posts indirectly.
- If direct X ingestion is added, keep it low-volume and explicit.
- Treat direct X coverage as fragile.
- Do not block v1 on X.

---

## 8. Target Frontend Design

The frontend should feel like an archive/ledger, not a news engagement product.

### 8.1 App structure

Target:

```text
apps/web/
  app/
    page.tsx
    topic/[slug]/page.tsx
    search/page.tsx
    source/[sourceKey]/page.tsx
    about/page.tsx
    layout.tsx
  components/
    IntroAnimation.tsx
    FeedItem.tsx
    ClaimsLedger.tsx
    Timeline.tsx
    VerifiableFactsPanel.tsx
    RelatedTopics.tsx
    TopicHistory.tsx
    CorrectionReportButton.tsx
    FilterSidebar.tsx
    ThemeToggle.tsx
```

### 8.2 Main feed

The main feed should be a vertical chronological ledger.

Each row:

- topic title,
- neutral one-line summary,
- source-count badge,
- source-type breakdown,
- entity tags,
- status: Live or Archived,
- last updated time.

Do not use:

- infinite engagement bait,
- likes,
- comment counts,
- “trending” labels unless they are purely formulaic and documented,
- partisan categories.

### 8.3 Case file page

The case file page must follow this order:

```text
Title
Neutral summary
Timeline
Claims Ledger
Verifiable Facts
Related Topics
Source/Evidence list
History
Corrections
```

The Claims Ledger must visually separate:

- Government says.
- Independent media reports.
- Citizens/protesters say.
- Opposition says.

The Verifiable Facts panel must be visually distinct. A fact is not just another claim.

### 8.4 History view

History is essential because the roadmap promises append-only accountability.

History should show:

- when claims were added,
- when events were added,
- when facts were added,
- when corrections were reported,
- when corrections were reviewed/fixed,
- when topic status changed.

If history is missing, “we never silently rewrite the past” is only a slogan.

### 8.5 Search

Search should use pgvector semantic search, not only keyword search.

Initial search modes:

- topic search,
- signal/evidence search,
- source search.

Later:

- filters by source type,
- date range,
- official/media/citizen,
- live/archived.

### 8.6 Intro animation

Keep it lightweight:

- SVG/CSS only.
- One or two mission lines.
- Store seen flag in `localStorage`.
- No video.
- No login wall.

---

## 9. GitHub Actions Target Workflow

Current workflow:

```text
.github/workflows/ingest.yml
  every 6 hours
  install package
  run pipeline.scheduler --persist
```

This is good for Phase 1, but Phase 4-6 need more.

### 9.1 Ingest workflow

Purpose:

- Fetch enabled sources.
- Persist signals/snapshots.
- Record metrics.
- Telegram alert on abnormal drop.

Keep:

```yaml
schedule:
  - cron: "17 */6 * * *"
```

Future:

- Add dependency install caching.
- Consider per-source-class matrix only if runtime grows.

### 9.2 Embedding workflow

Purpose:

- Embed new signals after ingestion.

Suggested schedule:

```text
every 6 hours, offset after ingest
```

Command:

```powershell
python -m pipeline.embed_signals --limit 500 --batch-size 16
```

Secrets:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

Dependency:

- install `.[embeddings]`

### 9.3 Case-file workflow

Purpose:

- Cluster recent signals.
- Persist/update case-file rows.
- Persist relations.

Command:

```powershell
python -m pipeline.case_file_persist --signals 500 --topics 10 --promotable-only
```

Before public launch, keep private/non-promotable runs manual. After launch, automated public persistence should use `--promotable-only`.

### 9.4 Health workflow

Purpose:

- Detect source failures separately from ingestion.
- Send Telegram alerts.

Command:

```powershell
python -m pipeline.monitoring.health_check
```

If health is embedded in scheduler, this can stay combined. If failures get noisy, split it.

### 9.5 Lifecycle workflow

Purpose:

- Archive/reopen topics.

Future command:

```powershell
python -m pipeline.lifecycle.status_manager
```

Suggested schedule:

```text
daily
```

### 9.6 Frontend deploy/revalidation

Frontend deployment should happen through Vercel or equivalent.

Case-file updates should eventually trigger:

- Next.js on-demand revalidation,
- or a simple cache invalidation endpoint,
- or ISR with short revalidate windows.

Do not overbuild this before the frontend exists. Start with simple SSR/server-fetching, then optimize.

---

## 10. API v1 Design

Current API v0 is intentionally thin. API v1 should become the frontend contract.

### 10.1 Required endpoints

```text
GET /health
GET /topics
GET /topics/{topic_id}
GET /topics/{topic_id}/claims
GET /topics/{topic_id}/events
GET /topics/{topic_id}/facts
GET /topics/{topic_id}/relations
GET /topics/{topic_id}/history
GET /topics/{topic_id}/sources
GET /sources
GET /sources/{source_key}
GET /sources/{source_key}/signals
GET /source-runs
GET /signals/search
POST /corrections
GET /corrections/public
```

### 10.2 Response requirements

Every public response should be:

- deterministic,
- paginated where list-like,
- typed with Pydantic models,
- stable enough for frontend development,
- citation-rich,
- free of service-role or internal-only values.

Topic detail should ideally return:

```json
{
  "topic": {},
  "summary": {},
  "claims": [],
  "events": [],
  "facts": [],
  "relations": [],
  "sources": [],
  "history": [],
  "corrections": []
}
```

### 10.3 Security requirements

- Never expose `SUPABASE_SERVICE_ROLE_KEY` to the browser.
- Frontend calls FastAPI or a safe public Supabase anon view.
- Add CORS only for known frontend domains in production.
- Validate correction input.
- Rate limit correction reports before public launch.

---

## 11. Deployment Plan

### 11.1 Local development

Backend:

```powershell
python -m pip install -e ".[api,embeddings,generation]"
python -m uvicorn api.main:app --reload
```

Frontend:

```powershell
cd apps/web
npm install
npm run dev
```

Database:

- Supabase hosted project.
- SQL migrations manually run for now.
- Later, add a migration runner or Supabase CLI.

### 11.2 Production target

Suggested v1:

- Supabase: database/storage.
- GitHub Actions: ingestion/processing cron.
- Render/Railway/Fly: FastAPI.
- Vercel: Next.js frontend.
- Domain: connected to frontend.
- Telegram: operator alerts and later public mirror.

### 11.3 Required production environment variables

API/cron:

```text
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
GEMINI_API_KEY
GEMINI_MODEL
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Frontend:

```text
NEXT_PUBLIC_TATHYA_API_URL
```

Do not put service-role keys in frontend variables.

---

## 12. Phase 4 Implementation Plan

Phase 4 goal:

```text
public v1 frontend, no login, every claim traceable, no public launch before audit
```

### 12.1 Build order

1. Upgrade API v0 to API v1 response models.
2. Scaffold `apps/web` Next.js.
3. Build homepage feed.
4. Build topic detail page.
5. Build Claims Ledger.
6. Build Timeline.
7. Build Verifiable Facts panel.
8. Build Related Topics.
9. Build History.
10. Build correction report UI.
11. Build semantic search UI.
12. Add About page using mission/ethics doc.
13. Deploy private/staging.
14. Complete manual audit.
15. Public launch only if audit passes.

### 12.2 Phase 4 verification

Run:

```powershell
python -m pytest -q
python -m pipeline.scheduler --persist
python -m pipeline.embed_signals --limit 300 --batch-size 16
python -m pipeline.case_file_persist --signals 300 --topics 5
python -m uvicorn api.main:app --reload
```

Then verify:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/health"
Invoke-RestMethod "http://127.0.0.1:8000/topics?limit=5"
```

Frontend checks:

- Homepage loads topics.
- Topic page loads claims/events/facts.
- Search returns semantically relevant rows.
- Correction form creates a row.
- No unsupported claim appears without citation.

---

## 13. Phase 5 Implementation Plan

Phase 5 goal:

```text
topic lifecycle automation and realistic X coverage
```

### 13.1 Lifecycle files

Create:

```text
pipeline/lifecycle/__init__.py
pipeline/lifecycle/activity_monitor.py
pipeline/lifecycle/status_manager.py
.github/workflows/lifecycle.yml
```

### 13.2 Lifecycle logic

Status transitions:

```text
raw_cluster -> live
live -> archived
archived -> live
```

Rules:

- `raw_cluster -> live` when significance threshold passes.
- `live -> archived` when no linked signal exists for 60 days.
- `archived -> live` when a new signal links to the topic.

Tests:

- active topic stays live,
- dormant topic archives,
- archived topic reopens,
- reopened topic keeps same ID,
- no duplicate topic is created.

### 13.3 X coverage

Implement only after core v1 is stable.

Options:

1. Official API if budget allows.
2. Low-volume scraper for a tiny handle list.
3. Indirect capture through news RSS.

Recommended v1:

- Defer direct X unless absolutely necessary.
- Capture indirect X references through media.
- Add direct X only as explicitly fragile/non-guaranteed coverage.

---

## 14. Phase 6 Implementation Plan

Phase 6 goal:

```text
hardening, Hindi reach, Telegram mirror, resilience
```

### 14.1 Hindi generation

Add:

- Hindi summary field or table.
- Hindi claim rendering.
- Hindi UI path.
- Hindi audit samples.

Do not assume translation quality. Audit it.

Possible data model:

```text
topic_translations
  topic_id
  language
  summary
  generated_at

claim_translations
  claim_id
  language
  claim_text
  generated_at
```

Simpler v1.5:

- Generate Hindi summaries only first.
- Add claims later.

### 14.2 Telegram mirror

Telegram should mirror key updates, not replace the website.

Bot behavior:

- New live topic notification.
- Major topic update notification.
- Link back to case file.
- No political commentary.
- No engagement bait.

Needed:

- topic update detector,
- message renderer,
- Telegram send command,
- GitHub Actions integration.

### 14.3 Backups

Minimum:

- Supabase scheduled backups if available.
- Periodic export of schema and critical rows.
- Store audit CSVs.
- Store seed config in git.

Better:

- Nightly `pg_dump`.
- Archive snapshots/case files.
- Mirror deployment.

### 14.4 Mirror/resilience

Start simple:

- Keep code public.
- Keep migrations reproducible.
- Keep snapshots immutable.
- Keep exported case-file JSON possible.

Later:

- Secondary deployment.
- Static export of public case files.
- IPFS/archive only after legal review.

---

## 15. Manual Audit Procedure

This is the gate between private system and public product.

### 15.1 Generate audit files

Run:

```powershell
python -m pipeline.case_file_persist --signals 300 --topics 5
python -m pipeline.audit_export --target claims --limit 50 > audit_claims.csv
python -m pipeline.audit_export --target events --limit 50 > audit_events.csv
python -m pipeline.audit_export --target facts --limit 50 > audit_facts.csv
```

### 15.2 Audit columns to add manually

In the CSV/spreadsheet, add:

```text
audit_status
audit_issue_type
audit_notes
```

Suggested statuses:

```text
pass
minor_issue
major_issue
unclear
```

Suggested issue types:

```text
wrong_quote
wrong_date
wrong_source
misattribution
unsupported_summary
hallucination
duplicate
too_broad
bad_entity_match
```

### 15.3 Acceptable launch gate

Do not launch if there are:

- hallucinated claims,
- unsupported facts,
- recurring misattribution,
- systematic wrong dates,
- unclear source mapping.

Launch is acceptable only when:

- severe hallucinations are zero,
- misattribution is rare and fixed,
- every fact has primary evidence,
- every claim has a quoted span,
- every event has source signal IDs,
- you would be comfortable having your own name on the site.

---

## 16. Immediate Next Sprint

The next sprint should not add more random features. It should convert the working backend into a private end-to-end product.

Recommended order:

1. API v1 response models and endpoints.
2. Topic promotion/status manager.
3. Frontend scaffold.
4. Feed page.
5. Topic page.
6. Claims Ledger component.
7. Timeline component.
8. Verifiable Facts panel.
9. History/corrections UI.
10. Manual audit pass.
11. Official-source improvements.
12. Private staging deployment.

Do not do these yet:

- broad X ingestion,
- Instagram,
- state governments,
- user accounts,
- comments,
- monetization,
- public launch,
- generalized ontology,
- bias/truth scoring.

---

## 17. End-to-End Runbook

Use this to validate the full private backend.

### 17.1 Install

```powershell
python -m pip install -e ".[api,embeddings,generation]"
```

### 17.2 Test

```powershell
python -m pytest -q
```

### 17.3 Ingest

```powershell
python -m pipeline.scheduler
python -m pipeline.scheduler --persist
```

### 17.4 Embed

```powershell
python -m pipeline.embed_signals --limit 300 --batch-size 16
```

### 17.5 Search check

```powershell
python -m pipeline.semantic_search "RBI monetary penalty" --limit 10
python -m pipeline.semantic_search "Sonam Wangchuk Parliament march" --limit 10
```

### 17.6 Duplicate check

```powershell
python -m pipeline.duplicate_scan --signals 300 --threshold 0.82 --limit 20
```

Only use `--apply` after manually confirming candidate pairs.

### 17.7 Topic check

```powershell
python -m pipeline.topic_report --signals 300 --topics 10
```

### 17.8 Case-file check

```powershell
python -m pipeline.case_file_report --signals 300 --topics 5
python -m pipeline.case_file_persist --signals 300 --topics 5
```

### 17.9 Audit export

```powershell
python -m pipeline.audit_export --target claims --limit 50 > audit_claims.csv
python -m pipeline.audit_export --target events --limit 50 > audit_events.csv
python -m pipeline.audit_export --target facts --limit 50 > audit_facts.csv
```

### 17.10 API

```powershell
python -m uvicorn api.main:app --reload
```

Check:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/health"
Invoke-RestMethod "http://127.0.0.1:8000/topics?limit=5"
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

## 18. Definition of Done Through Phase 6

### Phase 4 done

- Frontend public v1 exists.
- API v1 serves it.
- Manual audit passed.
- Every public claim/event/fact is sourced.
- Correction reports work.
- History is visible.
- Search works.
- Domain connected.

### Phase 5 done

- Lifecycle automation exists.
- Dormant topics archive after 60 days.
- New signals reopen archived topics.
- Same topic ID is reused.
- X strategy is implemented or explicitly deferred with rationale.

### Phase 6 done

- Hindi summaries or Hindi case-file output exists and is audited.
- Telegram mirror sends key updates.
- Backups exist.
- Basic deployment resilience exists.
- Operational runbooks exist.

---

## 19. The Main Risks

### Risk 1 — Official sources remain blocked

Mitigation:

- Find alternate official endpoints.
- Use Gazette/data.gov.in/ministry pages.
- Treat RBI/regulators as official but not sufficient.
- Do not weaken significance thresholds just to make media-only topics live.

### Risk 2 — AI extraction errors

Mitigation:

- Keep extractive fallback.
- Require quoted spans.
- Audit 30-50 rows.
- Use Gemini only as transformer, never source.
- Use two-pass critique only for facts.

### Risk 3 — Scope creep

Mitigation:

- No comments/accounts/social features.
- No verdicts.
- No state coverage before Union v1.
- No generalized ontology.
- No manual topic curation.

### Risk 4 — Legal exposure

Mitigation:

- Complete legal consult.
- Keep source citations.
- Avoid overexposing private citizens.
- Decide snapshot display policy carefully.
- Make corrections mechanical and transparent.

### Risk 5 — GitHub Actions becomes too heavy

Mitigation:

- Split workflows.
- Cache dependencies/model downloads.
- Move embeddings/generation to a worker if needed.
- Keep ingestion fast and reliable.

---

## 20. Final Implementation North Star

The best version of Tathya is not the one with the most sources, the fanciest AI, or the slickest UI.

The best version is the one where:

- topics emerge automatically,
- claims are separated by who said them,
- facts are only what primary documents support,
- every row is traceable,
- every source disappearance is survivable,
- every correction is transparent,
- and no human quietly decides what deserves attention.

That is the roadmap. Every implementation step from here to Phase 6 should protect that shape.
