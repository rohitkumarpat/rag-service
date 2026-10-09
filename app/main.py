import secrets
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile

from app import db
from app.config import RAG_API_KEY
from app.ingest import ingest
from app.loaders import load_pdf, load_txt, load_url
from app.schemas import SearchIn, TextIn, UrlIn
from app.retriever import retrieve
from app.generator import generate
from app.schemas import GenerateIn, SearchIn, TextIn, UrlIn

MAX_FILE_BYTES = 10 * 1024 * 1024


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield
    db.close_db()


app = FastAPI(title="Brand Knowledge RAG Service", lifespan=lifespan)


def require_key(x_api_key: str = Header(...)):
    if not secrets.compare_digest(x_api_key, RAG_API_KEY):
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/health")
def health():
    with db.get_pool().connection() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok", "db": "connected"}


@app.post("/ingest/text", dependencies=[Depends(require_key)])
def ingest_text(body: TextIn):
    try:
        return ingest(body.clerk_id, body.title, "text", None, body.text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/ingest/url", dependencies=[Depends(require_key)])
def ingest_url(body: UrlIn):
    try:
        title, text = load_url(body.url)
        return ingest(body.clerk_id, title, "url", body.url, text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not fetch that URL")


@app.post("/ingest/file", dependencies=[Depends(require_key)])
def ingest_file(clerk_id: str = Form(...), file: UploadFile = File(...)):
    data = file.file.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")
    name = (file.filename or "").lower()
    try:
        if name.endswith(".pdf"):
            text = load_pdf(data)
        elif name.endswith((".txt", ".md")):
            text = load_txt(data)
        else:
            raise HTTPException(status_code=400, detail="Only PDF, TXT or MD files are supported")
        return ingest(clerk_id, file.filename, "file", file.filename, text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    

@app.post("/search", dependencies=[Depends(require_key)])
def search(body: SearchIn):
    return {"results": retrieve(body.clerk_id, body.query, body.k)}


@app.post("/generate", dependencies=[Depends(require_key)])
def generate_route(body: GenerateIn):
    try:
        return generate(
            body.clerk_id, body.template_prompt, body.user_input,
            body.use_knowledge, body.cite, body.k,
        )
    except Exception:
        raise HTTPException(status_code=502, detail="Generation failed, please try again")