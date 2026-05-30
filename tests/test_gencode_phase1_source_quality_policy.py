from __future__ import annotations

from core.gencode.example_feature_extractor import extract_example_feature_rule_only
from core.gencode.problem_type_induction import induce_problem_types_from_examples


def _ex(ex_id: int, stem: str, answer: str = "1", skill_id: str = "vh_mock_skill") -> dict:
    return {
        "id": ex_id,
        "example_id": ex_id,
        "skill_id": skill_id,
        "problem_text": stem,
        "correct_answer": answer,
    }


def test_source_quality_reject_detects_broken_latex():
    feat = extract_example_feature_rule_only(_ex(1, r"求值：\frac 1 2 + 3"))
    assert feat["source_quality_reject"] is True
    assert "broken_latex_fraction" in (feat.get("source_quality_issues") or [])


def test_source_quality_reject_reported_in_phase1_output():
    examples = [
        _ex(1, r"求值：\frac 1 2 + 3"),
        _ex(2, "求 A(1,2)、B(3,4) 的中點坐標。", "(2,3)"),
    ]
    out = induce_problem_types_from_examples("vh_mock_Midpoint", examples, spec_mode="rule_first_induce_from_sources")
    assert isinstance(out.get("rejected_source_examples"), list)
    assert any(int(x.get("example_id", 0)) == 1 for x in out.get("rejected_source_examples") or [])
    assert isinstance(out.get("source_quality_issues"), list)
