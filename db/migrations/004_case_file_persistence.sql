-- Adds idempotent topic/event/claim/fact persistence for private Phase 3 drafts.

create unique index if not exists topics_title_idx on topics (title);
create unique index if not exists events_topic_description_date_idx on events (topic_id, event_date, md5(description));
create unique index if not exists claims_topic_signal_text_idx on claims (topic_id, source_signal_id, md5(claim_text));
create unique index if not exists facts_topic_doc_text_idx on verifiable_facts (topic_id, primary_doc_url, md5(fact_text));

create or replace function upsert_topic_cluster(
  p_title text,
  p_signal_ids uuid[],
  p_significance_score numeric,
  p_summary text default null
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

  insert into topics (title, status, first_seen, last_signal_at, significance_score, summary, summary_generated_at)
  values (p_title, 'raw_cluster', v_first_seen, v_last_seen, p_significance_score, p_summary, case when p_summary is null then null else now() end)
  on conflict (title) do update
  set last_signal_at = greatest(topics.last_signal_at, excluded.last_signal_at),
      significance_score = greatest(topics.significance_score, excluded.significance_score),
      summary = coalesce(excluded.summary, topics.summary),
      summary_generated_at = case when excluded.summary is null then topics.summary_generated_at else now() end
  returning id into v_topic_id;

  foreach v_signal_id in array p_signal_ids loop
    insert into topic_signals (topic_id, signal_id)
    values (v_topic_id, v_signal_id)
    on conflict do nothing;
  end loop;

  return v_topic_id;
end;
$$;

create or replace function append_topic_event(
  p_topic_id uuid,
  p_event_date date,
  p_description text,
  p_source_signal_ids uuid[]
) returns uuid language plpgsql as $$
declare v_event_id uuid;
begin
  insert into events (topic_id, event_date, description, source_signal_ids)
  values (p_topic_id, p_event_date, p_description, p_source_signal_ids)
  on conflict (topic_id, event_date, md5(description)) do update
  set source_signal_ids = excluded.source_signal_ids
  returning id into v_event_id;
  return v_event_id;
end;
$$;

create or replace function append_topic_claim(
  p_topic_id uuid,
  p_claim_text text,
  p_source_type claim_source_type,
  p_source_signal_id uuid,
  p_quoted_span text
) returns uuid language plpgsql as $$
declare v_claim_id uuid;
begin
  insert into claims (topic_id, claim_text, source_type, source_signal_id, quoted_span)
  values (p_topic_id, p_claim_text, p_source_type, p_source_signal_id, p_quoted_span)
  on conflict (topic_id, source_signal_id, md5(claim_text)) do update
  set quoted_span = excluded.quoted_span
  returning id into v_claim_id;
  return v_claim_id;
end;
$$;

create or replace function append_topic_fact(
  p_topic_id uuid,
  p_fact_text text,
  p_primary_doc_url text,
  p_doc_type text,
  p_quoted_span text
) returns uuid language plpgsql as $$
declare v_fact_id uuid;
begin
  insert into verifiable_facts (topic_id, fact_text, primary_doc_url, doc_type, quoted_span)
  values (p_topic_id, p_fact_text, p_primary_doc_url, p_doc_type, p_quoted_span)
  on conflict (topic_id, primary_doc_url, md5(fact_text)) do update
  set quoted_span = excluded.quoted_span
  returning id into v_fact_id;
  return v_fact_id;
end;
$$;
