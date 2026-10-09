import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]
RAG_API_KEY = os.environ["RAG_API_KEY"]

EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 768
GEN_MODEL = "gemini-2.5-flash"