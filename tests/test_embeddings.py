from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.embeddings import cosine, embed


def test_embed_stable():
    a = embed("Acme SaaS lead")
    b = embed("Acme SaaS lead")
    assert a == b
    assert abs(cosine(a, b) - 1.0) < 1e-6


def test_similar_docs_rank_higher():
    q = embed("Acme AI SDR outreach")
    acme = embed("Acme is a SaaS lead interested in AI SDR outreach")
    other = embed("Unrelated manufacturing logistics warehouse")
    assert cosine(q, acme) > cosine(q, other)
