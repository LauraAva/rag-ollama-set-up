from .db import connect

def log_feedback(qa_id: int, rating: int, comment: str = "", user_id: str = None):
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO rag_feedback (qa_id, user_id, rating, comment) VALUES (%s,%s,%s,%s)",
            (qa_id, user_id, rating, comment),
        )
        conn.commit()