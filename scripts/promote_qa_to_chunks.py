import os
import json
import argparse
from datetime import datetime, timedelta, timezone

import psycopg
from pgvector.psycopg import register_vector, Vector
from ollama import embed

EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")

def get_vec(text: str):
    r = embed(model=EMBED_MODEL, input=text)
    v = r["embeddings"][0] if isinstance(r["embeddings"][0], list) else r["embeddings"]
    return v

def get_vector_dim(cur) -> int:
    cur.execute("""
        SELECT a.atttypmod - 4 AS dim
        FROM pg_attribute a
        JOIN pg_class c ON c.oid = a.attrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname='public'
          AND c.relname='rag_chunks'
          AND a.attname='embedding'
          AND a.attnum > 0
          AND NOT a.attisdropped
        LIMIT 1
    """)
    row = cur.fetchone()
    if not row or row[0] is None:
        raise RuntimeError("Could not determine vector dimension for rag_chunks.embedding")
    return int(row[0])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--only-verified", action="store_true")
    ap.add_argument("--since-hours", type=int, default=None)
    ap.add_argument("--source", default="qa_promoted")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    where = ["promoted_chunk_id IS NULL"]
    params = []

    if args.only_verified:
        where.append("verified = TRUE")

    if args.since_hours is not None:
        since = datetime.now(timezone.utc) - timedelta(hours=args.since_hours)
        where.append("created_at >= %s")
        params.append(since)

    where_sql = " AND ".join(where)

    with psycopg.connect("") as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            dim = get_vector_dim(cur)

            cur.execute(f"""
                SELECT id, question, answer, created_at
                FROM qa_log
                WHERE {where_sql}
                ORDER BY id ASC
                LIMIT %s
            """, (*params, args.limit))
            rows = cur.fetchall()

            if not rows:
                print("Nothing to promote (no matching qa_log rows).")
                return

            promoted = 0
            for qa_id, q, a, created_at in rows:
                content = f"Q: {q.strip()}\nA: {a.strip()}"
                vec = get_vec(content)

                if len(vec) != dim:
                    raise RuntimeError(
                        f"Embedding dim mismatch: got {len(vec)} from model '{EMBED_MODEL}', "
                        f"but rag_chunks.embedding is vector({dim})."
                    )

                meta = {
                    "type": "qa_log",
                    "qa_id": qa_id,
                    "created_at": created_at.isoformat() if created_at else None,
                    "embed_model": EMBED_MODEL,
                }

                if args.dry_run:
                    print(f"[DRY RUN] would promote qa_log.id={qa_id}")
                    continue

                cur.execute(
                    """
                    INSERT INTO rag_chunks (source, chunk_index, content, metadata, embedding)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (args.source, 0, content, json.dumps(meta), Vector(vec))
                )
                chunk_id = cur.fetchone()[0]

                cur.execute(
                    "UPDATE qa_log SET promoted_chunk_id=%s, promoted_at=now() WHERE id=%s",
                    (chunk_id, qa_id)
                )
                promoted += 1

            conn.commit()

    print(f"Promoted {promoted} Q/A rows into rag_chunks (source={args.source}).")

if __name__ == "__main__":
    main()
