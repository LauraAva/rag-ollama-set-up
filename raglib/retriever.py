from typing import List, Tuple, Optional
from .db import connect

# Returns rows: (id, content, distance)
def retrieve(qvec, k: int, collection_id: Optional[int] = None) -> List[Tuple[int, str, float]]:
    sql = """
      SELECT id, content, (embedding <=> %s) AS distance
      FROM rag_chunks
      WHERE (%s::bigint IS NULL OR collection_id = %s)
      ORDER BY embedding <=> %s
      LIMIT %s
    """
    with connect() as conn, conn.cursor() as cur:
        cur.execute(sql, (qvec, collection_id, collection_id, qvec, k))
        return cur.fetchall()