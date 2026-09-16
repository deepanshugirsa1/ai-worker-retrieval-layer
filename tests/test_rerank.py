from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cache import LRUCache
from src.rerank import rerank


def test_rerank_promotes_lexical_match():
    docs = [
        {"doc_id": "a", "title": "unrelated", "body": "logistics warehouse", "score": 0.30},
        {"doc_id": "b", "title": "Acme", "body": "Acme AI SDR outreach", "score": 0.28},
    ]
    ranked = rerank("Acme AI SDR outreach", docs, alpha=0.5)
    assert ranked[0]["doc_id"] == "b"
    assert ranked[0]["rerank_score"] >= ranked[1]["rerank_score"]


def test_rerank_preserves_original_fields():
    docs = [{"doc_id": "a", "title": "t", "body": "b", "score": 0.5}]
    ranked = rerank("t b", docs)
    assert ranked[0]["doc_id"] == "a"
    assert "lexical_overlap" in ranked[0]


def test_lru_cache_hits_and_evicts():
    cache = LRUCache(capacity=2)
    calls = {"n": 0}

    def compute():
        calls["n"] += 1
        return [1.0]

    cache.get_or_compute("q1", compute)
    cache.get_or_compute("q1", compute)  # hit, no recompute
    assert calls["n"] == 1
    assert cache.stats()["hits"] == 1

    cache.get_or_compute("q2", compute)
    cache.get_or_compute("q3", compute)  # evicts q1
    cache.get_or_compute("q1", compute)  # recompute after eviction
    assert calls["n"] == 4
