from __future__ import annotations

from typing import Any

from core.domain.statistics.descriptive_statistics_domain import build_descriptive_statistics_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "compare_dispersion"
TEXTBOOK_EXAMPLE_ID = 3847
DEFAULT_COMPONENT_ID = "src_3847" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_descriptive_statistics_matrix(
        seed=seed,
        domain_operation="compare_dispersion",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B4_DispersionMeasures', 'source_example_id': 3847, 'textbook_example_id': 3847, 'source_hash': '7245ea3ac78040faf5b69c1e92b49229', 'problem_type_id': 'dispersion_comparison', 'required_capabilities': ['dispersion_comparison', 'range', 'quartile', 'interquartile_range'], 'classification_source': 'descriptive_statistics_domain_analyzer', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression', 'selected_operation': 'compare_dispersion', 'domain_operation': 'compare_dispersion', 'answer_shape': 'multi_part', 'fixed_domain_key': 'statistics.descriptive_statistics'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B4_DispersionMeasures', 'source_example_id': 3847, 'textbook_example_id': 3847, 'source_hash': '7245ea3ac78040faf5b69c1e92b49229', 'problem_type_id': 'dispersion_comparison', 'required_capabilities': ['dispersion_comparison', 'range', 'quartile', 'interquartile_range'], 'classification_source': 'descriptive_statistics_domain_analyzer', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression', 'selected_operation': 'compare_dispersion', 'domain_operation': 'compare_dispersion', 'answer_shape': 'multi_part', 'fixed_domain_key': 'statistics.descriptive_statistics'}, 'problem_type_id': 'dispersion_comparison', 'required_capabilities': ['dispersion_comparison', 'range', 'quartile', 'interquartile_range'], 'classification_source': 'descriptive_statistics_domain_analyzer', 'source_hash': '7245ea3ac78040faf5b69c1e92b49229', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'source_example_id': 3847, 'answer_type': 'expression', 'exact_task_operation': '', 'source_answer_label': '略', 'domain_resolution': {'skill_id': 'vh_數學B4_DispersionMeasures', 'fixed_domain_key': 'statistics.descriptive_statistics', 'resolution_source': 'derived_capability_match', 'binding_status': 'derived', 'required_capabilities': ['dispersion_comparison', 'range', 'quartile', 'interquartile_range'], 'matched_capabilities': ['dispersion_comparison', 'interquartile_range', 'quartile', 'range'], 'selected_operation': 'dispersion_comparison', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.statistics.descriptive_statistics_domain', 'entrypoint': 'build_descriptive_statistics_matrix', 'allowed_operations': ['compute_arithmetic_mean_from_raw_values', 'compute_arithmetic_mean_from_frequency_table', 'compute_weighted_mean', 'compute_median_from_raw_values', 'compute_mode_from_raw_values', 'compute_mode_from_frequency_table', 'compute_range', 'compute_population_variance', 'compute_population_standard_deviation', 'complete_descriptive_statistics_table', 'compute_quartiles_and_iqr', 'compare_dispersion', 'conceptual_dispersion_judgment'], 'curriculum_profile': 'vocational_high_b'}, 'question_text': '某籃球隊身高：(1)女生：182, 175, 175, 184, 188, 184, 177, 168, 178；(2)男生：185, 175, 181, 191, 198, 193, 187, 182, 178, 200。求 R 與 IQR。'},
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
        domain_operation="compare_dispersion",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
