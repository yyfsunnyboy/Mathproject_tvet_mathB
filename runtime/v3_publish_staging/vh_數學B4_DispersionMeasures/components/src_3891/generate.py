from __future__ import annotations

from typing import Any

from core.domain.statistics.descriptive_statistics_domain import build_descriptive_statistics_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "conceptual_dispersion_judgment"
TEXTBOOK_EXAMPLE_ID = 3891
DEFAULT_COMPONENT_ID = "src_3891" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_descriptive_statistics_matrix(
        seed=seed,
        domain_operation="conceptual_dispersion_judgment",
        curriculum_profile="vocational_high_b",
        difficulty_profile="hard",
        constraints={'v3_induced_spec': {'classification_status': 'resolved', 'skill_id': 'vh_數學B4_DispersionMeasures', 'source_example_id': 3891, 'textbook_example_id': 3891, 'source_hash': '98c40fc1c7fffa3a0a830d241a245db8', 'problem_type_id': 'conceptual_dispersion_judgment', 'required_capabilities': ['conceptual_dispersion_judgment'], 'classification_source': 'descriptive_statistics_domain_analyzer', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice', 'selected_operation': 'conceptual_dispersion_judgment', 'domain_operation': 'conceptual_dispersion_judgment', 'answer_shape': 'single_choice', 'fixed_domain_key': 'statistics.descriptive_statistics'}, 'phase1_classification': {'classification_status': 'resolved', 'skill_id': 'vh_數學B4_DispersionMeasures', 'source_example_id': 3891, 'textbook_example_id': 3891, 'source_hash': '98c40fc1c7fffa3a0a830d241a245db8', 'problem_type_id': 'conceptual_dispersion_judgment', 'required_capabilities': ['conceptual_dispersion_judgment'], 'classification_source': 'descriptive_statistics_domain_analyzer', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'answer_type': 'choice', 'selected_operation': 'conceptual_dispersion_judgment', 'domain_operation': 'conceptual_dispersion_judgment', 'answer_shape': 'single_choice', 'fixed_domain_key': 'statistics.descriptive_statistics'}, 'problem_type_id': 'conceptual_dispersion_judgment', 'required_capabilities': ['conceptual_dispersion_judgment'], 'classification_source': 'descriptive_statistics_domain_analyzer', 'source_hash': '98c40fc1c7fffa3a0a830d241a245db8', 'presentation_mode': 'single_choice', 'answer_contract': {'answer_type': 'choice', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}, 'source_example_id': 3891, 'answer_type': 'choice', 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '四分位距'}, {'key': 'B', 'label': 'B', 'text': '全距'}, {'key': 'C', 'label': 'C', 'text': '標準差'}, {'key': 'D', 'label': 'D', 'text': '算術平均數'}], 'source_answer_label': 'B', 'domain_resolution': {'skill_id': 'vh_數學B4_DispersionMeasures', 'fixed_domain_key': 'statistics.descriptive_statistics', 'resolution_source': 'derived_capability_match', 'binding_status': 'derived', 'required_capabilities': ['conceptual_dispersion_judgment'], 'matched_capabilities': ['conceptual_dispersion_judgment'], 'selected_operation': 'conceptual_dispersion_judgment', 'registry_revision': '2026-06-23-v1.8', 'domain_module': 'core.domain.statistics.descriptive_statistics_domain', 'entrypoint': 'build_descriptive_statistics_matrix', 'allowed_operations': ['compute_arithmetic_mean_from_raw_values', 'compute_arithmetic_mean_from_frequency_table', 'compute_weighted_mean', 'compute_median_from_raw_values', 'compute_mode_from_raw_values', 'compute_mode_from_frequency_table', 'compute_range', 'compute_population_variance', 'compute_population_standard_deviation', 'complete_descriptive_statistics_table', 'compute_quartiles_and_iqr', 'compare_dispersion', 'conceptual_dispersion_judgment'], 'curriculum_profile': 'vocational_high_b'}, 'question_text': '甲同學想要網購某支特定手機，上網逛了7家購物網站後，告訴好友說：「該款手機的價差在100元以內」。試問甲所說的話中，應用了下列哪一種統計量？ (A)四分位距 (B)全距 (C)標準差 (D)算術平均數。', 'source_answer_text': 'B', 'concept_scenarios': [{'story': '甲同學想要網購某支特定手機，上網逛了7家購物網站後，告訴好友說：「該款手機的價差在100元以內」。試問甲所說的話中，應用了下列哪一種統計量？', 'target_statistic': 'range', 'correct_label': 'B', 'choices': [{'key': 'A', 'label': 'A', 'text': '四分位距'}, {'key': 'B', 'label': 'B', 'text': '全距'}, {'key': 'C', 'label': 'C', 'text': '標準差'}, {'key': 'D', 'label': 'D', 'text': '算術平均數'}]}]},
    )
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
        answer_schema_key="choice_label",
        domain_operation="conceptual_dispersion_judgment",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
