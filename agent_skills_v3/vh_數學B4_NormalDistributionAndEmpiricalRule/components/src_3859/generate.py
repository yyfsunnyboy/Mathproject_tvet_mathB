from __future__ import annotations
from typing import Any
from core.domain.statistics.descriptive_statistics_domain import build_descriptive_statistics_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "compare_distribution_spread"
TEXTBOOK_EXAMPLE_ID = 3859
DEFAULT_COMPONENT_ID = "src_3859"
SKILL_ID = "vh_數學B4_NormalDistributionAndEmpiricalRule"

def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    constraints = {
        "question_text": "如圖所示，有甲、乙兩班的成績直方圖，試比較兩班成績的標準差大小。",
        "textbook_example_id": 3859,
        "presentation_mode": "single_choice",
    }
    matrix = build_descriptive_statistics_matrix(
        seed=seed,
        domain_operation="compare_distribution_spread",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints=constraints,
    )
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id="src_3859",
        textbook_example_id=3859,
        answer_schema_key="choice_label",
        domain_operation="compare_distribution_spread",
        seed=seed,
    )
    payload["skill_id"] = SKILL_ID
    payload["checker_key"] = "choice_label_checker"
    payload["equivalence_type"] = "choice_label"

    if "answer_contract" not in payload:
        payload["answer_contract"] = {}
    payload["answer_contract"]["equivalence_type"] = "choice_label"
    payload["answer_contract"]["checker_key"] = "choice_label_checker"

    # Promote image_base64 to top-level so the renderer can display it.
    # The adapter stores the chart inside visual_spec (and table_data) but not
    # at the root level; promote it here without modifying shared adapter code.
    if not payload.get("image_base64"):
        vs = payload.get("visual_spec") or {}
        img = vs.get("image_base64") or (payload.get("table_data") or {}).get("image_base64") or ""
        if img:
            payload["image_base64"] = img

    return payload
