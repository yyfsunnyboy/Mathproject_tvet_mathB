from __future__ import annotations

from typing import Any

from core.gencode.division_point_slot_engine import generate_division_point_payload
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
from core.gencode.midpoint_source_fidelity import generate_source_faithful_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "coordinate_pair"
PROBLEM_TYPE_ID = "inverse_centroid_vertex"
TEXTBOOK_EXAMPLE_ID = 4447
DEFAULT_COMPONENT_ID = "src_4447" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return generate_source_faithful_payload(TEXTBOOK_EXAMPLE_ID, seed)
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B1_MidpointCoordinates",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy",
        "answer_schema_key": "coordinate_pair",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "coordinate_geometry.division_point_coordinates",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_MidpointCoordinates', 'source_example_id': 4447, 'textbook_example_id': 4447, 'source_hash': '5f2062b8112e31a86f22483eb37d7044', 'problem_type_id': 'compute_centroid_coordinates', 'required_capabilities': ['compute_centroid_coordinates'], 'classification_source': 'python_skill_classifier', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'coordinate_pair', 'checker_key': 'coordinate_pair_checker', 'equivalence_type': 'coordinate_pair_equivalence'}, 'answer_type': 'coordinate_pair'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_MidpointCoordinates', 'source_example_id': 4447, 'textbook_example_id': 4447, 'source_hash': '5f2062b8112e31a86f22483eb37d7044', 'problem_type_id': 'compute_centroid_coordinates', 'required_capabilities': ['compute_centroid_coordinates'], 'classification_source': 'python_skill_classifier', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'coordinate_pair', 'checker_key': 'coordinate_pair_checker', 'equivalence_type': 'coordinate_pair_equivalence'}, 'answer_type': 'coordinate_pair'}, 'problem_type_id': 'compute_centroid_coordinates', 'required_capabilities': ['compute_centroid_coordinates'], 'classification_source': 'python_skill_classifier', 'source_hash': '5f2062b8112e31a86f22483eb37d7044', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'coordinate_pair', 'checker_key': 'coordinate_pair_checker', 'equivalence_type': 'coordinate_pair_equivalence'}, 'source_example_id': 4447, 'answer_type': 'coordinate_pair', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B1_MidpointCoordinates', 'fixed_domain_key': 'coordinate_geometry.division_point_coordinates', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['compute_centroid_coordinates'], 'matched_capabilities': ['compute_centroid_coordinates'], 'selected_operation': '', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.gencode.division_point_slot_engine', 'entrypoint': 'generate_division_point_payload', 'allowed_operations': ['compute_midpoint_coordinates', 'compute_centroid_coordinates'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B1_MidpointCoordinates'})
    constraints["skill_id"] = "vh_數學B1_MidpointCoordinates"

    matrix = _v3_invoke_domain_entrypoint(
        generate_division_point_payload,
        entrypoint_name="generate_division_point_payload",
        domain_operation="compute_centroid_coordinates",
        seed=seed,
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints=constraints,
    )
    matrix = normalize_domain_payload_to_v3_matrix(matrix, norm_context)

    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
        answer_schema_key="coordinate_pair",
        domain_operation="compute_centroid_coordinates",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
