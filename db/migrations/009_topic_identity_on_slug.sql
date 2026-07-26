-- Decouples topic identity/dedup from `title` (now a real, evolving
-- headline picked from a signal's own title -- see
-- pipeline/generation/case_file_builder.py's _representative_title) and
-- moves it to `slug` (derived from the stable cluster anchor entity, e.g.
-- "reserve-bank-of-india" -- doesn't change as headlines are reworded
-- across runs).
--
-- Without this: upsert_topic_cluster's old `on conflict (title)` would
-- treat every re-generated headline as a brand-new topic instead of
-- updating the same one, and the separate `topics_title_idx` unique
-- index would eventually throw a hard error the first time two
-- unrelated topics happened to produce identical headline text.
--
-- See docs/audit_and_next_steps.md Section 14. Safe to re-run.

drop index if exists topics_title_idx;

create or replace function upsert_topic_cluster(
  p_title text,
  p_signal_ids uuid[],
  p_significance_score numeric,
  p_summary text default null,
  p_slug text default null,
  p_promotable boolean default false
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

  insert into topics (title, status, first_seen, last_signal_at, significance_score, summary, summary_generated_at, slug)
  values (p_title, v_status::topic_status, v_first_seen, v_last_seen, p_significance_score, p_summary, case when p_summary is null then null else now() end, v_slug)
  on conflict (slug) where slug is not null do update
  set title = excluded.title,
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
