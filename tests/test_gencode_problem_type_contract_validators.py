from __future__ import annotations

from core.gencode.problem_type_spec import load_problem_type_spec
from core.gencode.validators import validate_answer_contract, validate_generator_payload, validate_semantic_and_dependency


def test_single_choice_rejects_embedded_choices_in_stem():
    spec = load_problem_type_spec(
        "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "coordinate_quadrant_single_choice",
    )
    assert spec is not None
    payload = {
        "question_text": "題幹\n(A) 第一象限",
        "answer": "A",
        "choices": [{"label": "A", "text": "第一象限"}, {"label": "B", "text": "第二象限"}, {"label": "C", "text": "第三象限"}, {"label": "D", "text": "第四象限"}],
        "metadata": {"givens": ["x=1"], "target": "第一象限", "derivation": ["x=1>0"]},
    }
    assert "choices_embedded_in_question_text" in validate_answer_contract(payload, spec)


def test_short_answer_rejects_choice_label_answer():
    spec = load_problem_type_spec(
        "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "coordinate_quadrant_short_answer",
    )
    assert spec is not None
    payload = {
        "question_text": "點在第幾象限？",
        "answer": "A",
        "choices": [],
        "metadata": {"givens": ["x=1", "y=2"], "target": "第一象限", "derivation": ["x=1", "y=2"]},
    }
    assert "short_answer_must_not_be_choice_label" in validate_answer_contract(payload, spec)


def test_dependency_condition_unused_by_target():
    spec = load_problem_type_spec(
        "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "symbolic_expression_quadrant_short_answer",
    )
    assert spec is not None
    payload = {
        "question_text": "題幹",
        "answer": "第四象限",
        "choices": [],
        "metadata": {"givens": ["a<b<0"], "target": "7", "derivation": ["固定數字"]},
    }
    assert "condition_unused_by_target" in validate_semantic_and_dependency(payload, spec)


def test_validate_generator_payload_merges_errors():
    spec = load_problem_type_spec(
        "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "coordinate_quadrant_single_choice",
    )
    assert spec is not None
    payload = {
        "question_text": "(A) opt",
        "answer": "Z",
        "choices": ["第一象限"],
        "metadata": {"givens": [], "target": "", "derivation": []},
    }
    errors = validate_generator_payload(payload, problem_type_spec=spec)
    assert errors
