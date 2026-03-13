-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create embeddings table
CREATE TABLE IF NOT EXISTS public.embeddings (
  id BIGSERIAL PRIMARY KEY,
  content TEXT NOT NULL,
  embedding VECTOR(1024),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster search
CREATE INDEX IF NOT EXISTS idx_embeddings_vector 
ON public.embeddings 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Create search function
CREATE OR REPLACE FUNCTION match_embeddings(
  query_embedding VECTOR(1024),
  match_count INT DEFAULT 3,
  match_threshold FLOAT DEFAULT 0.5
)
RETURNS TABLE (
  id BIGINT,
  content TEXT,
  metadata JSONB,
  similarity FLOAT
) LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    embeddings.id,
    embeddings.content,
    embeddings.metadata,
    (1 - (embeddings.embedding <=> query_embedding)) AS similarity
  FROM embeddings
  WHERE (1 - (embeddings.embedding <=> query_embedding)) > match_threshold
  ORDER BY embeddings.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Set table permissions (RLS)
ALTER TABLE public.embeddings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users"
  ON public.embeddings
  FOR SELECT
  USING (true);

CREATE POLICY "Enable insert for all users"
  ON public.embeddings
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Enable delete for all users"
  ON public.embeddings
  FOR DELETE
  USING (true);
