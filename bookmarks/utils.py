"""
Utility functions for SmartBookmarks.

• Text extraction  (PDF, DOCX, plain text, URL)
• Embedding        (Sentence-Transformers)
• Auto-tagging     (zero-shot, transformers)
• Vector search    (FAISS index + JSON map)
"""

from __future__ import annotations

import json, os, re
from pathlib import Path
from typing import Iterable, List

from django.conf import settings
from .models import Bookmark, Tag

# ────────────────────────────────────────────────────────────
# 0. Paths for the vector store
# ────────────────────────────────────────────────────────────
BASE_DATA_DIR   = Path(getattr(settings, "BASE_DATA_DIR", settings.BASE_DIR))
VECTOR_MAP_FILE = getattr(settings, "VECTOR_MAP_FILE", BASE_DATA_DIR / "vector_map.json")
FAISS_INDEX_FILE = getattr(settings, "FAISS_INDEX_FILE", BASE_DATA_DIR / "faiss.index")


# ────────────────────────────────────────────────────────────
# 1.  Text extraction
# ────────────────────────────────────────────────────────────
def extract_text_from_file(file_path: str) -> str:
    """Return text from PDF, DOCX, or plain-text file."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        try:
            from pdfminer.high_level import extract_text
            return extract_text(file_path)
        except ImportError as exc:
            raise RuntimeError("Install pdfminer.six for PDF support") from exc

    if ext in {".docx", ".doc"}:
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)
        except ImportError as exc:
            raise RuntimeError("Install python-docx for Word support") from exc

    # fallback: treat as UTF-8 text
    with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
        return fp.read()


def extract_text_from_url(url: str) -> str:
    try:
        import requests
    except ImportError as exc:
        raise RuntimeError("Install requests for URL fetching") from exc

    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return re.sub("<[^<]+?>", "", r.text)          # naive HTML strip


# ────────────────────────────────────────────────────────────
# 2.  Embeddings
# ────────────────────────────────────────────────────────────
def generate_embedding(text: str) -> List[float]:
    """Return a 384-D MiniLM vector."""
    from sentence_transformers import SentenceTransformer
    if not hasattr(generate_embedding, "_model"):
        generate_embedding._model = SentenceTransformer("all-MiniLM-L6-v2")
    return generate_embedding._model.encode(text, convert_to_numpy=True).tolist()


# ────────────────────────────────────────────────────────────
# 3.  Auto-tagging
# ────────────────────────────────────────────────────────────
def auto_tag(text: str,
             candidate_labels: Iterable[str] | None = None,
             threshold: float = 0.3) -> List[str]:
    from transformers import pipeline
    if candidate_labels is None:
        candidate_labels = [
            "natural language processing", "machine learning", "deep learning",
            "computer vision", "data science", "ai", "tutorial", "paper",
            "web development", "python", "chat log", "research",
        ]
    if not hasattr(auto_tag, "_clf"):
        auto_tag._clf = pipeline("zero-shot-classification",
                                 model="facebook/bart-large-mnli")
    res = auto_tag._clf(text, list(candidate_labels))
    return [lbl for lbl, scr in zip(res["labels"], res["scores"]) if scr >= threshold]


# ────────────────────────────────────────────────────────────
# 4.  FAISS helpers
# ────────────────────────────────────────────────────────────
def _load_faiss():
    import faiss
    vec_map = {}
    if VECTOR_MAP_FILE.exists():
        with open(VECTOR_MAP_FILE, "r", encoding="utf-8") as fp:
            vec_map = json.load(fp)
    index = faiss.read_index(str(FAISS_INDEX_FILE)) if FAISS_INDEX_FILE.exists() else None
    return index, vec_map


def _save_faiss(index, vec_map):
    import faiss
    FAISS_INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    VECTOR_MAP_FILE.parent.mkdir(parents=True, exist_ok=True)
    if index is not None:
        faiss.write_index(index, str(FAISS_INDEX_FILE))
    with open(VECTOR_MAP_FILE, "w", encoding="utf-8") as fp:
        json.dump(vec_map, fp)


def add_embedding_to_index(bookmark_id: int, emb: List[float]) -> None:
    import faiss, numpy as np
    index, vec_map = _load_faiss()
    vec = np.asarray([emb], dtype="float32")
    if index is None:
        index = faiss.IndexFlatL2(vec.shape[1])
    pos = index.ntotal
    index.add(vec)
    vec_map[str(pos)] = bookmark_id
    _save_faiss(index, vec_map)


def search_embeddings(query_vec: List[float], k: int = 10) -> List[int]:
    import faiss, numpy as np
    index, vec_map = _load_faiss()
    if index is None or index.ntotal == 0:
        return []
    q = np.asarray([query_vec], dtype="float32")
    _, idxs = index.search(q, min(k, index.ntotal))
    return [int(vec_map[str(i)]) for i in idxs[0] if str(i) in vec_map]


# ────────────────────────────────────────────────────────────
# 5.  Process one Bookmark
# ────────────────────────────────────────────────────────────
# 5. Process one Bookmark
def process_bookmark(bookmark: Bookmark) -> None:
    """Extract text from URL + all attached files, then embed/tag/index."""
    chunks: list[str] = []

    # URLs: Access the related BookmarkLink model for URLs
    for link in bookmark.links.all():
        try:
            chunks.append(extract_text_from_url(link.url))  # Extract text from each URL in BookmarkLink
        except Exception as exc:
            print("URL extraction failed:", exc)

    # Attached files
    for bf in bookmark.files.all():
        try:
            chunks.append(extract_text_from_file(bf.file.path))
        except Exception as exc:
            print("File extraction failed:", exc)

    full_text = "\n".join(chunks).strip()
    bookmark.text = full_text

    # Embedding
    if full_text:
        try:
            bookmark.embedding = generate_embedding(full_text)
        except Exception as exc:
            bookmark.embedding = None
            print("Embedding failed:", exc)

    bookmark.save()

    # Auto-tag
    if full_text:
        try:
            for lbl in auto_tag(full_text):
                tag, _ = Tag.objects.get_or_create(name=lbl)
                bookmark.tags.add(tag)
        except Exception as exc:
            print("Auto-tagging failed:", exc)

    # FAISS
    if bookmark.embedding:
        try:
            add_embedding_to_index(bookmark.id, bookmark.embedding)
        except Exception as exc:
            print("FAISS update failed:", exc)
