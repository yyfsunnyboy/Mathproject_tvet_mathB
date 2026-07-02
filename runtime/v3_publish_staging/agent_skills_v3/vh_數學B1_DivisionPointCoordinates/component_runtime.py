from __future__ import annotations

from typing import Any

from core.gencode.division_point_slot_engine import generate_division_point_payload
from core.gencode.generator_contract_schema import enrich_generator_contract

SKILL_ID = "vh_數學B1_DivisionPointCoordinates"


def generate_component(
    *,
    source_id: int,
    problem_type_id: str,
    operation: str,
    answer_type: str,
    presentation_mode: str,
    checker_key: str,
    equivalence_type: str,
    generator_key: str,
    seed: int | None,
    component_id: str,
) -> dict[str, Any]:
    is_choice = presentation_mode == "single_choice"
    answer_contract = {
        "answer_type": "single_choice" if is_choice else answer_type,
        "answer_shape": "choice_label" if is_choice else "coordinate_pair",
        "answer_equivalence": equivalence_type,
        "equivalence_type": equivalence_type,
        "checker": checker_key,
        "checker_key": checker_key,
        "presentation_mode": presentation_mode,
        "choices_required": is_choice,
    }
    spec = {
        "skill_id": SKILL_ID,
        "problem_type_id": problem_type_id,
        "target_task": operation,
        "task_family": "division_point_coordinates_family",
        "answer_contract": answer_contract,
        "generator_contract": enrich_generator_contract(
            operation,
            answer_contract=answer_contract,
            problem_type_id=problem_type_id,
        ),
    }
    payload = generate_division_point_payload(
        SKILL_ID,
        problem_type_id,
        spec,
        seed,
    )
    payload["component_id"] = component_id
    payload["textbook_example_id"] = source_id
    payload["source_id"] = source_id
    payload["operation"] = operation
    payload["presentation_mode"] = presentation_mode
    payload["generator_key"] = generator_key
    payload["seed"] = seed
    metadata = dict(payload.get("metadata") or {})
    metadata["component_id"] = component_id
    metadata["source_trace"] = {
        "skill_id": SKILL_ID,
        "source_id": source_id,
        "component_id": component_id,
        "generator_key": generator_key,
    }
    payload["metadata"] = metadata
    return payload
