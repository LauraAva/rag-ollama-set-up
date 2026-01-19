import os, glob, json
import psycopg
from pgvector.psycopg import register_vector, Vector
from ollama import embed

EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")

def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200):
    text = text.replace("\r\n", "\n")
    out = []
    i = 0
    step = max(1, chunk_size - overlap)
    while i < len(text):
        c = text[i:i+chunk_size].strip()
        if c:
            out.append(c)
        i += step
    return out

def get_vec(text: str):
    r = embed(model=EMBED_MODEL, input=text)
    v = r["embeddings"][0] if isinstance(r["embeddings"][0], list) else r["embeddings"]
    return v

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default="docs", help="Folder with .txt/.md")
    ap.add_argument("--source", default="local", help="Source label")
    args = ap.parse_args()

    files = glob.glob(os.path.join(args.path, "**", "*.txt"), recursive=True) + \
            glob.glob(os.path.join(args.path, "**", "*.md"), recursive=True)
    if not files:
        raise SystemExit(f"No .txt/.md found under: {args.path}")

    with psycopg.connect("") as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            for f in files:
                txt = open(f, "r", encoding="utf-8", errors="ignore").read()
                chunks = chunk_text(txt)
                for idx, c in enumerate(chunks):
                    vec = get_vec(c)
                    meta = {"file": os.path.basename(f), "path": os.path.abspath(f)}
                    cur.execute(
                        "INSERT INTO rag_chunks (source, chunk_index, content, metadata, embedding) VALUES (%s,%s,%s,%s,%s)",
                        (args.source, idx, c, json.dumps(meta), Vector(vec)),
                    )
            conn.commit()

    print(f"Ingested {len(files)} files into rag_chunks (source={args.source})")

if __name__ == "__main__":
    main()
