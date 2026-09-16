from __future__ import annotations

"""Pluggable embedding providers.

The retrieval layer talks to embeddings through a small interface so the demo
runs fully offline with a deterministic hashing embedder, while production can
swap in a hosted model (OpenAI, Cohere, a local sentence-transformer, etc.)
without touching indexing or retrieval code.
"""

import os
from typing import Protocol, runtime_checkable

from src.embeddings import embed as _hash_embed


@runtime_checkable
class EmbeddingProvider(Protocol):
    name: str
    dim: int

    def embed(self, text: str) -> list[float]:
        ...


class HashingEmbeddingProvider:
    """Deterministic, dependency-free embedder for offline demos and tests."""

    name = "hashing"

    def __init__(self, dim: int = 64) -> None:
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        return _hash_embed(text, dim=self.dim)


class HostedEmbeddingProvider:
    """Placeholder for a hosted embedding API.

    Intentionally not wired to a network call. It raises a clear error unless an
    API key is present, so production wiring is an explicit, reviewable change
    rather than an accidental live dependency in CI.
    """

    name = "hosted"

    def __init__(self, dim: int = 1536, model: str = "text-embedding-3-small") -> None:
        self.dim = dim
        self.model = model

    def embed(self, text: str) -> list[float]:  # pragma: no cover - not used offline
        if not os.getenv("EMBEDDINGS_API_KEY"):
            raise RuntimeError(
                "HostedEmbeddingProvider requires EMBEDDINGS_API_KEY. "
                "Use HashingEmbeddingProvider for offline runs."
            )
        raise NotImplementedError(
            "Wire your embedding client here (kept out of the offline demo)."
        )


def get_embedding_provider(dim: int = 64) -> EmbeddingProvider:
    """Select a provider from the EMBEDDINGS_PROVIDER env var (default: hashing)."""
    choice = os.getenv("EMBEDDINGS_PROVIDER", "hashing").lower()
    if choice == "hosted":
        return HostedEmbeddingProvider()
    return HashingEmbeddingProvider(dim=dim)
