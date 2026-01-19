from __future__ import annotations
import os, json, argparse
from pathlib import Path
import psycopg
from pgvector.psycopg import register_vector, Vector
from ollama import embed, chat

# --- IMPORTANT: allow "import raglib" when running scripts from /scripts ---
import sys
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from raglib.config import EMBED_MODEL, CHAT_MODEL, AUDIT_MODEL, TOP_K, RELEVANCE_MAX_DISTANCE  # noqa: E402


def get_vec(text: str) -> list[float]:
    r = embed(model=EMBED_MODEL, input=text)
    v = r["embeddings"][0] if isinstance(r["embeddings"][0], list) else r["embeddings"]
    return v


def get_collection(cur, name: str) -> tuple[int, int]:
    cur.execute("SELECT id, sensitivity_level FROM rag_collections WHERE name=%s", (name,))
    row = cur.fetchone()
    if not row:
        raise RuntimeError(f"Collection not found: {name} (create it by running ingest.py or inserting into rag_collections)")
    return int(row[0]), int(row[1])


def retrieve(cur, collection_id: int, qvec: list[float], k: int) -> list[tuple[int, str, float]]:
    cur.execute(
        """
        SELECT id, content, (embedding <=> %s) AS distance
        FROM rag_chunks
        WHERE collection_id = %s
        ORDER BY embedding <=> %s
        LIMIT %s
        """,
        (Vector(qvec), collection_id, Vector(qvec), k),
    )
    return [(int(r[0]), str(r[1]), float(r[2])) for r in cur.fetchall()]


def llm_answer(question: str, context: str | None) -> str:
    if context:
        prompt = f"""Use ONLY the context to answer.
If the context is not enough, say you don't have enough information.

Context:
{context}

Question: {question}
Answer:"""
    else:
        prompt = f"""Answer the question.
If you are not sure or you don't have verified info, say you don't have enough information.

Question: {question}
Answer:"""

    resp = chat(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.2},
    )
    return resp["message"]["content"]


def audit_answer(question: str, context: str | None, answer: str) -> dict:
    # LLM-based audit: tries to check if answer is supported by context.
    audit_prompt = f"""You are a strict auditor.
Return JSON only with keys: verdict (pass|fail|unknown), score (0..1), notes (string).
Rules:
- If context is provided, answer must be supported by context.
- If no context, verdict should usually be 'unknown' unless answer admits insufficient info.

Context:
{context or "(none)"}

Question: {question}
Answer: {answer}

JSON:"""
    resp = chat(model=AUDIT_MODEL, messages=[{"role": "user", "content": audit_prompt}], options={"temperature": 0.0})
    txt = resp["message"]["content"].strip()

    # Try parse JSON, otherwise fall back
    try:
        j = json.loads(txt)
        verdict = str(j.get("verdict", "unknown")).lower()
        score = float(j.get("score", 0.0))
        notes = str(j.get("notes", ""))
        return {"verdict": verdict, "score": score, "notes": notes, "raw": txt}
    except Exception:
        return {"verdict": "unknown", "score": 0.0, "notes": "audit_json_parse_failed", "raw": txt}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question")
    ap.add_argument("--collection", default=os.getenv("DEFAULT_COLLECTION", "public"))
    ap.add_argument("--k", type=int, default=int(os.getenv("TOP_K", str(TOP_K))))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    max_sens = int(os.getenv("MAX_SENSITIVITY", "0"))

    with psycopg.connect("") as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            collection_id, collection_sens = get_collection(cur, args.collection)

            if collection_sens > max_sens:
                out = {
                    "answer": "Access denied: collection sensitivity is above your allowed level.",
                    "used_rag": False,
                    "relevance_distance": None,
                    "retrieved_chunk_ids": [],
                    "audit": {"verdict": "fail", "score": 0.0, "notes": "sensitivity_denied"},
                }
                if args.json:
                    print(json.dumps(out, ensure_ascii=False))
                else:
                    print(out["answer"])
                return

            qvec = get_vec(args.question)
            rows = retrieve(cur, collection_id, qvec, args.k)

    chunk_ids = [r[0] for r in rows]
    best_distance = rows[0][2] if rows else None

    used_rag = bool(rows) and (best_distance is not None) and (best_distance <= RELEVANCE_MAX_DISTANCE)
    context = "\n\n".join([f"[chunk {rid} | dist={dist:.4f}]\n{txt}" for rid, txt, dist in rows]) if used_rag else None

    answer = llm_answer(args.question, context)
    audit = audit_answer(args.question, context, answer)

    # Log to DB
    with psycopg.connect("") as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM rag_collections WHERE name=%s", (args.collection,))
            cid = cur.fetchone()
            cid = int(cid[0]) if cid else None

            cur.execute(
                """
                INSERT INTO qa_log (question, answer, retrieved_chunk_ids, collection_id, used_rag, relevance_distance, audit_verdict, audit_score, audit_details)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    args.question,
                    answer,
                    chunk_ids,
                    cid,
                    used_rag,
                    best_distance,
                    audit.get("verdict"),
                    audit.get("score"),
                    json.dumps(audit, ensure_ascii=False),
                ),
            )
        conn.commit()

    out = {
        "answer": answer,
        "used_rag": used_rag,
        "relevance_distance": best_distance,
        "retrieved_chunk_ids": chunk_ids,
        "audit": {"verdict": audit.get("verdict"), "score": audit.get("score"), "notes": audit.get("notes")},
    }

    if args.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        print("\nAnswer:\n", answer)
        print("\nUsed RAG:", used_rag, " best_distance=", best_distance)
        print("Retrieved chunk ids:", chunk_ids)
        print("Audit:", out["audit"])


if __name__ == "__main__":
    main()