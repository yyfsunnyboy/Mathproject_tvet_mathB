from __future__ import annotations
from typing import Any
from core.domain.statistics.descriptive_statistics_domain import build_descriptive_statistics_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "empirical_rule_population_count"
TEXTBOOK_EXAMPLE_ID = 3898
DEFAULT_COMPONENT_ID = "src_3898"
SKILL_ID = "vh_數學B4_NormalDistributionAndEmpiricalRule"

def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    constraints = {
        "question_text": "某次數學考試共有1000人參加。若成績呈常態分配，且平均數為62分，標準差為8分，則成績低於70分的人數為何？",
        "textbook_example_id": 3898,
        "presentation_mode": "single_choice",
    }
    matrix = build_descriptive_statistics_matrix(
        seed=seed,
        domain_operation="empirical_rule_population_count",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints=constraints,
    )
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id="src_3898",
        textbook_example_id=3898,
        answer_schema_key="choice_label",
        domain_operation="empirical_rule_population_count",
        seed=seed,
    )
    payload["skill_id"] = SKILL_ID
    payload["checker_key"] = "choice_label_checker"
    payload["equivalence_type"] = "choice_label"
    
    if "answer_contract" not in payload:
        payload["answer_contract"] = {}
    payload["answer_contract"]["equivalence_type"] = "choice_label"
    payload["answer_contract"]["checker_key"] = "choice_label_checker"
    
    return payload
