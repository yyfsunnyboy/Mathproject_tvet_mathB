from __future__ import annotations

from typing import Any

from core.gencode.division_point_slot_engine import generate_division_point_payload
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "graph_multi_part"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "graph_based_tiered_linear_application_multi_part"
TEXTBOOK_EXAMPLE_ID = 4445
DEFAULT_COMPONENT_ID = "src_4445" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    norm_context = {
        "skill_id": "vh_數學B1_LinearFunction",
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy",
        "answer_schema_key": "multi_part_scalar",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "coordinate_geometry.division_point_coordinates",
    }

    constraints = dict({'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_LinearFunction', 'source_example_id': 4445, 'textbook_example_id': 4445, 'source_hash': 'b89cb6af41bb63da02d17720d18e17cd', 'problem_type_id': 'graph_based_tiered_linear_application_multi_part', 'required_capabilities': ['graph_based_tiered_linear_application_multi_part'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'graph_multi_part', 'answer_contract': {'answer_type': 'multi_part', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer'}, 'answer_type': 'multi_part', 'source_topology': {'problem_type_id': 'graph_based_tiered_linear_application_multi_part', 'exact_task_operation': 'graph_based_tiered_linear_application_multi_part', 'required_givens': ['context_variables', 'threshold_rule', 'linear_relation_graph'], 'requested_quantity': ['base_value', 'evaluated_context_value'], 'topology_tags': ['contextual_application', 'graph_reading', 'threshold', 'multi_part'], 'answer_schema': 'multi_part_numeric', 'presentation_mode': 'graph_multi_part'}, 'required_givens': ['context_variables', 'threshold_rule', 'linear_relation_graph'], 'requested_quantity': ['base_value', 'evaluated_context_value'], 'topology_tags': ['contextual_application', 'graph_reading', 'threshold', 'multi_part'], 'answer_schema': 'multi_part_numeric'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_LinearFunction', 'source_example_id': 4445, 'textbook_example_id': 4445, 'source_hash': 'b89cb6af41bb63da02d17720d18e17cd', 'problem_type_id': 'graph_based_tiered_linear_application_multi_part', 'required_capabilities': ['graph_based_tiered_linear_application_multi_part'], 'classification_source': 'phase1_rule_pack', 'presentation_mode': 'graph_multi_part', 'answer_contract': {'answer_type': 'multi_part', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer'}, 'answer_type': 'multi_part', 'source_topology': {'problem_type_id': 'graph_based_tiered_linear_application_multi_part', 'exact_task_operation': 'graph_based_tiered_linear_application_multi_part', 'required_givens': ['context_variables', 'threshold_rule', 'linear_relation_graph'], 'requested_quantity': ['base_value', 'evaluated_context_value'], 'topology_tags': ['contextual_application', 'graph_reading', 'threshold', 'multi_part'], 'answer_schema': 'multi_part_numeric', 'presentation_mode': 'graph_multi_part'}, 'required_givens': ['context_variables', 'threshold_rule', 'linear_relation_graph'], 'requested_quantity': ['base_value', 'evaluated_context_value'], 'topology_tags': ['contextual_application', 'graph_reading', 'threshold', 'multi_part'], 'answer_schema': 'multi_part_numeric'}, 'problem_type_id': 'graph_based_tiered_linear_application_multi_part', 'required_capabilities': ['graph_based_tiered_linear_application_multi_part'], 'classification_source': 'phase1_rule_pack', 'source_hash': 'b89cb6af41bb63da02d17720d18e17cd', 'presentation_mode': 'graph_multi_part', 'answer_contract': {'answer_type': 'multi_part', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer'}, 'source_example_id': 4445, 'answer_type': 'multi_part', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B1_LinearFunction', 'fixed_domain_key': 'coordinate_geometry.division_point_coordinates', 'resolution_source': 'derived_capability_match', 'binding_status': 'derived', 'required_capabilities': ['graph_based_tiered_linear_application_multi_part'], 'matched_capabilities': ['graph_based_tiered_linear_application_multi_part'], 'selected_operation': 'graph_based_tiered_linear_application_multi_part', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.gencode.division_point_slot_engine', 'entrypoint': 'generate_division_point_payload', 'allowed_operations': ['compute_internal_division_point_coordinates', 'compute_centroid_coordinates', 'compute_section_point_distance_from_origin', 'compute_midpoint_coordinates', 'midpoint_coordinate', 'midpoint_distance_from_origin', 'parallelogram_fourth_vertex', 'centroid_coordinate', 'inverse_centroid_vertex', 'triangle_median_length', 'multi_part_midpoint_application', 'graph_based_tiered_linear_application_multi_part'], 'curriculum_profile': 'vocational_high_b'}, 'skill_id': 'vh_數學B1_LinearFunction'})
    constraints["skill_id"] = "vh_數學B1_LinearFunction"

    matrix = _v3_invoke_domain_entrypoint(
        generate_division_point_payload,
        entrypoint_name="generate_division_point_payload",
        domain_operation="graph_based_tiered_linear_application_multi_part",
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
        answer_schema_key="multi_part_scalar",
        domain_operation="graph_based_tiered_linear_application_multi_part",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
