import psycopg
from psycopg_pool import ConnectionPool
from pgvector.psycopg import register_vector
from app.config import DATABASE_URL, EMBED_DIM

pool: ConnectionPool | None = None

SCHEMA = f"""
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS knowledge_docs (
    id SERIAL PRIMARY KEY,
    clerk_id TEXT NOT NULL,
    title TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_ref TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_docs_clerk
    ON knowledge_docs (clerk_id);

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id SERIAL PRIMARY KEY,
    doc_id INT NOT NULL REFERENCES knowledge_docs(id) ON DELETE CASCADE,
    clerk_id TEXT NOT NULL,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    embedding vector({EMBED_DIM}) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_chunks_clerk
    ON knowledge_chunks (clerk_id);

CREATE INDEX IF NOT EXISTS idx_chunks_embedding
    ON knowledge_chunks USING hnsw (embedding vector_cosine_ops);
"""


def _configure(conn):
    register_vector(conn)


def init_db():
    global pool

    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        conn.execute(SCHEMA)

    pool = ConnectionPool(
        DATABASE_URL,
        configure=_configure,
        kwargs={"prepare_threshold": None},
        min_size=1,
        max_size=5,
        open=True,
    )


def close_db():
    if pool:
        pool.close()


def get_pool() -> ConnectionPool:
    assert pool is not None, "DB not initialised"
    return pool