import os
import psycopg
from pgvector.psycopg import register_vector, Vector
from ollama import embed, chat

EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")
CHAT_MODEL  = os.getenv("CHAT_MODEL", "gemma3:4b")

def get_vec(text: str):
    r = embed(model=EMBED_MODEL, input=text)
    v = r["embeddings"][0] if isinstance(r["embeddings"][0], list) else r["embeddings"]
    return v

def rag(question: str, k: int = 5):
    qvec = get_vec(question)

    with psycopg.connect("") as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, content FROM rag_chunks ORDER BY embedding <=> %s LIMIT %s",
                (Vector(qvec), k),
            )
            rows = cur.fetchall()

    chunk_ids = [r[0] for r in rows]
    context = "\n\n".join([f"[chunk {rid}]\n{txt}" for rid, txt in rows])

    prompt = f"""Use ONLY the context to answer.
If the context is not enough, say you don't have enough information.

Context:
{context}

Question: {question}
Answer:"""

    resp = chat(model=CHAT_MODEL, messages=[{"role": "user", "content": prompt}], options={"temperature": 0.2})
    answer = resp["message"]["content"]

    with psycopg.connect("") as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO qa_log (question, answer, retrieved_chunk_ids) VALUES (%s,%s,%s)",
                (question, answer, chunk_ids),
            )
        conn.commit()

    return answer, chunk_ids

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("question")
    ap.add_argument("--k", type=int, default=5)
    args = ap.parse_args()

    ans, ids = rag(args.question, args.k)
    print("\nAnswer:\n", ans)
    print("\nRetrieved chunk ids:", ids)

if __name__ == "__main__":
    main()
