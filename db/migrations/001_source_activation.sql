-- Adds local activation helpers for safely testing disabled sources.
-- Run this in Supabase SQL Editor if your database was created before this file existed.

create or replace function set_source_enabled(
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

create or replace function source_activation_summary(p_source_key text)
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
