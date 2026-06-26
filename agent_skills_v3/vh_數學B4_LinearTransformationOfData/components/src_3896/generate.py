from __future__ import annotations

from typing import Any

from core.domain.statistics.descriptive_statistics_domain import build_descriptive_statistics_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "compute_population_standard_deviation"
TEXTBOOK_EXAMPLE_ID = 3896
DEFAULT_COMPONENT_ID = "src_3896" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_descriptive_statistics_matrix(
        seed=seed,
        domain_operation="compute_population_standard_deviation",
        curriculum_profile="vocational_high_b",
        difficulty_profile="hard",
        constraints={'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B4_LinearTransformationOfData', 'source_example_id': 3896, 'textbook_example_id': 3896, 'source_hash': 'e4a32986d8544c65b3919c8e6dc5247e', 'problem_type_id': 'standard_deviation_computation', 'required_capabilities': ['standard_deviation'], 'classification_source': 'descriptive_statistics_domain_analyzer', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice', 'selected_operation': 'compute_population_standard_deviation', 'domain_operation': 'compute_population_standard_deviation', 'answer_shape': 'single_choice', 'fixed_domain_key': 'statistics.descriptive_statistics'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B4_LinearTransformationOfData', 'source_example_id': 3896, 'textbook_example_id': 3896, 'source_hash': 'e4a32986d8544c65b3919c8e6dc5247e', 'problem_type_id': 'standard_deviation_computation', 'required_capabilities': ['standard_deviation'], 'classification_source': 'descriptive_statistics_domain_analyzer', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice', 'selected_operation': 'compute_population_standard_deviation', 'domain_operation': 'compute_population_standard_deviation', 'answer_shape': 'single_choice', 'fixed_domain_key': 'statistics.descriptive_statistics'}, 'problem_type_id': 'standard_deviation_computation', 'required_capabilities': ['standard_deviation'], 'classification_source': 'descriptive_statistics_domain_analyzer', 'source_hash': 'e4a32986d8544c65b3919c8e6dc5247e', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'source_example_id': 3896, 'answer_type': 'choice', 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '1'}, {'key': 'B', 'label': 'B', 'text': '2'}, {'key': 'C', 'label': 'C', 'text': '3'}, {'key': 'D', 'label': 'D', 'text': '4'}], 'source_answer_label': 'C', 'domain_resolution': {'skill_id': 'vh_數學B4_LinearTransformationOfData', 'fixed_domain_key': 'statistics.descriptive_statistics', 'resolution_source': 'derived_capability_match', 'binding_status': 'derived', 'required_capabilities': ['standard_deviation'], 'matched_capabilities': ['standard_deviation'], 'selected_operation': 'standard_deviation_computation', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.statistics.descriptive_statistics_domain', 'entrypoint': 'build_descriptive_statistics_matrix', 'allowed_operations': ['compute_arithmetic_mean_from_raw_values', 'compute_arithmetic_mean_from_frequency_table', 'compute_weighted_mean', 'compute_median_from_raw_values', 'compute_mode_from_raw_values', 'compute_mode_from_frequency_table', 'compute_range', 'compute_population_variance', 'compute_population_standard_deviation', 'compute_sample_variance', 'compute_sample_standard_deviation', 'complete_descriptive_statistics_table', 'compute_quartiles_and_iqr', 'compare_dispersion', 'conceptual_dispersion_judgment'], 'curriculum_profile': 'vocational_high_b'}, 'question_text': '已知A組樣本的數值資料為 \\(x_i\\)，B組樣本的數值資料為 \\(y_i=3x_i + 2\\)。若A組樣本的標準差為1，則B組樣本的標準差為何？ (A) 1 (B) 2 (C) 3 (D) 4。', 'source_answer_text': 'C'},
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
        domain_operation="compute_population_standard_deviation",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
