from __future__ import annotations

from core.gencode.problem_type_induction import _infer_template_slot
from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.slot_generators import SLOT_REGISTRY, generate_from_problem_type_spec
from core.gencode.spec_phase1_merge import slot_generator_readiness


def _spec(*, target_task: str) -> dict:
    return {
        "problem_type_id": f"numeric_{target_task}_short_answer",
        "target_task": target_task,
        "answer_contract": {
            "answer_type": "numeric",
            "answer_shape": "scalar",
            "checker": "numeric_checker",
            "answer_equivalence": "numeric_equal",
            "choices_required": False,
        },
        "generator_contract": {
            "template_slots": {"stem": "function_value_numeric"},
            "template_families": [target_task],
            "template_variants": [{"id": "default", "label": "default", "stem_pattern": "default", "enabled": True}],
            "parameter_schema": {"seed": {"type": "integer"}},
            "variation_dimensions": ["seed", "difficulty_level", "context_style", "function_symbol"],
            "validity_constraints": ["answer derivable from givens"],
            "answer_shape": "numeric",
        },
    }


def test_infer_template_slot_for_function_value_tasks_numeric():
    assert _infer_template_slot("numeric", "evaluate_function_value", []) == "function_value_numeric"
    assert _infer_template_slot("numeric", "interpret_function_notation", []) == "function_value_numeric"


def test_slot_registry_has_function_value_numeric():
    assert "function_value_numeric" in SLOT_REGISTRY
    assert "linear_function_two_point_choice" in SLOT_REGISTRY
    assert "linear_function_contextual_word_problem" in SLOT_REGISTRY


def test_function_value_numeric_generator_payload_shape_and_latex():
    spec = _spec(target_task="evaluate_function_value")
    payload = generate_from_problem_type_spec("mock_skill_function_value", spec, seed=7)
    assert isinstance(payload, dict)
    q = str(payload.get("question_text", ""))
    exp = str(payload.get("explanation", ""))
    assert "$" in q and "(x)" in q
    assert "$" in exp and "\\times" in exp
    ans = str(payload.get("answer", ""))
    corr = str(payload.get("correct_answer", ""))
    assert ans == corr
    int(ans)
    md = payload.get("metadata")
    assert isinstance(md, dict)
    assert isinstance(md.get("givens"), list) and md.get("givens")
    assert str(md.get("target", "")).strip()
    assert isinstance(md.get("derivation"), list) and md.get("derivation")
    assert md.get("template_slot") == "function_value_numeric"


def test_slot_generator_readiness_runtime_ready_for_function_value_numeric():
    spec = _spec(target_task="evaluate_function_value")
    assert slot_generator_readiness(spec) == "runtime_ready"


def test_function_value_slot_choice_branch_builds_two_point_linear_function():
    spec = _spec(target_task="interpret_function_notation")
    spec["problem_type_id"] = "single_choice_interpret_function_notation_single_choice"
    spec["answer_contract"] = {
        "answer_type": "single_choice",
        "answer_shape": "choice_label",
        "checker": "choice_label_checker",
        "answer_equivalence": "choice_label",
        "choices_required": True,
        "choice_count": 4,
        "correct_choice_count": 1,
    }

    payload = generate_from_problem_type_spec("mock_skill_function_choice", spec, seed=0)

    assert len(str(payload["question_text"])) > 30
    assert "線型函數" in payload["question_text"]
    assert "$f(x)=ax+b$" in payload["question_text"]
    assert payload["checker"] == "choice_label_checker"
    assert payload["answer_contract"]["checker"] == "choice_label_checker"
    assert len(payload["choices"]) == 4
    assert len({choice["text"] for choice in payload["choices"]}) == 4
    assert payload["metadata"]["template_slot"] == "linear_function_two_point_choice"
    assert payload["metadata"]["scenario"] == "two_point_linear_function_choice"


def test_function_value_slot_application_branch_uses_contextual_expression_templates():
    spec = _spec(target_task="evaluate_function_value")
    spec["problem_type_id"] = "expression_evaluate_function_value"
    spec["answer_contract"] = {
        "answer_type": "expression",
        "answer_shape": "scalar",
        "checker": "expression_checker",
        "answer_equivalence": "algebraic_equivalent",
        "choices_required": False,
    }
    spec["generator_contract"]["contextual_application"] = True

    payloads = [
        generate_from_problem_type_spec("mock_skill_function_application", spec, seed=seed)
        for seed in range(12)
    ]

    assert {payload["metadata"]["scenario"] for payload in payloads} >= {
        "fuel_remaining",
        "mobile_plan",
    }
    for payload in payloads:
        assert len(str(payload["question_text"])) > 30
        assert "$f(x)$" in payload["question_text"]
        assert payload["answer_type"] == "expression"
        assert payload["checker"] == "expression_checker"
        assert "x" in str(payload["answer"])
        assert check_answer(
            f"({payload['answer']})+0",
            payload["correct_answer"],
            payload=payload,
            answer_contract=payload["answer_contract"],
        )


def test_function_value_slot_choice_branch_repairs_legacy_expression_choice_contract():
    spec = _spec(target_task="interpret_function_notation")
    spec["problem_type_id"] = "expression_interpret_function_notation"
    spec["answer_contract"] = {
        "answer_type": "expression",
        "answer_shape": "choice_label",
        "checker": "expression_checker",
        "answer_equivalence": "algebraic_equivalent",
        "source_has_choices": True,
        "choices_required": False,
    }
    spec["generator_contract"]["has_choices"] = True

    payload = generate_from_problem_type_spec("mock_skill_legacy_function_choice", spec, seed=3)

    assert payload["answer_type"] == "single_choice"
    assert payload["answer_contract"]["answer_type"] == "single_choice"
    assert payload["checker"] == "choice_label_checker"
    assert len(payload["choices"]) == 4
