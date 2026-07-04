from __future__ import annotations

from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.gencode.division_point_slot_engine import (
    build_graph_based_tiered_linear_application_multi_part_matrix,
)
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
from core.gencode.services.v3_question_integrity_validator import validate_component_payload
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority
from core.registry.domain_operation_registry import check_registry_consistency

FIXED_SEEDS = (7, 42, 101)
OP = "graph_based_tiered_linear_application_multi_part"


def _payload_for_seed(seed: int, *, component_id: str, textbook_example_id: int) -> dict:
    matrix = build_graph_based_tiered_linear_application_multi_part_matrix(seed=seed)
    return convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="graph_multi_part",
        answer_type="multi_part",
        problem_type_id=OP,
        component_id=component_id,
        textbook_example_id=textbook_example_id,
        domain_operation=OP,
    )


def test_registry_and_resolver_ready() -> None:
    issues = check_registry_consistency()
    assert not issues
    resolved = resolve_domain_authority(
        "vh_數學B1_LinearFunction",
        problem_type_id=OP,
        extra={"required_capabilities": [OP]},
    )
    assert resolved.selected_operation == OP
    assert resolved.fixed_domain_key == "coordinate_geometry.division_point_coordinates"


def test_mathematical_invariants_and_seeds() -> None:
    for seed in FIXED_SEEDS:
        matrix = build_graph_based_tiered_linear_application_multi_part_matrix(seed=seed)
        facts = matrix["validation_facts"]
        assert 1 <= facts["val1"] < facts["limit"]
        assert facts["val2"] > facts["limit"]
        assert facts["tier1_rate"] < facts["tier2_rate"]
        assert facts["ans1"] == facts["val1"] * facts["tier1_rate"]
        assert facts["ans2"] == (
            facts["limit"] * facts["tier1_rate"]
            + (facts["val2"] - facts["limit"]) * facts["tier2_rate"]
        )
        answer = matrix["semantic_answer"]
        assert answer == {"part_1": facts["ans1"], "part_2": facts["ans2"]}
        question = matrix["question"]
        for token in (
            facts["val1"],
            facts["val2"],
            facts["limit"],
            facts["tier1_rate"],
            facts["tier2_rate"],
        ):
            assert str(token) in question
        assert "（1）" in question and "（2）" in question


def test_adapter_answer_contract_checker_and_validator_per_component() -> None:
    components = (
        ("src_4425", 4425),
        ("src_4445", 4445),
    )
    for component_id, example_id in components:
        for seed in FIXED_SEEDS:
            payload = _payload_for_seed(
                seed,
                component_id=component_id,
                textbook_example_id=example_id,
            )
            answer = payload["semantic_answer"]
            assert payload["answer"] == payload["correct_answer"] == answer
            ac = payload["answer_contract"]
            assert ac["answer_type"] == "multi_part"
            assert ac["checker"] == "multi_part_answer_checker"
            assert ac["presentation_mode"] == "graph_multi_part"
            assert {p["key"] for p in ac["parts"]} == {"part_1", "part_2"}

            correct = check_multi_part_answer(
                answer,
                answer,
                answer_contract=ac,
                payload=payload,
            )
            assert correct.get("is_correct") is True

            wrong = {k: int(v) + 1 for k, v in answer.items()}
            incorrect = check_multi_part_answer(
                wrong,
                answer,
                answer_contract=ac,
                payload=payload,
            )
            assert incorrect.get("is_correct") is False

            integrity = validate_component_payload(payload, component_id=component_id)
            assert integrity.get("passed") is True, integrity.get("blockers")
