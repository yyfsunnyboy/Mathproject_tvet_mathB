from __future__ import annotations

from typing import Any

from core.domain.statistics.descriptive_statistics_domain import build_descriptive_statistics_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "compute_linear_transform_median_and_range"
TEXTBOOK_EXAMPLE_ID = 3893
DEFAULT_COMPONENT_ID = "src_3893" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_descriptive_statistics_matrix(
        seed=seed,
        domain_operation="compute_linear_transform_median_and_range",
        curriculum_profile="vocational_high_b",
        difficulty_profile="hard",
        constraints={'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B4_LinearTransformationOfData', 'source_example_id': 3893, 'textbook_example_id': 3893, 'source_hash': '60c575c0f1ba5bccce2644cc8cb96f28', 'problem_type_id': 'median_computation', 'required_capabilities': ['median', 'range'], 'classification_source': 'descriptive_statistics_domain_analyzer', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice', 'selected_operation': 'compute_linear_transform_median_and_range', 'domain_operation': 'compute_linear_transform_median_and_range', 'answer_shape': 'single_choice', 'fixed_domain_key': 'statistics.descriptive_statistics'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B4_LinearTransformationOfData', 'source_example_id': 3893, 'textbook_example_id': 3893, 'source_hash': '60c575c0f1ba5bccce2644cc8cb96f28', 'problem_type_id': 'median_computation', 'required_capabilities': ['median', 'range'], 'classification_source': 'descriptive_statistics_domain_analyzer', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice', 'selected_operation': 'compute_linear_transform_median_and_range', 'domain_operation': 'compute_linear_transform_median_and_range', 'answer_shape': 'single_choice', 'fixed_domain_key': 'statistics.descriptive_statistics'}, 'problem_type_id': 'median_computation', 'required_capabilities': ['median', 'range'], 'classification_source': 'descriptive_statistics_domain_analyzer', 'source_hash': '60c575c0f1ba5bccce2644cc8cb96f28', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'source_example_id': 3893, 'answer_type': 'choice', 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '新的中位數和全距與原來的都相同'}, {'key': 'B', 'label': 'B', 'text': '新的中位數和全距與原來的都不相同'}, {'key': 'C', 'label': 'C', 'text': '新的中位數與原來的相同，但全距不相同'}, {'key': 'D', 'label': 'D', 'text': '新的全距與原來的相同，但中位數不同'}], 'source_answer_label': 'D', 'domain_resolution': {'skill_id': 'vh_數學B4_LinearTransformationOfData', 'fixed_domain_key': 'statistics.descriptive_statistics', 'resolution_source': 'derived_capability_match', 'binding_status': 'derived', 'required_capabilities': ['median', 'range'], 'matched_capabilities': ['median', 'range'], 'selected_operation': 'median_computation', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.statistics.descriptive_statistics_domain', 'entrypoint': 'build_descriptive_statistics_matrix', 'allowed_operations': ['compute_arithmetic_mean_from_raw_values', 'compute_arithmetic_mean_from_frequency_table', 'compute_weighted_mean', 'compute_median_from_raw_values', 'compute_mode_from_raw_values', 'compute_mode_from_frequency_table', 'compute_range', 'compute_population_variance', 'compute_population_standard_deviation', 'compute_sample_variance', 'compute_sample_standard_deviation', 'complete_descriptive_statistics_table', 'compute_quartiles_and_iqr', 'compare_dispersion', 'conceptual_dispersion_judgment', 'compute_linear_transform_median_and_range'], 'curriculum_profile': 'vocational_high_b'}, 'question_text': '有20筆資料，在計算時，若把所有數值都減去50以後，再計算中位數和全距，則下列何者正確？ (A)新的中位數和全距與原來的都相同 (B)新的中位數和全距與原來的都不相同 (C)新的中位數與原來的相同，但全距不相同 (D)新的全距與原來的相同，但中位數不同。', 'source_answer_text': 'D'},
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
        domain_operation="compute_linear_transform_median_and_range",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
