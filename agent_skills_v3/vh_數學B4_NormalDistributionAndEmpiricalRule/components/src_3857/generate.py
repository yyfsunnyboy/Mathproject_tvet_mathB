from __future__ import annotations
from typing import Any
from core.domain.statistics.descriptive_statistics_domain import build_descriptive_statistics_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "multi_blank"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "empirical_rule_population_count"
TEXTBOOK_EXAMPLE_ID = 3857
DEFAULT_COMPONENT_ID = "src_3857"
SKILL_ID = "vh_數學B4_NormalDistributionAndEmpiricalRule"

def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    constraints = {
        "question_text": "某校 1000 個學生，英文成績呈常態分配，平均 60 分，標準差 10 分。求：(1) 高於 60 分人數；(2) 50 分以下人數；(3) 50~70 分人數。",
        "textbook_example_id": 3857,
        "presentation_mode": "multi_blank",
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
        component_id="src_3857",
        textbook_example_id=3857,
        answer_schema_key="multi_part",
        domain_operation="empirical_rule_population_count",
        seed=seed,
    )
    payload["skill_id"] = SKILL_ID
    payload["checker_key"] = "multi_part_answer_checker"
    payload["equivalence_type"] = "multi_part_answer"
    
    if "answer_contract" not in payload:
        payload["answer_contract"] = {}
    payload["answer_contract"]["equivalence_type"] = "multi_part_answer"
    payload["answer_contract"]["checker_key"] = "multi_part_answer_checker"
    
    return payload
