-- rag_extended.sql
-- Adds: collections (separate RAGs by sensitivity), ACL scaffolding, test runs/results,
-- audit fields, feedback table, and safe defaults.
-- Run on database: ragdb

CREATE EXTENSION IF NOT EXISTS vector;

-- 1) Collections (separate RAGs by sensitivity level)
CREATE TABLE IF NOT EXISTS rag_collections (
  id bigserial PRIMARY KEY,
  name text NOT NULL UNIQUE,
  sensitivity_level int NOT NULL DEFAULT 0, -- 0=public, higher=more sensitive
  description text,
  created_at timestamptz DEFAULT now()
);

-- Ensure a default public collection exists
INSERT INTO rag_collections (name, sensitivity_level, description)
VALUES ('public', 0, 'Default non-sensitive collection')
ON CONFLICT (name) DO UPDATE
SET sensitivity_level = EXCLUDED.sensitivity_level;

-- 2) Ensure rag_chunks exists + add collection support
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'rag_chunks') THEN
    CREATE TABLE rag_chunks (
      id bigserial PRIMARY KEY,
      source text,
      chunk_index int,
      content text NOT NULL,
      metadata jsonb,
      embedding vector(1024) NOT NULL,
      created_at timestamptz DEFAULT now(),
      collection_id bigint REFERENCES rag_collections(id)
    );
  END IF;
END $$;

ALTER TABLE IF EXISTS rag_chunks
  ADD COLUMN IF NOT EXISTS created_at timestamptz DEFAULT now(),
  ADD COLUMN IF NOT EXISTS collection_id bigint REFERENCES rag_collections(id);

-- Backfill: assign existing chunks to 'public' collection if missing
UPDATE rag_chunks
SET collection_id = (SELECT id FROM rag_collections WHERE name='public')
WHERE collection_id IS NULL;

-- Indexes
CREATE INDEX IF NOT EXISTS rag_chunks_collection_id_idx ON rag_chunks(collection_id);

-- HNSW index (keep your existing one if already created)
CREATE INDEX IF NOT EXISTS rag_chunks_embedding_hnsw
  ON rag_chunks
  USING hnsw (embedding vector_cosine_ops);

-- 3) QA log extensions (audit + relevance + collection)
-- Base table qa_log already exists in your setup; we just extend it.
ALTER TABLE IF EXISTS qa_log
  ADD COLUMN IF NOT EXISTS collection_id bigint REFERENCES rag_collections(id),
  ADD COLUMN IF NOT EXISTS used_rag boolean,
  ADD COLUMN IF NOT EXISTS relevance_distance double precision,
  ADD COLUMN IF NOT EXISTS audit_verdict text,
  ADD COLUMN IF NOT EXISTS audit_score double precision,
  ADD COLUMN IF NOT EXISTS audit_details jsonb;

-- 4) Feedback table (user feedback stored in DB)
CREATE TABLE IF NOT EXISTS rag_feedback (
  id bigserial PRIMARY KEY,
  qa_id bigint REFERENCES qa_log(id) ON DELETE CASCADE,
  principal text,
  rating int, -- e.g. -1/0/+1 or 1..5
  comment text,
  created_at timestamptz DEFAULT now()
);

-- 5) Test runs/results (automated evaluation of RAG)
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

-- 6) Authorization scaffolding (local now; AD groups later)
-- Minimal concept: principals + per-collection ACL.
CREATE TABLE IF NOT EXISTS auth_principals (
  principal text PRIMARY KEY,
  kind text NOT NULL DEFAULT 'local', -- local/ad
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rag_collection_acl (
  collection_id bigint NOT NULL REFERENCES rag_collections(id) ON DELETE CASCADE,
  principal text NOT NULL REFERENCES auth_principals(principal) ON DELETE CASCADE,
  can_read boolean NOT NULL DEFAULT true,
  can_write boolean NOT NULL DEFAULT false,
  PRIMARY KEY(collection_id, principal)
);

-- Seed a local admin principal and allow read/write on public collection
INSERT INTO auth_principals (principal, kind)
VALUES ('local_admin', 'local')
ON CONFLICT (principal) DO NOTHING;

INSERT INTO rag_collection_acl (collection_id, principal, can_read, can_write)
SELECT c.id, 'local_admin', true, true
FROM rag_collections c
WHERE c.name='public'
ON CONFLICT (collection_id, principal) DO UPDATE
SET can_read=EXCLUDED.can_read, can_write=EXCLUDED.can_write;