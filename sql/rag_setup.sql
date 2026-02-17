CREATE EXTENSION IF NOT EXISTS vector;

-- Collections allow multiple RAG corpora with optional sensitivity levels.
CREATE TABLE IF NOT EXISTS rag_collections (
  id bigserial PRIMARY KEY,
  name text NOT NULL UNIQUE,
  sensitivity_level int NOT NULL DEFAULT 0,
  description text,
  created_at timestamptz DEFAULT now()
);

INSERT INTO rag_collections (name, sensitivity_level, description)
VALUES ('public', 0, 'Default non-sensitive collection')
ON CONFLICT (name) DO UPDATE
SET sensitivity_level = EXCLUDED.sensitivity_level;

-- Core chunks table for vector search.
CREATE TABLE IF NOT EXISTS rag_chunks (
  id bigserial PRIMARY KEY,
  source text,
  chunk_index int,
  content text NOT NULL,
  metadata jsonb,
  embedding vector(1024) NOT NULL,
  created_at timestamptz DEFAULT now(),
  collection_id bigint REFERENCES rag_collections(id)
);

ALTER TABLE rag_chunks
  ALTER COLUMN collection_id DROP NOT NULL;

-- Backfill older rows to the default public collection.
UPDATE rag_chunks
SET collection_id = (SELECT id FROM rag_collections WHERE name = 'public')
WHERE collection_id IS NULL;

CREATE INDEX IF NOT EXISTS rag_chunks_collection_id_idx ON rag_chunks(collection_id);
CREATE INDEX IF NOT EXISTS rag_chunks_embedding_hnsw
  ON rag_chunks
  USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS qa_log (
  id bigserial PRIMARY KEY,
  question text NOT NULL,
  answer text NOT NULL,
  retrieved_chunk_ids bigint[],
  collection_id bigint REFERENCES rag_collections(id),
  used_rag boolean,
  relevance_distance double precision,
  audit_verdict text,
  audit_score double precision,
  audit_details jsonb,
  verified boolean NOT NULL DEFAULT false,
  promoted_chunk_id bigint REFERENCES rag_chunks(id),
  promoted_at timestamptz,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rag_feedback (
  id bigserial PRIMARY KEY,
  qa_id bigint REFERENCES qa_log(id) ON DELETE CASCADE,
  principal text,
  rating int,
  comment text,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rag_test_runs (
  id bigserial PRIMARY KEY,
  run_name text NOT NULL,
  settings jsonb,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rag_test_results (
  id bigserial PRIMARY KEY,
  run_id bigint NOT NULL REFERENCES rag_test_runs(id) ON DELETE CASCADE,
  test_id text NOT NULL,
  collection text,
  question text NOT NULL,
  expected jsonb,
  answer text,
  used_rag boolean,
  relevance_distance double precision,
  audit_verdict text,
  audit_score double precision,
  passed boolean,
  details jsonb,
  created_at timestamptz DEFAULT now()
);
