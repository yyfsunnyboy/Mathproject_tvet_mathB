from __future__ import annotations

import re
from typing import Any

from core.gencode.task_families import (
    ABSOLUTE_VALUE_INEQUALITY_FAMILY,
    CLASSIFY_QUADRANT_FAMILY,
    DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
    DIVISION_POINT_COORDINATES_FAMILY,
    DIVISION_POINT_COORDINATES_TASKS,
    QUADRATIC_INEQUALITY_FAMILY,
    QUADRATIC_INEQUALITY_TASKS,
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

QUADRATIC_RATIONAL_SCALAR_TASKS = frozenset(
    {
        "quadratic_vertex_or_parameter_computation",
        "compute_quadratic_vertex",
        "compute_quadratic_axis_of_symmetry",
        "quadratic_vertex_axis_identification",
    }
)

_QUADRATIC_RATIONAL_TOKENS = frozenset(
    {
        "quadratic_vertex_or_parameter_computation",
        "compute_quadratic_vertex",
        "compute_quadratic_axis_of_symmetry",
        "completing_the_square",
        "complete_square",
        "axis_of_symmetry",
    }
)

CLASSIFICATION_TASKS = frozenset({"classify_quadrant", "identify_concept", "choose_name"})

_INTERVAL_TASKS = frozenset(
    {
        "solve_absolute_value_inequality",
        "expand_absolute_value_inequality",
        "interpret_number_line_interval",
        "solve_inequality",
        "solve_quadratic_inequality",
        "interpret_quadratic_inequality_solution_set",
    }
)

_FACTORING_TASKS = frozenset(
    {
        "factor_quadratic_by_cross_multiplication",
        "solve_quadratic_by_factoring",
    }
)

QUADRATIC_INEQUALITY_INTERVAL_SOLUTION_TASKS = frozenset(
    {
        "solve_quadratic_inequality",
        "interpret_quadratic_inequality_solution_set",
        "applied_quadratic_inequality_problem",
        "solve_quadratic_inequality_parameter_range",
    }
)

QUADRATIC_INEQUALITY_SOLUTION_TASKS = QUADRATIC_INEQUALITY_INTERVAL_SOLUTION_TASKS | frozenset(
    {
        "solve_quadratic_inequality_special_cases",
        "reverse_quadratic_inequality_coefficients",
    }
)

QUADRATIC_INEQUALITY_SPECIAL_CASE_ANSWERS = frozenset({"無解", "任意實數"})

_INTERVAL_ACCEPTED_FORMATS = [
    "-5 <= x <= 1",
    "(-5, 1]",
    "x in [-5,1]",
    "x<-2 or x>5",
    "-2<x<5",
    "x<=-2 or x>=5",
]

_RADICAL_IN_ANSWER = re.compile(r"\\sqrt|sqrt\s*\(|√", re.I)
_NUMERIC_ANSWER = re.compile(r"^-?\d+(?:\.\d+)?$")
_RATIONAL_IN_ANSWER = re.compile(r"^-?\d+\s*/\s*-?\d+$")


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


def _answers_suggest_rational(features: list[dict[str, Any]] | None) -> bool:
    answers = _feature_answers(features)
    if not answers:
        return False
    return any("/" in a or _RATIONAL_IN_ANSWER.search(a) for a in answers)


def is_quadratic_rational_scalar_semantic(
    *,
    problem_type_id: str = "",
    target_task: str = "",
    task_family: str = "",
    math_objects: list[str] | None = None,
) -> bool:
    """True for quadratic vertex/completing-square scalar tasks that may be fractional.

    Source examples for these tasks often have integer answers, but generators can
    legitimately emit values such as -b/(2a) or (4ac-b^2)/(4a).
    """
    task = str(target_task or "").strip()
    family = str(task_family or task_family_for_task(task)).strip()
    if task in QUADRATIC_RATIONAL_SCALAR_TASKS:
        return True
    combined = " ".join(
        [
            str(problem_type_id or ""),
            task,
            family,
            " ".join(str(m or "") for m in (math_objects or [])),
        ]
    ).lower()
    return any(token in combined for token in _QUADRATIC_RATIONAL_TOKENS)


def is_quadratic_inequality_semantic(
    *,
    problem_type_id: str = "",
    target_task: str = "",
    task_family: str = "",
    math_objects: list[str] | None = None,
) -> bool:
    task = str(target_task or "").strip()
    family = str(task_family or task_family_for_task(task)).strip()
    if task in QUADRATIC_INEQUALITY_TASKS or family == QUADRATIC_INEQUALITY_FAMILY:
        return True
    combined = " ".join(
        [
            str(problem_type_id or ""),
            task,
            family,
            " ".join(str(m or "") for m in (math_objects or [])),
        ]
    ).lower()
    tokens = (
        "quadratic_inequality",
        "factor_quadratic",
        "quadratic_trinomial",
        "cross_multiplication",
        "factoring_expression",
        "inequality_solution",
        "solution_set",
    )
    return any(token in combined for token in tokens)


def is_quadratic_inequality_interval_semantic(
    *,
    problem_type_id: str = "",
    target_task: str = "",
    task_family: str = "",
    math_objects: list[str] | None = None,
) -> bool:
    """True when answer must be an interval/union (interval_checker), not numeric/expression."""
    task = str(target_task or "").strip()
    family = str(task_family or task_family_for_task(task)).strip()
    if task in QUADRATIC_INEQUALITY_INTERVAL_SOLUTION_TASKS:
        return True
    if task in {
        "solve_quadratic_inequality_special_cases",
        "reverse_quadratic_inequality_coefficients",
    }:
        return False
    combined = " ".join(
        [
            str(problem_type_id or ""),
            task,
            family,
            " ".join(str(m or "") for m in (math_objects or [])),
        ]
    ).lower()
    return any(
        token in combined
        for token in (
            "solve_quadratic_inequality",
            "interpret_quadratic_inequality_solution_set",
            "inequality_solution",
            "solution_set",
        )
    )


def build_interval_answer_contract(*, existing_ac: dict[str, Any] | None = None) -> dict[str, Any]:
    """Canonical interval contract for quadratic-inequality solution tasks."""
    base = dict(existing_ac or {})
    base.update(
        {
            "choices_required": False,
            "choice_count": None,
            "correct_choice_count": None,
            "frontend_render_choices": False,
            "source_has_choices": False,
            "answer_type": "interval",
            "answer_shape": "interval_or_union",
            "answer_semantics": "interval_union",
            "answer_equivalence": "interval_equivalence",
            "equivalence_type": "interval_equivalence",
            "checker": "interval_checker",
            "checker_key": "interval_checker",
            "presentation_mode": "short_answer",
            "selected_checker": "interval_checker",
            "checker_selection_reason": "quadratic_inequality_interval_solution",
            "accepted_formats": list(_INTERVAL_ACCEPTED_FORMATS),
        }
    )
    return base


def build_quadratic_inequality_parameter_range_contract(
    *, existing_ac: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Interval contract for parameter k/m range from D<0 definite-sign constraints."""
    base = dict(existing_ac or {})
    base.update(
        {
            "choices_required": False,
            "choice_count": None,
            "correct_choice_count": None,
            "frontend_render_choices": False,
            "source_has_choices": False,
            "answer_type": "interval",
            "answer_shape": "parameter_interval",
            "answer_semantics": "parameter_range",
            "answer_equivalence": "interval_equivalence",
            "equivalence_type": "interval_equivalence",
            "checker": "interval_checker",
            "checker_key": "interval_checker",
            "presentation_mode": "short_answer",
            "selected_checker": "interval_checker",
            "checker_selection_reason": "quadratic_inequality_parameter_range",
            "accepted_formats": ["m>1", "k<-2", "m>=1", "k<=-2", "a>3/2"],
            "answer_format_example": "m>1",
        }
    )
    return base


def build_quadratic_inequality_special_case_contract(
    *, existing_ac: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Text-short contract for 無解 / 任意實數 special-case inequality solutions."""
    base = dict(existing_ac or {})
    base.update(
        {
            "choices_required": False,
            "choice_count": None,
            "correct_choice_count": None,
            "frontend_render_choices": False,
            "source_has_choices": False,
            "answer_type": "text_short",
            "answer_shape": "text_short",
            "answer_semantics": "special_case_solution_label",
            "answer_equivalence": "exact_string",
            "equivalence_type": "exact_string",
            "checker": "text_short_checker",
            "checker_key": "text_short_checker",
            "presentation_mode": "short_answer",
            "selected_checker": "text_short_checker",
            "checker_selection_reason": "quadratic_inequality_special_case",
            "accepted_formats": ["無解", "任意實數"],
            "answer_format_example": "任意實數",
        }
    )
    return base


def build_reverse_quadratic_coefficients_integer_contract(
    *, existing_ac: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Integer contract for reverse-engineering hidden quadratic coefficients."""
    base = dict(existing_ac or {})
    base.update(
        {
            "choices_required": False,
            "choice_count": None,
            "correct_choice_count": None,
            "frontend_render_choices": False,
            "source_has_choices": False,
            "answer_type": "integer",
            "answer_shape": "scalar",
            "answer_semantics": "numeric_exact",
            "answer_equivalence": "numeric_exact",
            "equivalence_type": "numeric_exact",
            "checker": "integer_checker",
            "checker_key": "integer_checker",
            "presentation_mode": "short_answer",
            "selected_checker": "integer_checker",
            "checker_selection_reason": "quadratic_inequality_reverse_coefficient",
            "accepted_formats": ["2", "-3", "5"],
        }
    )
    return base


def is_coordinate_pair_semantic(
    *,
    answer_type: str = "",
    target_task: str = "",
    task_family: str = "",
    answer_shape: str = "",
    math_objects: list[str] | None = None,
) -> bool:
    at = str(answer_type or "").strip()
    shape = str(answer_shape or "").strip()
    task = str(target_task or "").strip()
    family = str(task_family or task_family_for_task(task)).strip()
    mos = set(math_objects or [])
    return (
        at in {"ordered_pair", "coordinate_pair"}
        or shape == "coordinate_pair"
        or "coordinate_pair" in mos
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
            "answer_shape": "single_choice",
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

    if is_coordinate_pair_semantic(answer_type=at, target_task=task, task_family=family, math_objects=mos):
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
            "answer_equivalence": "ordered_tuple_exact",
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

    if task == "solve_quadratic_inequality_special_cases":
        return build_quadratic_inequality_special_case_contract(existing_ac=base)

    if task == "solve_quadratic_inequality_parameter_range":
        return build_quadratic_inequality_parameter_range_contract(existing_ac=base)

    if task == "reverse_quadratic_inequality_coefficients":
        return build_reverse_quadratic_coefficients_integer_contract(existing_ac=base)

    if task in QUADRATIC_INEQUALITY_INTERVAL_SOLUTION_TASKS or is_quadratic_inequality_interval_semantic(
        target_task=task,
        task_family=family,
        math_objects=mos,
    ):
        return build_interval_answer_contract(existing_ac=base)

    if task in _INTERVAL_TASKS or family == ABSOLUTE_VALUE_INEQUALITY_FAMILY:
        return build_interval_answer_contract(existing_ac=base)

    if task in _FACTORING_TASKS or (
        is_quadratic_inequality_semantic(target_task=task, task_family=family, math_objects=mos)
        and task not in _INTERVAL_TASKS
    ):
        return {
            **base,
            "answer_type": "expression",
            "answer_shape": "factored_expression",
            "answer_equivalence": "algebraic_equivalent",
            "equivalence_type": "algebraic_equivalent",
            "checker": "expression_checker",
            "checker_key": "expression_checker",
            "presentation_mode": "short_answer",
            "selected_checker": "expression_checker",
            "checker_selection_reason": "quadratic_factoring_expression",
            "accepted_formats": ["(x-5)(x+3)", "(2x-1)(x+5)", "2(x-1)(3x+2)"],
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

    if is_quadratic_rational_scalar_semantic(
        target_task=task,
        task_family=family,
        math_objects=mos,
    ) and not source_has_choices:
        if _answers_suggest_rational(cluster_features):
            return {
                **base,
                "answer_type": "rational",
                "answer_shape": "scalar",
                "answer_equivalence": "rational_equivalent",
                "equivalence_type": "rational_equivalent",
                "checker": "rational_checker",
                "checker_key": "rational_checker",
                "presentation_mode": "short_answer",
                "source_has_choices": source_has_choices,
                "selected_checker": "rational_checker",
                "checker_selection_reason": "quadratic_vertex_rational_from_source_answers",
                "accepted_formats": ["-9/8", "3/2", "-2", "1.5"],
            }
        if at == "integer" or _answers_suggest_numeric_only(cluster_features):
            return {
                **base,
                "answer_type": "integer",
                "answer_shape": "scalar",
                "answer_equivalence": "numeric_exact",
                "equivalence_type": "numeric_exact",
                "checker": "integer_checker",
                "checker_key": "integer_checker",
                "presentation_mode": "short_answer",
                "source_has_choices": source_has_choices,
                "selected_checker": "integer_checker",
                "checker_selection_reason": "quadratic_vertex_integer_capable",
                "accepted_formats": ["-9", "0", "3", "12"],
            }
        return {
            **base,
            "answer_type": "rational",
            "answer_shape": "scalar",
            "answer_equivalence": "rational_equivalent",
            "equivalence_type": "rational_equivalent",
            "checker": "rational_checker",
            "checker_key": "rational_checker",
            "presentation_mode": "short_answer",
            "source_has_choices": source_has_choices,
            "selected_checker": "rational_checker",
            "checker_selection_reason": "quadratic_vertex_rational_capable",
            "accepted_formats": ["-9/8", "3/2", "-2", "1.5"],
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
