from __future__ import annotations

import importlib

from core.checkers.solution_set_checker import check_solution_set_answer
from core.gencode.answer_payload import is_valid_answer_payload, validate_generated_answer_shape
from core.gencode.runtime_smoke import run_draft_runtime_smoke
from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.validators import validate_answer_contract, validate_generator_payload
from core.gencode.validators.answer_contract_validator import CHOICE_EMBEDDED_PATTERN


def _solution_set_spec() -> dict:
    return {
        "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance",
        "answer_contract": {
            "answer_type": "solution_set",
            "answer_shape": "unordered_set",
            "answer_equivalence": "unordered_solution_set",
            "checker": "solution_set_checker",
        },
        "stem_contract": {"stem_must_not_embed_choices": True},
    }


def test_solution_set_list_valid_not_invalid_answer_type():
    spec = _solution_set_spec()
    payload = {
        "question_text": "求 k 的可能值。",
        "answer": [-3, 7],
        "correct_answer": [-3, 7],
        "choices": [],
        "metadata": {"givens": [], "target": "k", "derivation": []},
    }
    errors = validate_answer_contract(payload, spec)
    assert not any("invalid_answer_type" in e for e in errors), errors


def test_solution_set_brace_string_valid():
    spec = _solution_set_spec()
    payload = {
        "question_text": "求 k 的可能值。",
        "answer": "{-3,7}",
        "choices": [],
        "metadata": {"givens": [], "target": "k", "derivation": []},
    }
    errors = validate_answer_contract(payload, spec)
    assert not any("invalid_answer_type" in e for e in errors), errors


def test_solution_set_checker_order_insensitive():
    ca = [-3, 7]
    assert check_solution_set_answer("-3,7", ca)
    assert check_solution_set_answer("7,-3", ca)
    assert check_solution_set_answer("-3 或 7", ca)
    assert check_solution_set_answer("k=-3 或 k=7", ca)
    assert not check_solution_set_answer("7", ca)


def test_numeric_or_radical_and_interval_validate_generated_shape():
    radical_ac = {
        "answer_type": "numeric_or_radical",
        "checker": "expression_equivalence_checker",
        "answer_equivalence": "math_expression_equivalence",
    }
    ok, blockers, _ = validate_generated_answer_shape(
        {"answer": "2\\sqrt{5}", "correct_answer": "2\\sqrt{5}", "problem_type_id": "pt"},
        answer_contract=radical_ac,
    )
    assert ok and not blockers

    interval_ac = {
        "answer_type": "interval",
        "checker": "interval_checker",
        "answer_equivalence": "interval_set",
    }
    ok2, blockers2, _ = validate_generated_answer_shape(
        {"answer": "-4 <= x <= 0", "correct_answer": "-4 <= x <= 0", "problem_type_id": "pt"},
        answer_contract=interval_ac,
    )
    assert ok2 and not blockers2


def test_phase3_distance_draft_runtime_smoke_passes():
    skill_id = "vh_數學B1_DistanceBetweenTwoPointsInPlane"
    draft = f"reports/gencode_closed_loop/drafts/{skill_id}.py"
    result = run_draft_runtime_smoke(skill_id, draft, sample_count=30)
    assert result.get("status") == "passed", result
    assert result.get("interface_check", {}).get("generate_returns_dict") is True


def test_check_answer_routes_solution_set_via_payload():
    payload = {
        "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance",
        "answer_contract": _solution_set_spec()["answer_contract"],
        "checker": "solution_set_checker",
    }
    ca = [-3, 7]
    assert check_answer("7,-3", ca, payload=payload)
    assert not check_answer("7", ca, payload=payload)


def test_mixed_skill_packaging_contracts():
    numeric_spec = {
        "problem_type_id": "short_answer_compute_two_point_distance",
        "answer_contract": {
            "answer_type": "numeric_or_radical",
            "answer_equivalence": "math_expression_equivalence",
            "checker": "expression_equivalence_checker",
        },
        "stem_contract": {"stem_must_not_embed_choices": True},
    }
    set_spec = _solution_set_spec()
    set_payload = {
        "question_text": "求 k。",
        "answer": [-3, 7],
        "choices": [],
        "metadata": {"givens": [], "target": "k", "derivation": []},
    }
    num_payload = {
        "question_text": "求距離。",
        "answer": "2\\sqrt{5}",
        "choices": [],
        "metadata": {"givens": [], "target": "d", "derivation": []},
    }
    assert not validate_answer_contract(set_payload, set_spec)
    assert not validate_answer_contract(num_payload, numeric_spec)


def test_regression_choice_and_short_answer_rules():
    from core.gencode.problem_type_spec import load_problem_type_spec

    spec = load_problem_type_spec(
        "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "coordinate_quadrant_single_choice",
    )
    assert spec is not None
    payload = {
        "question_text": "題幹\n(A) 第一象限",
        "answer": "A",
        "choices": [
            {"label": "A", "text": "第一象限"},
            {"label": "B", "text": "第二象限"},
            {"label": "C", "text": "第三象限"},
            {"label": "D", "text": "第四象限"},
        ],
        "metadata": {"givens": ["x=1"], "target": "第一象限", "derivation": ["x=1>0"]},
    }
    assert "choices_embedded_in_question_text" in validate_answer_contract(payload, spec)

    spec2 = load_problem_type_spec(
        "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "coordinate_quadrant_short_answer",
    )
    assert spec2 is not None
    payload2 = {
        "question_text": "點在第幾象限？",
        "answer": "A",
        "choices": [],
        "metadata": {"givens": ["x=1", "y=2"], "target": "第一象限", "derivation": ["x=1", "y=2"]},
    }
    assert "short_answer_must_not_be_choice_label" in validate_answer_contract(payload2, spec2)


def test_cartesian_thin_wrapper_still_contract_safe():
    skill_id = "vh_數學B1_CartesianCoordinateSystemEstablishment"
    mod = importlib.import_module(f"skills.{skill_id}")
    for i in range(10):
        payload = mod.generate(level=1, seed=i)
        pt = str(payload.get("problem_type_id", "")).strip()
        from core.gencode.problem_type_spec import load_problem_type_spec

        spec = load_problem_type_spec(skill_id, pt, prefer="auto")
        assert spec is not None
        errors = validate_generator_payload(payload, problem_type_spec=spec)
        assert not errors, errors
        if str(payload.get("answer_type")) == "short_answer":
            assert not payload.get("choices")
        if str(payload.get("answer_type")) == "single_choice":
            texts = [str(c.get("text", c) if isinstance(c, dict) else c) for c in (payload.get("choices") or [])]
            assert len(texts) == len(set(texts))
            assert not CHOICE_EMBEDDED_PATTERN.search(str(payload.get("question_text", "")))


def test_is_valid_answer_payload_solution_set():
    ac = _solution_set_spec()["answer_contract"]
    ok, _ = is_valid_answer_payload([-3, 7], ac)
    assert ok
    ok2, _ = is_valid_answer_payload("{-3,7}", ac)
    assert ok2
