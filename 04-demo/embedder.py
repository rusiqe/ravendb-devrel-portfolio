"""
Embedding helper — generates 384-dim bge-micro-v2 vectors via sentence-transformers.

The BAAI/bge-small-en model (384 dims) is the publicly available version of
the same bge-micro-v2 architecture RavenDB bundles internally.

Requires: sentence-transformers
"""

import base64
import struct
from functools import lru_cache

import numpy as np


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("BAAI/bge-small-en-v1.5")


def embed_text(text: str) -> np.ndarray:
    """Return a normalised 384-dim float32 embedding for *text*."""
    model = _get_model()
    emb = model.encode(text, normalize_embeddings=True)
    return emb.astype(np.float32)


def embed_to_base64(text: str) -> str:
    """Return a base64-encoded float32 embedding suitable for RavenDB vector fields."""
    emb = embed_text(text)
    raw = struct.pack(f"{len(emb)}f", *emb)
    return base64.b64encode(raw).decode()


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))
