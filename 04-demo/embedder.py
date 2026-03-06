"""
Embedding helper — generates 384-dim vectors using the bge-micro-v2 model
bundled inside RavenDB's own Server/LocalEmbeddings directory.

This reuses the exact same model RavenDB uses internally, so vectors stored
in documents are directly compatible with any static vector index you define.

Requires: onnxruntime, transformers (tokenizer only — no PyTorch needed)
"""

import base64
import struct
from functools import lru_cache
from pathlib import Path
from typing import Union

import numpy as np

# ─── Model paths ─────────────────────────────────────────────────────────────
# Look for the model bundled with RavenDB first, then fall back to a local copy
_SEARCH_PATHS = [
    # Relative to this file — works when running from 04-demo/
    Path(__file__).parent.parent.parent / "ravendb-server" / "Server" / "LocalEmbeddings" / "bge-micro-v2",
    # Absolute — used when running from a different working directory
    Path("/sessions/eloquent-zealous-maxwell/ravendb-server/Server/LocalEmbeddings/bge-micro-v2"),
]


def _find_model_dir() -> Path:
    for path in _SEARCH_PATHS:
        if (path / "model.onnx").exists():
            return path
    raise FileNotFoundError(
        "bge-micro-v2 model not found. Expected at:\n"
        + "\n".join(str(p) for p in _SEARCH_PATHS)
    )


# ─── Lazy-load the tokenizer and ONNX session ────────────────────────────────
@lru_cache(maxsize=1)
def _get_session_and_tokenizer():
    import onnxruntime as ort
    from transformers import AutoTokenizer

    model_dir = _find_model_dir()
    session = ort.InferenceSession(
        str(model_dir / "model.onnx"),
        providers=["CPUExecutionProvider"],
    )
    # bge-micro-v2 uses the same WordPiece tokenizer as BGE-small
    tokenizer = AutoTokenizer.from_pretrained(
        "BAAI/bge-small-en",
        local_files_only=False,
    )
    return session, tokenizer


# ─── Public API ──────────────────────────────────────────────────────────────

def embed_text(text: str) -> np.ndarray:
    """Return a normalised 384-dim float32 embedding for *text*."""
    session, tokenizer = _get_session_and_tokenizer()

    enc = tokenizer(
        text,
        padding="max_length",
        truncation=True,
        max_length=128,
        return_tensors="np",
    )

    output = session.run(
        None,
        {
            "input_ids": enc["input_ids"].astype(np.int64),
            "attention_mask": enc["attention_mask"].astype(np.int64),
            "token_type_ids": enc["token_type_ids"].astype(np.int64),
        },
    )

    hidden = output[0][0]  # (seq_len, 384)
    mask = enc["attention_mask"][0][: hidden.shape[0]]
    emb = (hidden * mask[:, np.newaxis]).sum(0) / mask.sum()
    emb = emb / np.linalg.norm(emb)
    return emb.astype(np.float32)


def embed_to_base64(text: str) -> str:
    """Return a base64-encoded float32 embedding suitable for RavenDB vector fields."""
    emb = embed_text(text)
    raw = struct.pack(f"{len(emb)}f", *emb)
    return base64.b64encode(raw).decode()


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))
