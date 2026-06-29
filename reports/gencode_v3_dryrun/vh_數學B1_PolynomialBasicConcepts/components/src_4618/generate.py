from __future__ import annotations

from typing import Any

from core.domain.statistics.descriptive_statistics_domain import build_descriptive_statistics_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "complete_descriptive_statistics_table"
TEXTBOOK_EXAMPLE_ID = 4618
DEFAULT_COMPONENT_ID = "src_4618" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_descriptive_statistics_matrix(
        seed=seed,
        domain_operation="complete_descriptive_statistics_table",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_PolynomialBasicConcepts', 'source_example_id': 4618, 'textbook_example_id': 4618, 'source_hash': 'a5c4ad79e8927604266b86acebf4c952', 'problem_type_id': 'descriptive_statistics_table_completion', 'required_capabilities': ['descriptive_statistics_table_completion'], 'classification_source': 'descriptive_statistics_domain_analyzer', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression', 'selected_operation': 'complete_descriptive_statistics_table', 'domain_operation': 'complete_descriptive_statistics_table', 'answer_shape': 'table_fill', 'fixed_domain_key': 'statistics.descriptive_statistics'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B1_PolynomialBasicConcepts', 'source_example_id': 4618, 'textbook_example_id': 4618, 'source_hash': 'a5c4ad79e8927604266b86acebf4c952', 'problem_type_id': 'descriptive_statistics_table_completion', 'required_capabilities': ['descriptive_statistics_table_completion'], 'classification_source': 'descriptive_statistics_domain_analyzer', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression', 'selected_operation': 'complete_descriptive_statistics_table', 'domain_operation': 'complete_descriptive_statistics_table', 'answer_shape': 'table_fill', 'fixed_domain_key': 'statistics.descriptive_statistics'}, 'problem_type_id': 'descriptive_statistics_table_completion', 'required_capabilities': ['descriptive_statistics_table_completion'], 'classification_source': 'descriptive_statistics_domain_analyzer', 'source_hash': 'a5c4ad79e8927604266b86acebf4c952', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'source_example_id': 4618, 'answer_type': 'expression', 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'vh_數學B1_PolynomialBasicConcepts', 'fixed_domain_key': 'statistics.descriptive_statistics', 'resolution_source': 'derived_capability_match', 'binding_status': 'derived', 'required_capabilities': ['descriptive_statistics_table_completion'], 'matched_capabilities': ['descriptive_statistics_table_completion'], 'selected_operation': 'descriptive_statistics_table_completion', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.statistics.descriptive_statistics_domain', 'entrypoint': 'build_descriptive_statistics_matrix', 'allowed_operations': ['compute_arithmetic_mean_from_raw_values', 'compute_arithmetic_mean_from_frequency_table', 'compute_weighted_mean', 'compute_median_from_raw_values', 'compute_mode_from_raw_values', 'compute_mode_from_frequency_table', 'compute_range', 'compute_population_variance', 'compute_population_standard_deviation', 'compute_sample_variance', 'compute_sample_standard_deviation', 'complete_descriptive_statistics_table', 'compute_quartiles_and_iqr', 'compare_dispersion', 'conceptual_dispersion_judgment', 'compute_linear_transform_median_and_range', 'empirical_rule_probability', 'empirical_rule_population_count', 'compare_distribution_spread'], 'curriculum_profile': 'vocational_high_b'}, 'question_text': '已知$f\\left( x \\right)=2{{x}^{2}}+{{x}^{3}}-3x-5$，\n$g\\left( x \\right)=-3{{x}^{2}}+{{x}^{4}}-2x+{{x}^{3}}+1$，試按降冪排列完成下表：'},
    )
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
        answer_schema_key="numeric_scalar",
        domain_operation="complete_descriptive_statistics_table",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
