from __future__ import annotations

import re
from typing import Any

from core.gencode.task_families import (
    ABSOLUTE_VALUE_INEQUALITY_FAMILY,
    CLASSIFY_QUADRANT_FAMILY,
    DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
    DIVISION_POINT_COORDINATES_FAMILY,
    DIVISION_POINT_COORDINATES_TASKS,
    SOLVE_UNKNOWN_COORDINATE_TASKS,
    task_family_for_task,
)

DISTANCE_COMPUTE_TASKS = frozenset(
    {
        "compute_distance",
        "compute_distance_between_two_points",
        "verify_distance_between_two_points",
        "compare_distances_between_points",
    }
)

NUMERIC_SCALAR_TASKS = frozenset(
    {
        "compute_numeric",
        "compute_value",
        "compute_probability",
        "count_arrangements",
        "read_table",
        "read_graph",
        "simplify_expression",
        "solve_equation",
    }
)

CLASSIFICATION_TASKS = frozenset({"classify_quadrant", "identify_concept", "choose_name"})

_INTERVAL_TASKS = frozenset(
    {
        "solve_absolute_value_inequality",
        "expand_absolute_value_inequality",
        "interpret_number_line_interval",
        "solve_inequality",
    }
)

_RADICAL_IN_ANSWER = re.compile(r"\\sqrt|sqrt\s*\(|√", re.I)
_NUMERIC_ANSWER = re.compile(r"^-?\d+(?:\.\d+)?$")


def _feature_answers(features: list[dict[str, Any]] | None) -> list[str]:
    out: list[str] = []
    for f in features or []:
        if not isinstance(f, dict):
            continue
        ans = str(f.get("answer", "")).strip()
        if ans:
            out.append(ans)
    return out


def _answers_suggest_radical(features: list[dict[str, Any]] | None) -> bool:
    answers = _feature_answers(features)
    if any(_RADICAL_IN_ANSWER.search(a) for a in answers):
        return True
    if not answers:
        return True
    return not all(_NUMERIC_ANSWER.match(a) for a in answers)


def _answers_suggest_numeric_only(features: list[dict[str, Any]] | None) -> bool:
    answers = _feature_answers(features)
    return bool(answers) and all(_NUMERIC_ANSWER.match(a) for a in answers)


def is_coordinate_pair_semantic(
    *,
    answer_type: str = "",
    target_task: str = "",
    task_family: str = "",
    answer_shape: str = "",
) -> bool:
    at = str(answer_type or "").strip()
    shape = str(answer_shape or "").strip()
    task = str(target_task or "").strip()
    family = str(task_family or task_family_for_task(task)).strip()
    return (
        at in {"ordered_pair", "coordinate_pair"}
        or shape == "coordinate_pair"
        or task in DIVISION_POINT_COORDINATES_TASKS
        or family == DIVISION_POINT_COORDINATES_FAMILY
    )


def presentation_mode_for_features(
    answer_type: str,
    cluster_features: list[dict[str, Any]] | None,
) -> str:
    at = str(answer_type or "").strip()
    if at == "single_choice":
        return "single_choice"
    if cluster_features and any(f.get("has_choices") for f in cluster_features if isinstance(f, dict)):
        return "single_choice"
    return "short_answer"


def checker_selection_reason(
    *,
    answer_type: str,
    target_task: str,
    task_family: str,
    has_choices: bool,
    answer_shape: str = "",
) -> str:
    if is_coordinate_pair_semantic(
        answer_type=answer_type, target_task=target_task, task_family=task_family, answer_shape=answer_shape
    ):
        if has_choices and str(answer_type or "").strip() not in {"single_choice", "multi_choice"}:
            return "coordinate_pair_semantic_source_has_choices_not_overriding_checker"
        return "coordinate_pair_semantic"
    if str(answer_type or "").strip() == "single_choice" or (
        has_choices and str(answer_type or "").strip() in {"single_choice", "multi_choice", "choice", "choice_label"}
    ):
        return "explicit_single_choice"
    return "task_family_default"


def infer_answer_contract_from_problem_context(
    *,
    answer_type: str,
    target_task: str,
    task_family: str = "",
    math_objects: list[str] | None = None,
    cluster_features: list[dict[str, Any]] | None = None,
    has_choices: bool = False,
) -> dict[str, Any]:
    """Generic answer_contract inference from task / family / math objects (not skill_id)."""
    at = str(answer_type or "").strip()
    task = str(target_task or "").strip()
    family = str(task_family or task_family_for_task(task)).strip()
    mos = list(math_objects or [])
    if cluster_features:
        if any(f.get("has_choices") for f in cluster_features if isinstance(f, dict)):
            has_choices = True
        if not mos:
            for f in cluster_features:
                if isinstance(f, dict):
                    mos.extend(f.get("math_objects", []) or [])

    base = {
        "choices_required": False,
        "choice_count": None,
        "correct_choice_count": None,
        "frontend_render_choices": False,
    }
    presentation = presentation_mode_for_features(at, cluster_features)
    source_has_choices = bool(has_choices)

    if at == "single_choice" or (
        has_choices and at in {"single_choice", "multi_choice", "choice", "choice_label"}
    ):
        return {
            **base,
            "answer_type": "single_choice",
            "answer_shape": "choice_label",
            "answer_semantics": "choice_label",
            "answer_equivalence": "choice_label",
            "checker": "choice_label_checker",
            "presentation_mode": "single_choice",
            "source_has_choices": True,
            "selected_checker": "choice_label_checker",
            "checker_selection_reason": checker_selection_reason(
                answer_type=at, target_task=task, task_family=family, has_choices=True
            ),
            "choices_required": True,
            "choice_count": 4,
            "correct_choice_count": 1,
            "frontend_render_choices": True,
            "accepted_formats": ["A", "B", "C", "D"],
        }

    if is_coordinate_pair_semantic(answer_type=at, target_task=task, task_family=family):
        reason = checker_selection_reason(
            answer_type=at,
            target_task=task,
            task_family=family,
            has_choices=source_has_choices,
            answer_shape="coordinate_pair",
        )
        return {
            **base,
            "answer_type": "ordered_pair",
            "answer_shape": "coordinate_pair",
            "answer_semantics": "coordinate_pair",
            "answer_equivalence": "coordinate_pair_equivalence",
            "checker": "coordinate_pair_checker",
            "presentation_mode": presentation,
            "source_has_choices": source_has_choices,
            "selected_checker": "coordinate_pair_checker",
            "checker_selection_reason": reason,
            "accepted_formats": ["(0,-2)", "0,-2", "（0，-2）", "x=0,y=-2", "(0, -2)", "P(0,-2)"],
        }

    if task in SOLVE_UNKNOWN_COORDINATE_TASKS or at == "set":
        return {
            **base,
            "answer_type": "solution_set",
            "answer_shape": "unordered_set",
            "answer_equivalence": "unordered_solution_set",
            "checker": "solution_set_checker",
            "accepted_formats": ["-3, 7", "7, -3", "{-3, 7}", "k=-3 或 k=7", "-3 或 7"],
        }

    if task in CLASSIFICATION_TASKS or family == CLASSIFY_QUADRANT_FAMILY:
        return {
            **base,
            "answer_type": "classification",
            "answer_shape": "quadrant_label",
            "answer_equivalence": "normalized_label",
            "checker": "quadrant_checker",
            "accepted_formats": ["第一象限", "第二象限", "2", "II"],
        }

    if task in _INTERVAL_TASKS or family == ABSOLUTE_VALUE_INEQUALITY_FAMILY:
        return {
            **base,
            "answer_type": "interval",
            "answer_shape": "interval_or_union",
            "answer_equivalence": "interval_equivalence",
            "checker": "interval_checker",
            "accepted_formats": ["-5 <= x <= 1", "(-5, 1]", "x in [-5,1]"],
        }

    if task in DISTANCE_COMPUTE_TASKS or (
        family == DISTANCE_BETWEEN_TWO_POINTS_FAMILY and task not in SOLVE_UNKNOWN_COORDINATE_TASKS
    ):
        radical_likely = (
            "distance_formula" in mos
            or "segment_length" in mos
            or _answers_suggest_radical(cluster_features)
        )
        if radical_likely:
            return {
                **base,
                "answer_type": "numeric_or_radical",
                "answer_shape": "scalar",
                "answer_equivalence": "math_expression_equivalence",
                "checker": "expression_equivalence_checker",
                "accepted_formats": ["5", "5.0", "\\sqrt{13}", "sqrt(13)", "2\\sqrt{5}", "2√5"],
            }
        return {
            **base,
            "answer_type": "numeric",
            "answer_shape": "scalar",
            "answer_equivalence": "numeric_equivalence",
            "checker": "numeric_checker",
            "accepted_formats": ["5", "5.0", "-3"],
        }

    if at in {"numeric", "integer"} or "evaluate_function" in task or task in NUMERIC_SCALAR_TASKS or _answers_suggest_numeric_only(cluster_features):
        is_int = (at == "integer" or "integer" in task or _answers_suggest_numeric_only(cluster_features))
        return {
            **base,
            "answer_type": "integer" if is_int else "numeric",
            "answer_shape": "scalar",
            "answer_equivalence": "numeric_exact",
            "checker": "integer_checker" if is_int else "numeric_checker",
            "accepted_formats": ["5", "5.0", "-3"],
        }

    if at == "fraction":
        return {
            **base,
            "answer_type": "fraction",
            "answer_shape": "scalar",
            "answer_equivalence": "fraction_equal",
            "checker": "fraction_checker",
            "accepted_formats": ["1/2", "-3/4"],
        }

    if at == "expression" or _RADICAL_IN_ANSWER.search(" ".join(_feature_answers(cluster_features))):
        return {
            **base,
            "answer_type": "numeric_or_radical",
            "answer_shape": "scalar",
            "answer_equivalence": "math_expression_equivalence",
            "checker": "expression_equivalence_checker",
            "accepted_formats": ["\\sqrt{2}", "2x+1"],
        }

    return {
        **base,
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "answer_equivalence": "normalized_text_equivalence",
        "checker": "text_checker",
        "accepted_formats": [],
    }
