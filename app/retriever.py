from pgvector import Vector
from app.db import get_pool
from app.embeddings import embed_query


def retrieve(clerk_id: str, query: str, k: int = 5, min_score: float = 0.35) -> list[dict]:
    qvec = Vector(embed_query(query))
    with get_pool().connection() as conn:
        with conn.transaction():
            # widen the HNSW search so the per-user filter still returns k rows
            conn.execute("SET LOCAL hnsw.ef_search = 100")
            rows = conn.execute(
                """
                SELECT c.content, c.chunk_index, d.id, d.title,
                       1 - (c.embedding <=> %s) AS score
                FROM knowledge_chunks c
                JOIN knowledge_docs d ON d.id = c.doc_id
                WHERE c.clerk_id = %s
                ORDER BY c.embedding <=> %s
                LIMIT %s
                """,
                (qvec, clerk_id, qvec, k),
            ).fetchall()

    return [
        {
            "content": r[0],
            "chunk_index": r[1],
            "doc_id": r[2],
            "title": r[3],
            "score": round(float(r[4]), 4),
        }
        for r in rows
        if r[4] >= min_score
    ]