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


def test_strict_integer_rational_shape_audit():
    from core.gencode.runtime_smoke import _validate_runtime_payload

    # 1. Test integer answer type containing non-digits (Chinese text)
    payload_int_bad = {
        "question_text": "求函數值。",
        "answer_type": "integer",
        "answer": "第四象限",
        "correct_answer": "第四象限",
        "choices": [],
        "problem_type_id": "integer_numeric_evaluate_function_notation",
        "answer_contract": {
            "answer_type": "integer",
            "equivalence_type": "numeric_exact",
            "checker_key": "integer_checker",
        },
        "metadata": {"givens": [], "target": "y", "derivation": []},
    }
    blockers, _ = _validate_runtime_payload(payload_int_bad, "vh_數學B1_LinearFunction")
    assert "shape_mismatch" in blockers

    # 2. Test rational answer type containing alphabetical character pollution
    payload_rat_bad = {
        "question_text": "求機率。",
        "answer_type": "rational",
        "answer": "1/2a",
        "correct_answer": "1/2a",
        "choices": [],
        "problem_type_id": "probability_basic_question",
        "answer_contract": {
            "answer_type": "rational",
            "equivalence_type": "rational_equivalent",
            "checker_key": "rational_checker",
        },
        "metadata": {"givens": [], "target": "p", "derivation": []},
    }
    blockers2, _ = _validate_runtime_payload(payload_rat_bad, "vh_數學B1_LinearFunction")
    assert "shape_mismatch" in blockers2


def test_fake_diversity_detection_smoke():
    import tempfile
    import os as _os

    # Write a draft file that ignores seed and always outputs identical payload
    dummy_lines = [
        "GENERATOR_SPECS = [",
        "    {",
        '        "problem_type_id": "numeric_numeric_evaluate_function_notation_short_answer",',
        '        "answer_contract": {',
        '            "answer_type": "numeric",',
        '            "answer_shape": "scalar",',
        '            "answer_equivalence": "numeric_exact",',
        '            "checker": "numeric_checker",',
        '            "choices_required": False',
        "        }",
        "    }",
        "]",
        "def generate(level=1, seed=None):",
        "    return {",
        '        "question_text": "固定題目",',
        '        "answer_type": "numeric",',
        '        "answer": "42",',
        '        "correct_answer": "42",',
        '        "choices": [],',
        '        "problem_type_id": "numeric_numeric_evaluate_function_notation_short_answer",',
        '        "answer_contract": {',
        '            "answer_type": "numeric",',
        '            "answer_shape": "scalar",',
        '            "answer_equivalence": "numeric_exact",',
        '            "checker": "numeric_checker",',
        '            "choices_required": False',
        "        },",
        '        "metadata": {',
        '            "givens": [{"type": "symbolic_condition", "text": "f(x)=2x+1", "variables": ["x"]}],',
        '            "target": {"type": "evaluate_function", "x_val": "2", "variables": []},',
        '            "derivation": ["f(2) = 2*2+1 = 42"]',
        "        },",
        "    }",
        "",
        "def check(ua, ca, question_payload=None):",
        "    return str(ua).strip() == str(ca).strip()",
    ]
    dummy_code = "\n".join(dummy_lines) + "\n"

    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
        f.write(dummy_code)
        f_path = f.name

    try:
        # Run run_draft_runtime_smoke and check if fake_diversity_fatal was triggered
        res = run_draft_runtime_smoke("vh_數學B1_LinearFunction", f_path, sample_count=5)
        assert res.get("status") == "failed", res
        assert "fake_diversity_fatal" in res.get("blockers"), res.get("blockers")
    finally:
        try:
            _os.remove(f_path)
        except Exception:
            pass


def test_semantic_drifting_filter():
    from core.gencode.runtime_smoke import _validate_runtime_payload

    # 1. Test linear function containing drifting keyword "中點" (absent from its textbook examples)
    payload_drift = {
        "question_text": "求中點座標。",
        "answer_type": "numeric",
        "answer": "5",
        "correct_answer": "5",
        "choices": [],
        "problem_type_id": "numeric_numeric_evaluate_function_notation_short_answer",
        "answer_contract": {
            "answer_type": "numeric",
            "equivalence_type": "numeric_exact",
            "checker_key": "integer_checker",
        },
        "metadata": {
            "givens": [{"type": "symbolic_condition", "text": "f(x)=2x+1", "variables": ["x"]}],
            "target": {"type": "evaluate_function", "x_val": "2", "variables": []},
            "derivation": [],
        },
    }
    blockers, _ = _validate_runtime_payload(payload_drift, "vh_數學B1_LinearFunction")
    assert "semantic_drifting_fatal" in blockers

    # 2. Test valid linear function payload passes through
    payload_ok = {
        "question_text": "求 f(2) 的值。",
        "answer_type": "numeric",
        "answer": "5",
        "correct_answer": "5",
        "choices": [],
        "problem_type_id": "numeric_numeric_evaluate_function_notation_short_answer",
        "answer_contract": {
            "answer_type": "numeric",
            "equivalence_type": "numeric_exact",
            "checker_key": "integer_checker",
        },
        "metadata": {
            "givens": [{"type": "symbolic_condition", "text": "f(x)=2x+1", "variables": ["x"]}],
            "target": {"type": "evaluate_function", "x_val": "2", "variables": []},
            "derivation": ["f(2) = 5"],
        },
        "explanation": "步驟一",
    }
    blockers2, _ = _validate_runtime_payload(payload_ok, "vh_數學B1_LinearFunction")
    assert "semantic_drifting_fatal" not in blockers2


def test_expression_and_choice_shape_relaxation():
    from core.gencode.runtime_smoke import _validate_runtime_payload

    # Test 1: Algebraic expression with unicode minus sign and variable x
    payload_expr = {
        "question_text": "求函數的關係式。",
        "answer_type": "integer",  # Contract says integer initially
        "answer": "\u2212x + 2",
        "correct_answer": "\u2212x + 2",
        "choices": [],
        "problem_type_id": "short_answer_interpret_function_notation_short_answer",
        "answer_contract": {
            "answer_type": "integer",
            "equivalence_type": "numeric_exact",
            "checker_key": "integer_checker",
        },
        "metadata": {"givens": [], "target": "y", "derivation": []},
        "explanation": "說明",
    }
    blockers, _ = _validate_runtime_payload(payload_expr, "vh_數學B1_LinearFunction")
    # Should not fail shape check because −x + 2 is recognized as expression and aligned
    assert "shape_mismatch" not in blockers

    # Test 2: Choice question returning label "A"
    payload_choice = {
        "question_text": "設 f(x) = ax+b，選出正確關係式。",
        "answer_type": "integer",  # Contract says integer initially
        "answer": "A",
        "correct_answer": "A",
        "choices": ["\u2212x + 2", "x \u2212 2", "x + 2", "\u2212x \u2212 2"],
        "problem_type_id": "short_answer_interpret_function_notation_short_answer",
        "answer_contract": {
            "answer_type": "integer",
            "equivalence_type": "numeric_exact",
            "checker_key": "integer_checker",
        },
        "metadata": {"givens": [], "target": "y", "derivation": []},
        "explanation": "說明",
    }
    blockers2, _ = _validate_runtime_payload(payload_choice, "vh_數學B1_LinearFunction")
    # Should not fail shape check because "A" with choices is recognized as single_choice
    assert "shape_mismatch" not in blockers2


def test_phase1_source_salvage_and_unclassified_recovery():
    from core.gencode.induction_source_policy import filter_core_induction_examples
    from core.gencode.problem_type_induction import merge_unclassified_low_confidence_examples

    # Test 1: Salvage missing answer or broken LaTeX core example
    features = [
        {
            "source_example_id": 9991,
            "question_text": "設 $f(x)=ax+b$ 且過點 $(-2, 4)$，破損格式",
            "answer": "",  # missing answer
            "correct_answer": "",
            "answer_type": "short_answer",
            "choices": [],
            "source_quality_issues": ["missing_answer", "broken_latex_fraction"],
            "source_quality_reject": True,
            "induction_tier": "core",
        }
    ]
    examples = [
        {
            "id": 9991,
            "skill_id": "vh_數學B1_LinearFunction",
            "problem_text": "設 $f(x)=ax+b$ 且過點 $(-2, 4)$，破損格式",
            "correct_answer": "",
        }
    ]

    filter_core_induction_examples(features, examples)
    # Check that it's salvaged:
    assert features[0]["source_quality_reject"] is False
    assert features[0]["source_quality_status"] == "FORCE_ALLOWED_FOR_INDUCTION"
    assert features[0]["answer"] == "0"  # dynamic placeholder
    assert examples[0]["correct_answer"] == "0"

    # Test 2: Unclassified low confidence core example recovery
    excluded = [
        {
            "example_id": 9992,
            "exclude_reason": "unclassified_low_confidence",
            "induction_tier": "core",
            "included_in_phase1": False,
        }
    ]
    features_all = [
        {
            "source_example_id": 9992,
            "question_text": "極深應用題情境：油量計算表格",
            "answer": "12",
            "correct_answer": "12",
            "answer_type": "short_answer",
            "choices": [],
            "target_task": "compute_numeric",
            "induction_tier": "core",
        }
    ]
    features_for_induction = []
    main_skill_anchor = {
        "fallback_subskill": {"subskill_id": "evaluate_function_value"}
    }

    features_for_induction, still_excluded = merge_unclassified_low_confidence_examples(
        features_for_induction,
        excluded,
        features_all,
        "vh_數學B1_LinearFunction",
        main_skill_anchor,
    )

    assert len(features_for_induction) == 1
    assert features_for_induction[0]["target_task"] == "evaluate_function_value"
    assert "fallback_application" in features_for_induction[0]["problem_type_id"]
    assert len(still_excluded) == 0
