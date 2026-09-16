from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval.grounding_eval import evaluate


def _ensure_seeded():
    from src.lake import connect, init_schema

    con = connect()
    init_schema(con)
    n = con.execute("SELECT count(*) FROM knowledge_docs").fetchone()[0]
    if n == 0:
        from data.seed_knowledge import main as seed

        seed()


def test_eval_meets_baseline():
    _ensure_seeded()
    report = evaluate()
    assert report["cases"] >= 3
    # Deterministic hashing embedder should retrieve and support the gold set.
    assert report["top1_accuracy"] >= 0.66
    assert report["avg_supported_ratio"] >= 0.6
    assert report["grounding_match_rate"] >= 0.66
