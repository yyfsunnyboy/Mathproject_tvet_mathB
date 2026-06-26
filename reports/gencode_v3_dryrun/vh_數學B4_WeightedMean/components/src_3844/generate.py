from __future__ import annotations

from typing import Any

from core.domain.statistics.descriptive_statistics_domain import build_descriptive_statistics_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "compute_weighted_mean"
TEXTBOOK_EXAMPLE_ID = 3844
DEFAULT_COMPONENT_ID = "src_3844" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_descriptive_statistics_matrix(
        seed=seed,
        domain_operation="compute_weighted_mean",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B4_WeightedMean', 'source_example_id': 3844, 'textbook_example_id': 3844, 'source_hash': 'b2783bb73ab4c3f63b4fe1ad2a501517', 'problem_type_id': 'weighted_mean_computation', 'required_capabilities': ['weighted_mean'], 'classification_source': 'generic_structural_inference', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B4_WeightedMean', 'source_example_id': 3844, 'textbook_example_id': 3844, 'source_hash': 'b2783bb73ab4c3f63b4fe1ad2a501517', 'problem_type_id': 'weighted_mean_computation', 'required_capabilities': ['weighted_mean'], 'classification_source': 'generic_structural_inference', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression'}, 'problem_type_id': 'weighted_mean_computation', 'required_capabilities': ['weighted_mean'], 'classification_source': 'generic_structural_inference', 'source_hash': 'b2783bb73ab4c3f63b4fe1ad2a501517', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'source_example_id': 3844, 'answer_type': 'expression', 'exact_task_operation': '', 'source_answer_label': '80 分', 'domain_resolution': {'skill_id': 'vh_數學B4_WeightedMean', 'fixed_domain_key': 'statistics.descriptive_statistics', 'resolution_source': 'derived_capability_match', 'binding_status': 'derived', 'required_capabilities': ['weighted_mean'], 'matched_capabilities': ['weighted_mean'], 'selected_operation': 'weighted_mean_computation', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.statistics.descriptive_statistics_domain', 'entrypoint': 'build_descriptive_statistics_matrix', 'allowed_operations': ['compute_arithmetic_mean_from_raw_values', 'compute_arithmetic_mean_from_frequency_table', 'compute_weighted_mean', 'compute_median_from_raw_values', 'compute_mode_from_raw_values', 'compute_mode_from_frequency_table', 'compute_range', 'compute_population_variance', 'compute_population_standard_deviation', 'complete_descriptive_statistics_table'], 'curriculum_profile': 'vocational_high_b'}},
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
        domain_operation="compute_weighted_mean",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
