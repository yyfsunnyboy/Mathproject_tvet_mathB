from __future__ import annotations

from typing import Any

from core.domain.statistics.descriptive_statistics_domain import build_descriptive_statistics_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "compute_arithmetic_mean_from_raw_values"
TEXTBOOK_EXAMPLE_ID = 3887
DEFAULT_COMPONENT_ID = "src_3887" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_descriptive_statistics_matrix(
        seed=seed,
        domain_operation="compute_arithmetic_mean_from_raw_values",
        curriculum_profile="vocational_high_b",
        difficulty_profile="hard",
        constraints={'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B4_CentralTendencyMeasures', 'source_example_id': 3887, 'textbook_example_id': 3887, 'source_hash': 'b17609aabedd867097f83c11e7b6fd7f', 'problem_type_id': 'arithmetic_mean_computation', 'required_capabilities': ['arithmetic_mean'], 'classification_source': 'generic_structural_inference', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B4_CentralTendencyMeasures', 'source_example_id': 3887, 'textbook_example_id': 3887, 'source_hash': 'b17609aabedd867097f83c11e7b6fd7f', 'problem_type_id': 'arithmetic_mean_computation', 'required_capabilities': ['arithmetic_mean'], 'classification_source': 'generic_structural_inference', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice'}, 'problem_type_id': 'arithmetic_mean_computation', 'required_capabilities': ['arithmetic_mean'], 'classification_source': 'generic_structural_inference', 'source_hash': 'b17609aabedd867097f83c11e7b6fd7f', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'source_example_id': 3887, 'answer_type': 'choice', 'exact_task_operation': '', 'source_choices': ['64', '65', '71', '74。'], 'source_answer_label': 'B', 'domain_resolution': {'skill_id': 'vh_數學B4_CentralTendencyMeasures', 'fixed_domain_key': 'statistics.descriptive_statistics', 'resolution_source': 'derived_capability_match', 'binding_status': 'derived', 'required_capabilities': ['arithmetic_mean'], 'matched_capabilities': ['arithmetic_mean'], 'selected_operation': 'arithmetic_mean_computation', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.statistics.descriptive_statistics_domain', 'entrypoint': 'build_descriptive_statistics_matrix', 'allowed_operations': ['compute_arithmetic_mean_from_raw_values', 'compute_arithmetic_mean_from_frequency_table', 'compute_weighted_mean', 'compute_median_from_raw_values', 'compute_mode_from_raw_values', 'compute_mode_from_frequency_table', 'compute_range', 'compute_population_variance', 'compute_population_standard_deviation', 'complete_descriptive_statistics_table'], 'curriculum_profile': 'vocational_high_b'}},
    )
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
        answer_schema_key="",
        domain_operation="compute_arithmetic_mean_from_raw_values",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
