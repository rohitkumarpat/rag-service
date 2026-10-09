from contextlib import asynccontextmanager
from fastapi import FastAPI
from app import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield
    db.close_db()


app = FastAPI(title="Brand Knowledge RAG Service", lifespan=lifespan)


@app.get("/health")
def health():
    with db.get_pool().connection() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok", "db": "connected"}