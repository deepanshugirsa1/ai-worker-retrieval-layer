from __future__ import annotations

import hashlib
import math
import re

import numpy as np


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def embed(text: str, dim: int = 64) -> list[float]:
    """Deterministic hashing embedder for demos (no model download required)."""
    vec = np.zeros(dim, dtype=np.float64)
    for tok in tokenize(text):
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if (h >> 8) % 2 == 0 else -1.0
        vec[idx] += sign
    norm = math.sqrt(float(np.dot(vec, vec))) or 1.0
    vec = vec / norm
    return vec.astype(float).tolist()


def cosine(a: list[float], b: list[float]) -> float:
    va = np.asarray(a, dtype=np.float64)
    vb = np.asarray(b, dtype=np.float64)
    denom = (np.linalg.norm(va) * np.linalg.norm(vb)) or 1.0
    return float(np.dot(va, vb) / denom)
