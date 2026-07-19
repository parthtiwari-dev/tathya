-- Adds a guarded RPC for Phase 2 near-duplicate review.

create or replace function mark_signal_duplicate(
  p_duplicate_signal_id uuid,
  p_canonical_signal_id uuid
) returns void language plpgsql as $$
begin
  if p_duplicate_signal_id = p_canonical_signal_id then
    raise exception 'a signal cannot duplicate itself';
  end if;

  if not exists (select 1 from signals where id = p_duplicate_signal_id) then
    raise exception 'duplicate signal % does not exist', p_duplicate_signal_id;
  end if;

  if not exists (select 1 from signals where id = p_canonical_signal_id) then
    raise exception 'canonical signal % does not exist', p_canonical_signal_id;
  end if;

  update signals
  set duplicate_of_signal_id = p_canonical_signal_id
  where id = p_duplicate_signal_id
    and duplicate_of_signal_id is null;
end;
$$;
