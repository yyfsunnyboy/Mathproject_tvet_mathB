from __future__ import annotations

from typing import Any

from core.gencode.runtime_skill_wrapper import check_answer, generate_for_skill

SKILL_ID = "vh_數學B1_QuadraticFunctionGraph"
GENERATOR_KEYS = [
    "vh_數學B1_QuadraticFunctionGraph:quadratic_graph_vertex_axis_choice:draft_v1",
    "vh_數學B1_QuadraticFunctionGraph:quadratic_graph_translation_fill_blank:draft_v1",
    "vh_數學B1_QuadraticFunctionGraph:quadratic_graph_translation_short_answer:draft_v1",
    "vh_數學B1_QuadraticFunctionGraph:quadratic_vertex_form_properties:draft_v1",
    "vh_數學B1_QuadraticFunctionGraph:quadratic_standard_to_vertex_properties:draft_v1",
]
GENERATOR_SPECS = [
    {
        "problem_type_id": "quadratic_graph_vertex_axis_choice",
        "checker_key": "choice_label_checker",
        "equivalence_type": "choice_label",
        "generator_readiness": "runtime_ready",
    },
    {
        "problem_type_id": "quadratic_graph_translation_fill_blank",
        "checker_key": "text_short_checker",
        "equivalence_type": "exact_string",
        "generator_readiness": "runtime_ready",
    },
    {
        "problem_type_id": "quadratic_graph_translation_short_answer",
        "checker_key": "text_short_checker",
        "equivalence_type": "exact_string",
        "generator_readiness": "runtime_ready",
    },
    {
        "problem_type_id": "quadratic_vertex_form_properties",
        "checker_key": "choice_label_checker",
        "equivalence_type": "choice_label",
        "generator_readiness": "runtime_ready",
    },
    {
        "problem_type_id": "quadratic_standard_to_vertex_properties",
        "checker_key": "choice_label_checker",
        "equivalence_type": "choice_label",
        "generator_readiness": "runtime_ready",
    },
]


def generate(level: int = 1, seed: int | None = None, difficulty: int | str | None = None, **kwargs) -> dict[str, Any]:
    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)


def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None):
    return check_answer(user_answer, correct_answer, payload=question_payload)
