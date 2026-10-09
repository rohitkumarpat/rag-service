from google import genai
from google.genai import types
from app.config import GEMINI_API_KEY, EMBED_MODEL, EMBED_DIM

client = genai.Client(api_key=GEMINI_API_KEY)


def _embed(texts: list[str], task_type: str) -> list[list[float]]:
    vectors = []
    for i in range(0, len(texts), 100):  # API batch limit
        res = client.models.embed_content(
            model=EMBED_MODEL,
            contents=texts[i : i + 100],
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=EMBED_DIM,
            ),
        )
        vectors.extend(e.values for e in res.embeddings)
    return vectors


def embed_documents(texts: list[str]) -> list[list[float]]:
    return _embed(texts, "RETRIEVAL_DOCUMENT")


def embed_query(text: str) -> list[float]:
    return _embed([text], "RETRIEVAL_QUERY")[0]