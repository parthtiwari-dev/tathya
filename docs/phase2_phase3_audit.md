# Phase 2 and Phase 3 Audit

Last updated: 20 July 2026.

## Current Status

Phase 2 is functionally implemented as a private pipeline:

- Seed-based entity matching exists.
- Near-duplicate review exists.
- Semantic embeddings and pgvector search exist.
- Candidate clustering exists.
- Significance scoring exists and avoids political judgment.

Phase 3 is implemented as private, source-bound draft generation:

- Extractive case-file drafts exist.
- Draft topics, events, claims, and verifiable facts can be persisted.
- Gemini structured JSON generation is scaffolded as a private command.
- Manual audit export exists.

This is not public-launch complete. The roadmap requires manual audit before Phase 4.

## Design Decisions

- Vector database: Supabase Postgres with `pgvector`, because Tathya already stores signals and snapshots there.
- Embedding model: `intfloat/multilingual-e5-base`, because it is 768-dimensional and multilingual, matching the existing `signals.embedding vector(768)` column and future Hindi/regional needs.
- Retrieval style: evidence retrieval, not chatbot RAG. The system retrieves source rows/spans, then assembles structured case-file data.
- Reranking: not added yet. Current ranking is vector similarity plus source/date/type logic. Add reranking only if audit shows weak retrieval quality.
- Gemini: used only for private structured JSON drafts, never as a source of facts. Extractive rows remain the truth layer.
- Manual audit: mandatory before public frontend or public case-file launch.

## Known Flaws

- Entity matching is still a seed list, not full Wikidata-backed resolution.
- Topic clustering can still over-bucket broad people/entities such as Narendra Modi.
- Promotable status is strict: topics need both official and non-official sources. This is correct for launch-quality case files, but it means media-only topics remain draft-only.
- Old rows ingested before text cleaning may still contain HTML entities or markup. Future rows and future drafts are cleaner.
- RBI is an official/regulatory source, not a full Union Government ministry source. PIB/Parliament remain unresolved.
- Gemini generation is scaffolded but not validated against real output yet.

## Completion Gate Before Phase 4

- Run embeddings for all recent signals.
- Run semantic search spot checks for at least 5 topics.
- Persist case-file drafts.
- Export 30-50 claims/events/facts.
- Manually compare every exported row against the source URL/snapshot.
- Record the observed error rate.
- Do not launch publicly until the error rate is acceptable.
