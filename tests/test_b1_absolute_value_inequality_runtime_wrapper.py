from __future__ import annotations

import importlib


def test_runtime_wrapper_basic() -> None:
    mod = importlib.import_module("skills.vh_數學B1_AbsoluteValueInequality")
    q = mod.generate(level=1)
    assert isinstance(q, dict)
    assert q["skill_id"] == "vh_數學B1_AbsoluteValueInequality"
    assert "answer_contract" in q


def test_runtime_wrapper_coverage_and_checks() -> None:
    mod = importlib.import_module("skills.vh_數學B1_AbsoluteValueInequality")
    verified = {
        "absolute_value_inequality_zero_center_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_integer_solution_count_choice",
    }
    observed = set()
    choice_labels = []
    for i in range(100):
        q = mod.generate(level=1, seed=i)
        pt = q.get("problem_type_id")
        assert pt in verified
        assert pt != "absolute_value_inequality_malformed_source_review"
        observed.add(pt)
        eq = ((q.get("answer_contract") or {}).get("equivalence_type") or "").strip()
        if eq == "interval_set":
            ok = mod.check(q["correct_answer"], q["correct_answer"], current_question=q)
            bad = mod.check("x>9999", q["correct_answer"], current_question=q)
            assert bool(ok.get("correct")) is True
            assert bool(bad.get("correct")) is False
        elif eq == "choice_label":
            ok = mod.check(q["answer"], q["answer"], current_question=q)
            bad = mod.check("Z", q["answer"], current_question=q)
            assert bool(ok.get("correct")) is True
            assert bool(bad.get("correct")) is False
            choice_labels.append(q["answer"])
    assert observed == verified
    if len(choice_labels) >= 20:
        assert len(set(choice_labels)) >= 2
