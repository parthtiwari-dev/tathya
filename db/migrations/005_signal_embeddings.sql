-- Adds pgvector search support for signal embeddings.

create index if not exists signals_embedding_hnsw_idx
on signals using hnsw (embedding vector_cosine_ops)
where embedding is not null;

create or replace function store_signal_embedding(
  p_signal_id uuid,
  p_embedding text
) returns void language plpgsql as $$
begin
  update signals
  set embedding = p_embedding::vector
  where id = p_signal_id;
end;
$$;

create or replace function match_similar_signals(
  p_query_embedding text,
  p_match_count integer default 20,
  p_match_threshold double precision default 0.0
) returns table (
  id uuid,
  published_at timestamptz,
  title text,
  raw_text text,
  url text,
  source_key text,
  trust_category trust_category,
  similarity double precision
) language sql stable as $$
  select
    signal.id,
    signal.published_at,
    signal.title,
    signal.raw_text,
    signal.url,
    source.source_key,
    source.trust_category,
    1 - (signal.embedding <=> p_query_embedding::vector) as similarity
  from signals signal
  join sources source on source.id = signal.source_id
  where signal.embedding is not null
    and signal.duplicate_of_signal_id is null
    and 1 - (signal.embedding <=> p_query_embedding::vector) >= p_match_threshold
  order by signal.embedding <=> p_query_embedding::vector
  limit p_match_count;
$$;
