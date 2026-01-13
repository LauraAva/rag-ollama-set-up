CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS rag_chunks (
  id bigserial PRIMARY KEY,
  source text,
  chunk_index int,
  content text NOT NULL,
  metadata jsonb,
  embedding vector(1024) NOT NULL
);

CREATE INDEX IF NOT EXISTS rag_chunks_embedding_hnsw
  ON rag_chunks
  USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS qa_log (
  id bigserial PRIMARY KEY,
  question text NOT NULL,
  answer text NOT NULL,
  retrieved_chunk_ids bigint[],
  created_at timestamptz DEFAULT now()
);
