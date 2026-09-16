from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval.grounding_eval import evaluate, load_cases


def _ensure_seeded():
    from data.seed_knowledge import DOCS
    from src.lake import connect, init_schema

    con = connect()
    init_schema(con)
    n = con.execute("SELECT count(*) FROM knowledge_docs").fetchone()[0]
    if n != len(DOCS):
        from data.seed_knowledge import main as seed

        seed()


def test_eval_meets_baseline():
    _ensure_seeded()
    report = evaluate()
    assert report["cases"] == 50
    assert report["top1_accuracy"] >= 0.90
    assert report["recall_at_3"] >= 0.98
    assert report["mean_reciprocal_rank"] >= 0.94
    assert report["avg_supported_ratio"] >= 0.6
    assert report["grounding_match_rate"] >= 0.95
    assert report["regression_passed"] is True
    assert all(gate["passed"] for gate in report["gates"].values())


def test_gold_set_expands_to_unique_queries():
    cases = load_cases()
    queries = [case["query"] for case in cases]
    assert len(cases) == 50
    assert len(set(queries)) == 50
    assert len({case["expected_account_id"] for case in cases}) == 10


def test_report_includes_case_level_audit_details():
    _ensure_seeded()
    report = evaluate()
    assert len(report["details"]) == report["cases"]
    assert {
        "query",
        "expected_account_id",
        "top_account_id",
        "expected_rank",
        "top1",
        "recalled_at_3",
        "supported_ratio",
        "grounded",
    } <= report["details"][0].keys()
