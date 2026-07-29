-- Hindi for claims, event descriptions, verifiable facts, and open
-- questions -- the increment deliberately left out of migration 010.
--
-- quoted_span is never translated on any table here (it's a direct quote,
-- not Gemini's own text) -- only claim_text/description/fact_text get a
-- Hindi sibling column. On the extractive-only path these stay null (see
-- pipeline/generation/case_file_builder.py's DraftClaim/DraftEvent/DraftFact
-- comments for why: claim_text/fact_text literally ARE the quoted_span on
-- that path, so there's nothing to honestly translate independently of the
-- quote itself). question_hi is the one field that's always populated
-- regardless of path, since open_questions are a fixed template sentence,
-- not extracted text.
--
-- Safe to re-run.

alter table claims add column if not exists claim_text_hi text;
alter table events add column if not exists description_hi text;
alter table verifiable_facts add column if not exists fact_text_hi text;
alter table open_questions add column if not exists question_hi text;
alter table contradictions add column if not exists statement_a_text_hi text;
alter table contradictions add column if not exists statement_b_text_hi text;

create or replace function append_topic_event(
  p_topic_id uuid,
  p_event_date date,
  p_description text,
  p_source_signal_ids uuid[],
  p_description_hi text default null
) returns uuid language plpgsql as $$
declare v_event_id uuid;
begin
  insert into events (topic_id, event_date, description, source_signal_ids, description_hi)
  values (p_topic_id, p_event_date, p_description, p_source_signal_ids, p_description_hi)
  on conflict (topic_id, event_date, md5(description)) do update
  set source_signal_ids = excluded.source_signal_ids,
      description_hi = coalesce(excluded.description_hi, events.description_hi)
  returning id into v_event_id;
  return v_event_id;
end;
$$;

create or replace function append_topic_claim(
  p_topic_id uuid,
  p_claim_text text,
  p_source_type claim_source_type,
  p_source_signal_id uuid,
  p_quoted_span text,
  p_claim_text_hi text default null
) returns uuid language plpgsql as $$
declare v_claim_id uuid;
begin
  insert into claims (topic_id, claim_text, source_type, source_signal_id, quoted_span, claim_text_hi)
  values (p_topic_id, p_claim_text, p_source_type, p_source_signal_id, p_quoted_span, p_claim_text_hi)
  on conflict (topic_id, source_signal_id, md5(claim_text)) do update
  set quoted_span = excluded.quoted_span,
      claim_text_hi = coalesce(excluded.claim_text_hi, claims.claim_text_hi)
  returning id into v_claim_id;
  return v_claim_id;
end;
$$;

create or replace function append_topic_fact(
  p_topic_id uuid,
  p_fact_text text,
  p_primary_doc_url text,
  p_doc_type text,
  p_quoted_span text,
  p_fact_text_hi text default null
) returns uuid language plpgsql as $$
declare v_fact_id uuid;
begin
  insert into verifiable_facts (topic_id, fact_text, primary_doc_url, doc_type, quoted_span, fact_text_hi)
  values (p_topic_id, p_fact_text, p_primary_doc_url, p_doc_type, p_quoted_span, p_fact_text_hi)
  on conflict (topic_id, primary_doc_url, md5(fact_text)) do update
  set quoted_span = excluded.quoted_span,
      fact_text_hi = coalesce(excluded.fact_text_hi, verifiable_facts.fact_text_hi)
  returning id into v_fact_id;
  return v_fact_id;
end;
$$;
