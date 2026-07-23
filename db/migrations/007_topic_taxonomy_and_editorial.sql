-- Adds what the frontend contract (apps/web/lib/types.ts) already expects
-- but the DB never had: topic slugs, entity slugs, a topic<->entity link
-- (for ministry + entityTags), and open_questions/contradictions tables.
-- Safe to run against an existing Phase 0-5 database.

alter table topics add column if not exists slug text;
alter table entities add column if not exists slug text;

-- Backfill slugs for any rows that predate this migration. New rows always
-- arrive with a slug already set (topics via upsert_topic_cluster's p_slug,
-- entities are seeded and app-patched lazily), so this only ever fires once.
update topics
set slug = lower(regexp_replace(regexp_replace(trim(title), '[^a-zA-Z0-9]+', '-', 'g'), '(^-|-$)', '', 'g'))
where slug is null;

update entities
set slug = lower(regexp_replace(regexp_replace(trim(name), '[^a-zA-Z0-9]+', '-', 'g'), '(^-|-$)', '', 'g'))
where slug is null;

create unique index if not exists topics_slug_idx on topics (slug) where slug is not null;
create unique index if not exists entities_slug_idx on entities (slug) where slug is not null;

-- Links a topic to the entities (ministries, people, schemes...) matched
-- against it, so the API can derive Topic.ministry/ministrySlug/entityTags
-- without re-running entity matching on every read.
create table if not exists topic_entities (
  topic_id uuid not null references topics(id) on delete cascade,
  entity_id uuid not null references entities(id),
  is_ministry boolean not null default false,
  primary key (topic_id, entity_id)
);
create index if not exists topic_entities_topic_idx on topic_entities (topic_id);

-- Structural, not semantic: a topic has an open question when its claims
-- lack an official (govt-sourced) claim. The extractive builder computes
-- this deterministically; nothing here is LLM-generated or fabricated.
create table if not exists open_questions (
  id uuid primary key default gen_random_uuid(),
  topic_id uuid not null references topics(id) on delete cascade,
  question text not null,
  related_claim_id uuid references claims(id),
  created_at timestamptz not null default now()
);
create index if not exists open_questions_topic_idx on open_questions (topic_id, created_at);

-- Two directly conflicting statements from the same named entity, each
-- pinned to its own source signal. Detection is not implemented by the
-- current extractive pipeline (it requires cross-signal semantic judgment);
-- this table exists so the API/frontend contract is complete and ready for
-- that generation step once it's built.
create table if not exists contradictions (
  id uuid primary key default gen_random_uuid(),
  topic_id uuid not null references topics(id) on delete cascade,
  entity_name text not null,
  statement_a_text text not null,
  statement_a_date date not null,
  statement_a_source_signal_id uuid not null references signals(id),
  statement_b_text text not null,
  statement_b_date date not null,
  statement_b_source_signal_id uuid not null references signals(id),
  created_at timestamptz not null default now()
);
create index if not exists contradictions_topic_idx on contradictions (topic_id, created_at);

-- upsert_topic_cluster gains an optional p_slug so topic creation stores a
-- slug atomically instead of a separate patch step. Existing slugs are kept
-- (coalesce) so re-clustering into the same title row never overwrites one.
create or replace function upsert_topic_cluster(
  p_title text,
  p_signal_ids uuid[],
  p_significance_score numeric,
  p_summary text default null,
  p_slug text default null
) returns uuid language plpgsql as $$
declare
  v_topic_id uuid;
  v_first_seen timestamptz;
  v_last_seen timestamptz;
  v_signal_id uuid;
begin
  select min(published_at), max(published_at)
  into v_first_seen, v_last_seen
  from signals
  where id = any(p_signal_ids);

  if v_last_seen is null then
    raise exception 'cannot upsert topic % without valid signal ids', p_title;
  end if;

  insert into topics (title, status, first_seen, last_signal_at, significance_score, summary, summary_generated_at, slug)
  values (p_title, 'raw_cluster', v_first_seen, v_last_seen, p_significance_score, p_summary, case when p_summary is null then null else now() end, p_slug)
  on conflict (title) do update
  set last_signal_at = greatest(topics.last_signal_at, excluded.last_signal_at),
      significance_score = greatest(topics.significance_score, excluded.significance_score),
      summary = coalesce(excluded.summary, topics.summary),
      summary_generated_at = case when excluded.summary is null then topics.summary_generated_at else now() end,
      slug = coalesce(topics.slug, excluded.slug)
  returning id into v_topic_id;

  foreach v_signal_id in array p_signal_ids loop
    insert into topic_signals (topic_id, signal_id)
    values (v_topic_id, v_signal_id)
    on conflict do nothing;
  end loop;

  return v_topic_id;
end;
$$;
