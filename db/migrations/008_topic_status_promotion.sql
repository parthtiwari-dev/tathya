-- Fixes upsert_topic_cluster hardcoding status = 'raw_cluster' forever, with
-- no path to 'live' regardless of the significance scorer's promotable flag.
-- See docs/audit_and_next_steps.md Section 7.2.
--
-- p_promotable is added as a new final parameter (default false) so this
-- stays backward compatible with any caller still on the old signature.
-- Status only ever upgrades raw_cluster -> live through this function, never
-- downgrades live -> raw_cluster -- that direction belongs to the lifecycle
-- archival process (Phase 5), not a single persist run that happens to see a
-- lower score.

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
begin
  select min(published_at), max(published_at)
  into v_first_seen, v_last_seen
  from signals
  where id = any(p_signal_ids);

  if v_last_seen is null then
    raise exception 'cannot upsert topic % without valid signal ids', p_title;
  end if;

  v_status := case when p_promotable then 'live' else 'raw_cluster' end;

  insert into topics (title, slug, status, first_seen, last_signal_at, significance_score, summary, summary_generated_at)
  values (p_title, coalesce(p_slug, p_title), v_status::topic_status, v_first_seen, v_last_seen, p_significance_score, p_summary, case when p_summary is null then null else now() end)
  on conflict (title) do update
  set last_signal_at = greatest(topics.last_signal_at, excluded.last_signal_at),
      significance_score = greatest(topics.significance_score, excluded.significance_score),
      summary = coalesce(excluded.summary, topics.summary),
      summary_generated_at = case when excluded.summary is null then topics.summary_generated_at else now() end,
      slug = coalesce(topics.slug, excluded.slug),
      -- Only ever upgrade raw_cluster -> live from this function; never
      -- silently demote an already-live topic back to raw_cluster.
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
