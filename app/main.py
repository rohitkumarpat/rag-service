from fastapi import FastAPI
from app import config

app = FastAPI(title="Brand Knowledge RAG Service")


@app.get("/health")
def health():
    return {"status": "ok"}