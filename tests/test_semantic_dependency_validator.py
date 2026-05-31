from __future__ import annotations

from core.gencode.problem_type_spec import load_problem_type_spec
from core.gencode.validators import (
    validate_condition_target_dependency,
    validate_generator_payload,
)

SKILL_ID = "vh_數學B1_CartesianCoordinateSystemEstablishment"
PT = "short_answer_classify_quadrant_symbolic_condition_coordinate_point"


def _spec() -> dict:
    spec = load_problem_type_spec(SKILL_ID, PT, prefer="auto")
    if spec:
        return spec
    raise AssertionError("spec not found")


def test_symbolic_condition_with_numeric_target_fails():
    spec = _spec()
    payload = {
        "question_text": "若 $a<b<0$，且 $Q(12,-8)$，請判斷 $Q$ 位於哪一象限。",
        "answer_type": "short_answer",
        "choices": [],
        "answer": "第四象限",
        "problem_type_id": PT,
        "metadata": {
            "givens": [{"type": "symbolic_condition", "text": "a<b<0", "variables": ["a", "b"]}],
            "target": {
                "type": "coordinate_point",
                "label": "Q",
                "x_expr": "12",
                "y_expr": "-8",
                "variables": [],
            },
            "derivation": [],
        },
    }
    errors = validate_condition_target_dependency(payload, spec)
    assert "condition_unused_by_target" in errors
    all_errors = validate_generator_payload(payload, problem_type_spec=spec)
    assert "condition_unused_by_target" in all_errors


def test_symbolic_condition_with_symbolic_target_passes():
    spec = _spec()
    payload = {
        "question_text": "若 $a<b<0$，且 $Q(ab,a+b)$，請判斷 $Q$ 位於哪一象限。",
        "answer_type": "short_answer",
        "choices": [],
        "answer": "第四象限",
        "problem_type_id": PT,
        "metadata": {
            "givens": [{"type": "symbolic_condition", "text": "a<b<0", "variables": ["a", "b"]}],
            "target": {
                "type": "coordinate_point",
                "label": "Q",
                "x_expr": "ab",
                "y_expr": "a+b",
                "variables": ["a", "b"],
            },
            "derivation": ["a<0 且 b<0", "ab>0", "a+b<0", "所以 Q(ab,a+b) 在第四象限"],
        },
    }
    errors = validate_condition_target_dependency(payload, spec)
    assert "condition_unused_by_target" not in errors
