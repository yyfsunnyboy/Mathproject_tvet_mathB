from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CASES = [
    ("absolute_value_inequality_zero_center_basic", "interval_set"),
    ("absolute_value_inequality_shifted_basic", "interval_set"),
    ("absolute_value_inequality_linear_expression_basic", "interval_set"),
    ("absolute_value_inequality_integer_solution_count_choice", "choice_label"),
]


def _load_candidate(problem_type_id: str):
    path = PROJECT_ROOT / "generated_candidates" / "vocational_math_b1" / "section_1_1" / problem_type_id / "candidate_v1.py"
    assert path.exists(), f"candidate file missing: {path}"
    spec = importlib.util.spec_from_file_location(f"cand_{problem_type_id}", str(path))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_candidates_basic_contract_and_check() -> None:
    for pt, answer_type in CASES:
        mod = _load_candidate(pt)
        item = mod.generate(level=1)
        assert isinstance(item, dict)
        assert item.get("skill_id") == "vh_數學B1_AbsoluteValueInequality"
        assert item.get("problem_type_id") == pt
        assert "answer_contract" in item
        if answer_type == "interval_set":
            assert mod.check(item["correct_answer"], item["correct_answer"]).get("correct") is True
            assert mod.check("x>9999", item["correct_answer"]).get("correct") is False
        else:
            choices = item.get("choices", [])
            assert len(choices) == 4
            assert len(set(choices)) == 4
            assert item.get("answer") in {"A", "B", "C", "D"}
            assert mod.check(item["answer"], item["answer"], choices).get("correct") is True


def test_candidates_generate_10_samples_no_crash() -> None:
    for pt, _ in CASES:
        mod = _load_candidate(pt)
        for i in range(10):
            item = mod.generate(level=1, seed=i)
            assert isinstance(item, dict)


def test_choice_label_distribution_and_integrity() -> None:
    mod = _load_candidate("absolute_value_inequality_integer_solution_count_choice")
    labels = set()
    for i in range(100):
        item = mod.generate(level=1, seed=i)
        choices = item.get("choices", [])
        assert len(choices) == 4
        assert len(set(choices)) == 4
        label = item.get("answer")
        assert label in {"A", "B", "C", "D"}
        labels.add(label)
        assert mod.check(label, item.get("correct_answer"), choices).get("correct") is True
        wrong = "A" if label != "A" else "B"
        assert mod.check(wrong, item.get("correct_answer"), choices).get("correct") is False
    assert len(labels) >= 2
