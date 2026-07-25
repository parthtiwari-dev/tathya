Before I tell you exactly how to do this, I need to check one thing: whether `db/schema.sql` is a current, up-to-date snapshot (including everything migrations 001–008 added) or just the original baseline that the migrations layered on top of. That completely changes what "run the three db files, skip migrations" would actually leave you with. Let me check.`db/schema.sql` is actually a fully current, rolled-up schema — it already contains everything migrations 001–008 added (the `topic_entities`/`open_questions`/`contradictions` tables, `topics.slug`, `duplicate_of_signal_id`, `embedding vector(768)`, and critically the **corrected** `upsert_topic_cluster` with `p_promotable`). That's good news — it means your plan works cleanly. Let me quickly check the two seed files too, then give you the exact steps.Good news: since `schema.sql` already includes everything from migrations 001–008 (including the corrected `upsert_topic_cluster`), your plan is actually the cleanest possible path — a full wipe + fresh `schema.sql` + seeds will also fix the RPC 404 from last time, as a side effect. Here's exactly how to do it.

## Step 1 — Wipe everything (run in Supabase SQL Editor)

Paste and run this first — it drops every table, function, and type `schema.sql` creates, so the fresh file has a truly clean slate to build on:

```sql
-- ============================================================
-- SAFE TEARDOWN SCRIPT
-- Drops all overloaded functions by name, then tables + enums
-- ============================================================

-- Step 1: Drop all overloads of every function by name
do $$
declare
  r record;
  func_names text[] := array[
    'match_similar_signals',
    'store_signal_embedding',
    'upsert_topic_relation',
    'append_topic_fact',
    'append_topic_claim',
    'append_topic_event',
    'upsert_topic_cluster',
    'mark_signal_duplicate',
    'source_activation_summary',
    'set_source_enabled',
    'recent_source_counts',
    'record_source_run',
    'record_signal_snapshot',
    'reject_snapshot_mutation'
  ];
  fname text;
begin
  foreach fname in array func_names loop
    for r in
      select oid::regprocedure as sig
      from pg_proc
      where proname = fname
    loop
      execute 'drop function if exists ' || r.sig || ' cascade';
      raise notice 'Dropped function: %', r.sig;
    end loop;
  end loop;
end $$;


-- Step 2: Drop tables (cascade clears FKs/indexes/triggers)
drop table if exists contradictions cascade;
drop table if exists open_questions cascade;
drop table if exists topic_entities cascade;
drop table if exists source_run_metrics cascade;
drop table if exists corrections cascade;
drop table if exists topic_relations cascade;
drop table if exists verifiable_facts cascade;
drop table if exists claims cascade;
drop table if exists events cascade;
drop table if exists topic_signals cascade;
drop table if exists topics cascade;
drop table if exists entities cascade;
drop table if exists snapshots cascade;
drop table if exists signals cascade;
drop table if exists sources cascade;


-- Step 3: Drop enum types
drop type if exists correction_status;
drop type if exists relation_type;
drop type if exists claim_source_type;
drop type if exists topic_status;
drop type if exists trust_category;
drop type if exists source_type;
```

This only touches `public` schema objects — it doesn't touch Supabase's `auth`/`storage` schemas or any role grants, so it's safe and won't break your project-level permissions.

## Step 2 — Rebuild, in this exact order

1. Run the **entire contents** of `db/schema.sql` — recreates every type, table, index, and function fresh (already-current, includes the 008 fix).
2. Run the **entire contents** of `db/seed_sources.sql` — repopulates `sources` (PIB/RBI/Indian Express/Hindustan Times enabled, rest disabled, matching `shared/config.py`).
3. Run the **entire contents** of `db/seed_entities_core.sql` — repopulates the ministry/person/scheme entity spine.

No migrations to run — you're correct that `schema.sql` supersedes them for a fresh build.

## Step 3 — Reload PostgREST's schema cache

Since you just did major DDL (drop + recreate), force Supabase's API layer to see it: Dashboard → **Database → API → Reload schema**, or run `NOTIFY pgrst, 'reload schema';` in the SQL editor. Supabase usually does this automatically, but do it explicitly this time so you're not chasing a phantom 404 again.

## Step 4 — Trigger the 4 workflows, in this order, via GitHub → Actions tab → "Run workflow"

All four already have `workflow_dispatch` enabled, so you can fire them manually without waiting for cron:

1. **`ingest.yml`** first — pulls signals into the now-empty `signals`/`snapshots` tables.
2. **`embed.yml`** next — embeds whatever `ingest.yml` just landed.
3. **`case-file.yml`** next — clusters, scores, and persists topics (this is the one that was 404ing — should go green now).
4. **`lifecycle.yml`** last — will almost certainly do *nothing* on a brand-new dataset (nothing is 60 days stale yet). That's correct, not broken.

## What to actually expect, so you can tell "working" from "broken"

- `ingest.yml` should now succeed cleanly across all 4 enabled sources (PIB included, assuming the header fix worked — this is also your first real test of that).
- `case-file.yml` runs `--promotable-only`, which needs a cluster with **3+ signals, 2+ distinct sources, and both an official and a non-official source** on the *same* real-world topic before anything goes public. On one single ingest cycle from a cold, empty database, it's entirely possible **zero topics go Live** yet — that's the significance gate working as designed, not a failure. You may need 2–3 ingest cycles before enough signals accumulate around the same story for a cluster to actually qualify.
- Even once something does persist, remember Section 7.2's still-open gap: it'll show up with a raw cluster-key title (e.g. "Reserve Bank of India") and a robotic summary line, not a narrative headline — because Gemini-grounded generation still isn't wired into `case_file_persist.py`. Seeing that is expected right now, not a new bug.
- Check the frontend after `case-file.yml` completes — since `lib/api.ts` fetches with `cache: "no-store"`, it should reflect the new DB state immediately, no redeploy needed.

Want me to stay on standby and help you read the actual run logs/output once you've done this, so we can tell together what's real signal vs. expected empty-state behavior?