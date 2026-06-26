from __future__ import annotations

from typing import Any

from core.domain.statistics.descriptive_statistics_domain import build_descriptive_statistics_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "compute_quartiles_and_iqr"
TEXTBOOK_EXAMPLE_ID = 3845
DEFAULT_COMPONENT_ID = "src_3845" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_descriptive_statistics_matrix(
        seed=seed,
        domain_operation="compute_quartiles_and_iqr",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B4_DispersionMeasures', 'source_example_id': 3845, 'textbook_example_id': 3845, 'source_hash': 'c96d32db441b6ed10cd9f9527897fd42', 'problem_type_id': 'quartiles_and_iqr_computation', 'required_capabilities': ['range', 'quartile', 'interquartile_range'], 'classification_source': 'descriptive_statistics_domain_analyzer', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression', 'selected_operation': 'compute_quartiles_and_iqr', 'domain_operation': 'compute_quartiles_and_iqr', 'answer_shape': 'multi_part', 'fixed_domain_key': 'statistics.descriptive_statistics'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B4_DispersionMeasures', 'source_example_id': 3845, 'textbook_example_id': 3845, 'source_hash': 'c96d32db441b6ed10cd9f9527897fd42', 'problem_type_id': 'quartiles_and_iqr_computation', 'required_capabilities': ['range', 'quartile', 'interquartile_range'], 'classification_source': 'descriptive_statistics_domain_analyzer', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'answer_type': 'expression', 'selected_operation': 'compute_quartiles_and_iqr', 'domain_operation': 'compute_quartiles_and_iqr', 'answer_shape': 'multi_part', 'fixed_domain_key': 'statistics.descriptive_statistics'}, 'problem_type_id': 'quartiles_and_iqr_computation', 'required_capabilities': ['range', 'quartile', 'interquartile_range'], 'classification_source': 'descriptive_statistics_domain_analyzer', 'source_hash': 'c96d32db441b6ed10cd9f9527897fd42', 'presentation_mode': 'short_answer', 'answer_contract': {'answer_type': 'expression', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent'}, 'source_example_id': 3845, 'answer_type': 'expression', 'exact_task_operation': '', 'source_answer_label': '(1) R=75, IQR=32；(2) R=24, IQR=15', 'domain_resolution': {'skill_id': 'vh_數學B4_DispersionMeasures', 'fixed_domain_key': 'statistics.descriptive_statistics', 'resolution_source': 'derived_capability_match', 'binding_status': 'derived', 'required_capabilities': ['range', 'quartile', 'interquartile_range'], 'matched_capabilities': ['interquartile_range', 'quartile', 'range'], 'selected_operation': 'quartiles_and_iqr_computation', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.statistics.descriptive_statistics_domain', 'entrypoint': 'build_descriptive_statistics_matrix', 'allowed_operations': ['compute_arithmetic_mean_from_raw_values', 'compute_arithmetic_mean_from_frequency_table', 'compute_weighted_mean', 'compute_median_from_raw_values', 'compute_mode_from_raw_values', 'compute_mode_from_frequency_table', 'compute_range', 'compute_population_variance', 'compute_population_standard_deviation', 'complete_descriptive_statistics_table', 'compute_quartiles_and_iqr', 'compare_dispersion', 'conceptual_dispersion_judgment'], 'curriculum_profile': 'vocational_high_b'}, 'question_text': '試求下列兩組資料的全距 R 與四分位距 IQR：(1) 5, 17, 18, 18, 27, 31, 32, 32, 50, 80, 80；(2) 55, 56, 56, 60, 65, 70, 72, 79。', 'source_answer_text': '(1) R=75, IQR=32；(2) R=24, IQR=15', 'datasets': [{'label': '組別1', 'raw_values': [5.0, 17.0, 18.0, 18.0, 27.0, 31.0, 32.0, 32.0, 50.0, 80.0, 80.0]}, {'label': '組別2', 'raw_values': [55.0, 56.0, 56.0, 60.0, 65.0, 70.0, 72.0, 79.0]}]},
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
        domain_operation="compute_quartiles_and_iqr",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
