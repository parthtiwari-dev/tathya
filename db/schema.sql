-- Tathya Phase 0 database foundation. Run in a fresh Supabase SQL editor.
create extension if not exists pgcrypto;
create extension if not exists vector;
create type source_type as enum ('rss', 'x', 'youtube', 'pib', 'parliament');
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

create function reject_snapshot_mutation() returns trigger language plpgsql as $$ begin raise exception 'snapshots are immutable'; end; $$;
create trigger snapshots_no_update before update or delete on snapshots for each row execute function reject_snapshot_mutation();
create index signals_source_published_idx on signals (source_id, published_at desc);
create index signals_canonical_idx on signals (duplicate_of_signal_id) where duplicate_of_signal_id is null;
create index topics_live_updated_idx on topics (status, last_signal_at desc);
create index claims_topic_idx on claims (topic_id, created_at);
create index events_topic_date_idx on events (topic_id, event_date);
