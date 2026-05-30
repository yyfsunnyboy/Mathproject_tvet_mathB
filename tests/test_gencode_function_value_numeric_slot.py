from __future__ import annotations

from core.gencode.problem_type_induction import _infer_template_slot
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
