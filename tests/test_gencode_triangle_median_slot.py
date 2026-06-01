from __future__ import annotations

from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.slot_generators import SLOT_REGISTRY, generate_from_problem_type_spec
from core.gencode.spec_phase1_merge import slot_generator_readiness
from core.gencode.template_slot_resolver import resolve_template_slot


def _spec(answer_type: str = "numeric_or_radical") -> dict:
    checker = "numeric_checker" if answer_type == "numeric" else "expression_equivalence_checker"
    return {
        "problem_type_id": f"{answer_type}_compute_triangle_median_line",
        "target_task": "compute_triangle_median_line",
        "answer_contract": {
            "answer_type": answer_type,
            "answer_shape": "scalar",
            "checker": checker,
            "answer_equivalence": "numeric_equal" if answer_type == "numeric" else "expression_equivalence",
            "choices_required": False,
        },
        "generator_contract": {
            "template_families": ["compute_triangle_median_line"],
            "template_slots": {"stem": "linear_triangle_median_compute"},
        },
    }


def test_triangle_median_target_task_routes_to_registered_slot():
    spec = _spec()
    assert resolve_template_slot(spec, seed=0) == "linear_triangle_median_compute"
    assert "linear_triangle_median_compute" in SLOT_REGISTRY
    assert slot_generator_readiness(spec) == "runtime_ready"


def test_triangle_median_expression_payload_is_complete_and_deterministic():
    spec = _spec()
    for seed in range(20):
        payload = generate_from_problem_type_spec("mock_triangle_median", spec, seed=seed)
        assert len(str(payload["question_text"])) > 30
        assert "三角形" in payload["question_text"]
        assert "中點公式" in payload["question_text"]
        assert "\\overline{AM}" in payload["question_text"]
        assert payload["metadata"]["template_slot"] == "linear_triangle_median_compute"
        assert check_answer(
            payload["answer"],
            payload["correct_answer"],
            payload=payload,
            answer_contract=spec["answer_contract"],
        )


def test_triangle_median_numeric_contract_only_emits_numeric_answers():
    spec = _spec("numeric")
    for seed in range(10):
        payload = generate_from_problem_type_spec("mock_triangle_median_numeric", spec, seed=seed)
        float(str(payload["answer"]))
        assert payload["checker"] == "numeric_checker"
