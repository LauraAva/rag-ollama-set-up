from __future__ import annotations
import os, glob, json, argparse
from pathlib import Path
import psycopg
from pgvector.psycopg import register_vector, Vector
from ollama import embed

# --- IMPORTANT: allow "import raglib" when running scripts from /scripts ---
import sys
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from raglib.config import EMBED_MODEL  # noqa: E402


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list[str]:
    text = text.replace("\r\n", "\n")
    out = []
    i = 0
    step = max(1, chunk_size - overlap)
    while i < len(text):
        c = text[i:i + chunk_size].strip()
        if c:
            out.append(c)
        i += step
    return out


def get_vec(text: str) -> list[float]:
    r = embed(model=EMBED_MODEL, input=text)
    v = r["embeddings"][0] if isinstance(r["embeddings"][0], list) else r["embeddings"]
    return v


def ensure_collection(cur, name: str, sensitivity: int) -> int:
    cur.execute(
        """
        INSERT INTO rag_collections (name, sensitivity_level)
        VALUES (%s, %s)
        ON CONFLICT (name) DO UPDATE SET sensitivity_level = EXCLUDED.sensitivity_level
        RETURNING id
        """,
        (name, sensitivity),
    )
    return int(cur.fetchone()[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default="sample_docs", help="Folder with .txt/.md")
    ap.add_argument("--source", default="local", help="Source label")
    ap.add_argument("--collection", default=os.getenv("DEFAULT_COLLECTION", "public"))
    ap.add_argument("--sensitivity", type=int, default=0)
    ap.add_argument("--chunk-size", type=int, default=1200)
    ap.add_argument("--overlap", type=int, default=200)
    args = ap.parse_args()

    files = glob.glob(os.path.join(args.path, "**", "*.txt"), recursive=True) + \
            glob.glob(os.path.join(args.path, "**", "*.md"), recursive=True)

    if not files:
        raise SystemExit(f"No .txt/.md found under: {args.path}")

    with psycopg.connect("") as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            collection_id = ensure_collection(cur, args.collection, args.sensitivity)

            inserted = 0
            for f in files:
                txt = open(f, "r", encoding="utf-8", errors="ignore").read()
                chunks = chunk_text(txt, chunk_size=args.chunk_size, overlap=args.overlap)

                for idx, c in enumerate(chunks):
                    vec = get_vec(c)
                    meta = {"file": os.path.basename(f), "embed_model": EMBED_MODEL}
                    cur.execute(
                        """
                        INSERT INTO rag_chunks (source, chunk_index, content, metadata, embedding, collection_id)
                        VALUES (%s,%s,%s,%s,%s,%s)
                        """,
                        (args.source, idx, c, json.dumps(meta), Vector(vec), collection_id),
                    )
                    inserted += 1

            conn.commit()

    print(f"Ingested {len(files)} files / {inserted} chunks into rag_chunks (collection={args.collection}, source={args.source})")


if __name__ == "__main__":
    main()