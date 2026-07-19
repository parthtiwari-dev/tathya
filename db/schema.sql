-- Tathya Phase 0 database foundation. Run in a fresh Supabase SQL editor.
create extension if not exists pgcrypto;
create extension if not exists vector;
create type source_type as enum ('rss', 'x', 'youtube', 'pib', 'parliament', 'official_website');
create type trust_category as enum ('official', 'media', 'citizen', 'foreign');
create type topic_status as enum ('raw_cluster', 'live', 'archived');
create type claim_source_type as enum ('govt', 'media', 'citizen', 'opposition');
create type relation_type as enum ('related', 'escalated_from', 'referenced_in', 'same_policy_area');
create type correction_status as enum ('reported', 'reviewed', 'fixed');

create table sources (id uuid primary key default gen_random_uuid(), source_key text not null unique, name text not null, type source_type not null, url text not null unique, trust_category trust_category not null, enabled boolean not null default true, created_at timestamptz not null default now());
create table signals (id uuid primary key default gen_random_uuid(), source_id uuid not null references sources(id), published_at timestamptz not null, ingested_at timestamptz not null default now(), title text, raw_text text not null, transcript text, url text not null, entities jsonb not null default '[]'::jsonb, snapshot_id uuid unique, duplicate_of_signal_id uuid references signals(id), embedding vector(768), unique (source_id, url));
create table snapshots (id uuid primary key default gen_random_uuid(), signal_id uuid not null unique references signals(id), captured_at timestamptz not null, raw_content text not null, content_hash char(64) not null, unique (signal_id, content_hash));
alter table signals add constraint signals_snapshot_id_fkey foreign key (snapshot_id) references snapshots(id);
create table entities (id uuid primary key default gen_random_uuid(), name text not null, type text not null check (type in ('person', 'ministry', 'scheme', 'law', 'place')), aliases jsonb not null default '[]'::jsonb, unique (name, type));
create table topics (id uuid primary key default gen_random_uuid(), title text not null, status topic_status not null default 'raw_cluster', first_seen timestamptz not null default now(), last_signal_at timestamptz not null, significance_score numeric not null default 0, summary text, summary_generated_at timestamptz);
create table topic_signals (topic_id uuid references topics(id), signal_id uuid references signals(id), primary key (topic_id, signal_id));
create table events (id uuid primary key default gen_random_uuid(), topic_id uuid not null references topics(id), event_date date not null, description text not null, source_signal_ids uuid[] not null, created_at timestamptz not null default now());
create table claims (id uuid primary key default gen_random_uuid(), topic_id uuid not null references topics(id), claim_text text not null, source_type claim_source_type not null, source_signal_id uuid not null references signals(id), quoted_span text not null, created_at timestamptz not null default now());
create table verifiable_facts (id uuid primary key default gen_random_uuid(), topic_id uuid not null references topics(id), fact_text text not null, primary_doc_url text not null, doc_type text not null check (doc_type in ('gazette', 'parliament_qa', 'pib', 'dataset')), quoted_span text not null, created_at timestamptz not null default now());
create table topic_relations (id uuid primary key default gen_random_uuid(), topic_id_a uuid not null references topics(id), topic_id_b uuid not null references topics(id), relation_type relation_type not null, created_at timestamptz not null default now(), check (topic_id_a <> topic_id_b), unique (topic_id_a, topic_id_b, relation_type));
create table corrections (id uuid primary key default gen_random_uuid(), target_table text not null check (target_table in ('claims', 'events', 'verifiable_facts')), target_row_id uuid not null, issue_description text not null, status correction_status not null default 'reported', resolved_at timestamptz, created_at timestamptz not null default now());
create table source_run_metrics (id uuid primary key default gen_random_uuid(), source_id uuid not null references sources(id), collected_at timestamptz not null default now(), signal_count integer not null check (signal_count >= 0), status text not null check (status in ('success', 'failure')), detail text);

create function reject_snapshot_mutation() returns trigger language plpgsql as $$ begin raise exception 'snapshots are immutable'; end; $$;
create trigger snapshots_no_update before update or delete on snapshots for each row execute function reject_snapshot_mutation();
create index signals_source_published_idx on signals (source_id, published_at desc);
create index signals_canonical_idx on signals (duplicate_of_signal_id) where duplicate_of_signal_id is null;
create index topics_live_updated_idx on topics (status, last_signal_at desc);
create index claims_topic_idx on claims (topic_id, created_at);
create index events_topic_date_idx on events (topic_id, event_date);
create index snapshots_content_hash_idx on snapshots (content_hash);
create index source_run_metrics_source_time_idx on source_run_metrics (source_id, collected_at desc);

-- Atomically write one raw signal and its immutable snapshot. The function is
-- idempotent per source URL, so re-running a watcher cannot create duplicates.
create function record_signal_snapshot(
  p_source_key text,
  p_published_at timestamptz,
  p_title text,
  p_raw_text text,
  p_transcript text,
  p_url text,
  p_captured_at timestamptz,
  p_raw_content text,
  p_content_hash char(64)
) returns uuid language plpgsql as $$
declare
  v_source_id uuid;
  v_signal_id uuid;
  v_snapshot_id uuid;
  v_duplicate_of_signal_id uuid;
begin
  select id into v_source_id from sources where source_key = p_source_key and enabled;
  if v_source_id is null then
    raise exception 'configured source % does not exist or is disabled', p_source_key;
  end if;

  insert into signals (source_id, published_at, title, raw_text, transcript, url)
  values (v_source_id, p_published_at, p_title, p_raw_text, p_transcript, p_url)
  on conflict (source_id, url) do update set url = excluded.url
  returning id into v_signal_id;

  select id into v_snapshot_id from snapshots where signal_id = v_signal_id;
  if v_snapshot_id is null then
    select signal_id into v_duplicate_of_signal_id
    from snapshots
    where content_hash = p_content_hash and signal_id <> v_signal_id
    order by captured_at asc
    limit 1;
    insert into snapshots (signal_id, captured_at, raw_content, content_hash)
    values (v_signal_id, p_captured_at, p_raw_content, p_content_hash)
    returning id into v_snapshot_id;
    update signals
    set snapshot_id = v_snapshot_id,
        duplicate_of_signal_id = v_duplicate_of_signal_id
    where id = v_signal_id;
  end if;
  return v_signal_id;
end;
$$;

create function record_source_run(
  p_source_key text,
  p_signal_count integer,
  p_status text,
  p_detail text default null
) returns void language plpgsql as $$
declare v_source_id uuid;
begin
  select id into v_source_id from sources where source_key = p_source_key;
  if v_source_id is null then raise exception 'configured source % does not exist', p_source_key; end if;
  insert into source_run_metrics (source_id, signal_count, status, detail)
  values (v_source_id, p_signal_count, p_status, p_detail);
end;
$$;

create function recent_source_counts(p_source_key text, p_limit integer default 10)
returns table (signal_count integer) language sql stable as $$
  select metric.signal_count
  from source_run_metrics metric
  join sources source on source.id = metric.source_id
  where source.source_key = p_source_key and metric.status = 'success'
  order by metric.collected_at desc
  limit p_limit;
$$;

create function set_source_enabled(
  p_source_key text,
  p_enabled boolean
) returns boolean language plpgsql as $$
declare
  v_previous boolean;
begin
  select enabled into v_previous from sources where source_key = p_source_key;
  if v_previous is null then raise exception 'configured source % does not exist', p_source_key; end if;
  update sources set enabled = p_enabled where source_key = p_source_key;
  return v_previous;
end;
$$;

create function source_activation_summary(p_source_key text)
returns table (
  source_key text,
  enabled boolean,
  signal_count bigint,
  snapshot_count bigint,
  canonical_signal_count bigint,
  source_run_count bigint,
  last_run_at timestamptz
) language sql stable as $$
  select
    source.source_key,
    source.enabled,
    count(distinct signal.id) as signal_count,
    count(distinct snapshot.id) as snapshot_count,
    count(distinct signal.id) filter (where signal.duplicate_of_signal_id is null) as canonical_signal_count,
    count(distinct metric.id) as source_run_count,
    max(metric.collected_at) as last_run_at
  from sources source
  left join signals signal on signal.source_id = source.id
  left join snapshots snapshot on snapshot.signal_id = signal.id
  left join source_run_metrics metric on metric.source_id = source.id
  where source.source_key = p_source_key
  group by source.source_key, source.enabled;
$$;
