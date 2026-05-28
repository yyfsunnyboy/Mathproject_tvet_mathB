from __future__ import annotations

from core.gencode.runtime_smoke import _run_negative_semantic_smoke, _validate_runtime_payload
from core.gencode.problem_type_spec import load_problem_type_spec
from core.gencode.validators import validate_generator_payload

SKILL_ID = "vh_數學B1_CartesianCoordinateSystemEstablishment"
PT = "short_answer_classify_quadrant_symbolic_condition_coordinate_point"


def _spec() -> dict:
    spec = load_problem_type_spec(SKILL_ID, PT, prefer="auto")
    if spec:
        return spec
    raise AssertionError("induced spec missing")


def test_negative_payload_blocked_by_validator():
    spec = _spec()
    payload = {
        "skill_id": SKILL_ID,
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
    errors = validate_generator_payload(payload, problem_type_spec=spec)
    assert "condition_unused_by_target" in errors
    blockers = _validate_runtime_payload(payload, SKILL_ID)
    assert "condition_unused_by_target" in blockers


def test_negative_semantic_smoke_gate():
    assert _run_negative_semantic_smoke(SKILL_ID) == []
