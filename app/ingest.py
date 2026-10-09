from pgvector import Vector
from app.chunker import chunk_text
from app.embeddings import embed_documents
from app.db import get_pool


def ingest(clerk_id: str, title: str, source_type: str, source_ref: str | None, text: str) -> dict:
    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("No readable text found in this source")
    vectors = embed_documents(chunks)

    with get_pool().connection() as conn:
        with conn.transaction():
            doc_id = conn.execute(
                "INSERT INTO knowledge_docs (clerk_id, title, source_type, source_ref) "
                "VALUES (%s, %s, %s, %s) RETURNING id",
                (clerk_id, title, source_type, source_ref),
            ).fetchone()[0]
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO knowledge_chunks (doc_id, clerk_id, chunk_index, content, embedding) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    [(doc_id, clerk_id, i, c, Vector(v)) for i, (c, v) in enumerate(zip(chunks, vectors))],
                )
    return {"doc_id": doc_id, "chunks": len(chunks)}