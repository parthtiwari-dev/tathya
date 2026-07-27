-- Adds Hindi columns for topic-level display text (title, summary) --
-- the highest-visibility content shown on the feed and topic page.
--
-- Deliberately NOT included in this pass: claim text, event descriptions,
-- verifiable facts, open questions. Those are the literal quoted/verifiable
-- units this project exists to protect; translating them accurately needs
-- the same grounded-generation care as the claims themselves, and doing
-- that in the same pass as this simpler topic-level text risked exactly the
-- kind of rushed-mistranslation-of-a-claim this project is meant to guard
-- against. Next increment, not forgotten -- see
-- docs/audit_and_next_steps.md Section 15.
--
-- Safe to re-run.

alter table topics add column if not exists title_hi text;
alter table topics add column if not exists summary_hi text;

create or replace function upsert_topic_cluster(
  p_title text,
  p_signal_ids uuid[],
  p_significance_score numeric,
  p_summary text default null,
  p_slug text default null,
  p_promotable boolean default false,
  p_title_hi text default null,
  p_summary_hi text default null
) returns uuid language plpgsql as $$
declare
  v_topic_id uuid;
  v_first_seen timestamptz;
  v_last_seen timestamptz;
  v_signal_id uuid;
  v_status text;
  v_slug text;
begin
  select min(published_at), max(published_at)
  into v_first_seen, v_last_seen
  from signals
  where id = any(p_signal_ids);

  if v_last_seen is null then
    raise exception 'cannot upsert topic % without valid signal ids', p_title;
  end if;

  v_status := case when p_promotable then 'live' else 'raw_cluster' end;
  v_slug := coalesce(p_slug, p_title);

  insert into topics (title, status, first_seen, last_signal_at, significance_score, summary, summary_generated_at, slug, title_hi, summary_hi)
  values (p_title, v_status::topic_status, v_first_seen, v_last_seen, p_significance_score, p_summary, case when p_summary is null then null else now() end, v_slug, p_title_hi, p_summary_hi)
  on conflict (slug) where slug is not null do update
  set title = excluded.title,
      title_hi = coalesce(excluded.title_hi, topics.title_hi),
      summary_hi = coalesce(excluded.summary_hi, topics.summary_hi),
      last_signal_at = greatest(topics.last_signal_at, excluded.last_signal_at),
      significance_score = greatest(topics.significance_score, excluded.significance_score),
      summary = coalesce(excluded.summary, topics.summary),
      summary_generated_at = case when excluded.summary is null then topics.summary_generated_at else now() end,
      status = case when excluded.status = 'live' then 'live'::topic_status else topics.status end
  returning id into v_topic_id;

  foreach v_signal_id in array p_signal_ids loop
    insert into topic_signals (topic_id, signal_id)
    values (v_topic_id, v_signal_id)
    on conflict do nothing;
  end loop;

  return v_topic_id;
end;
$$;
