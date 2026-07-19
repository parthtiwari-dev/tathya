-- Adds idempotent relation persistence used by the Phase 3 relations builder.

create or replace function upsert_topic_relation(
  p_topic_id_a uuid,
  p_topic_id_b uuid,
  p_relation_type relation_type
) returns uuid language plpgsql as $$
declare
  v_relation_id uuid;
  v_a uuid;
  v_b uuid;
begin
  if p_topic_id_a = p_topic_id_b then
    raise exception 'a topic cannot relate to itself';
  end if;

  if p_topic_id_a < p_topic_id_b then
    v_a := p_topic_id_a;
    v_b := p_topic_id_b;
  else
    v_a := p_topic_id_b;
    v_b := p_topic_id_a;
  end if;

  insert into topic_relations (topic_id_a, topic_id_b, relation_type)
  values (v_a, v_b, p_relation_type)
  on conflict (topic_id_a, topic_id_b, relation_type) do update
  set relation_type = excluded.relation_type
  returning id into v_relation_id;

  return v_relation_id;
end;
$$;
