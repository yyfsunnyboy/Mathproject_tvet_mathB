"""Adapter layer between Domain Full Matrix Dictionary and question payloads."""

from __future__ import annotations

import json
import random
from fractions import Fraction
from typing import Any

from core.gencode.resources.rational_display import (
    canonicalize_display_answer,
    canonicalize_multi_part_display,
    canonicalize_part_display_answer,
    fraction_to_plain,
    normalize_fraction_value,
)

MATRIX_REQUIRED_FIELDS = (
    "givens",
    "answer",
    "distractors",
    "explanation_steps",
    "validation_facts",
    "visual_spec",
)

ANSWER_REQUIRED_FIELDS = (
    "canonical_form",
    "general_form",
    "coefficients",
)

# slope and intercept are only available for slope-bearing line types
# (e.g. two_points, point_slope, slope_intercept_equation, etc.).
# Distance-type matrices (distance_from_point_to_line, compare_point_to_line_distances, etc.)
# do not carry slope/intercept. Do not add them to the universal required set.


def validate_domain_matrix(matrix: dict[str, Any], **kwargs: Any) -> bool:
    """Assert that a domain matrix contains all six required top-level fields.

    Accepts ignored **kwargs (component_id, problem_type_id, domain_operation) for
    forward-compatibility with callers that pass schema context alongside the matrix.
    Raises AnswerSchemaMismatchError for missing answer fields so callers can
    distinguish answer-schema violations from structural errors.
    """
    from core.gencode.answer_schema_registry import AnswerSchemaMismatchError

    if not isinstance(matrix, dict):
        raise ValueError("matrix must be a dict.")

    missing = [field for field in MATRIX_REQUIRED_FIELDS if field not in matrix]
    if missing:
        raise ValueError(f"domain matrix missing required fields: {missing}")

    answer = matrix["answer"]
    if not isinstance(answer, dict):
        raise AnswerSchemaMismatchError("matrix['answer'] must be a dict.")

    missing_answer = [field for field in ANSWER_REQUIRED_FIELDS if field not in answer]
    if missing_answer:
        raise AnswerSchemaMismatchError(
            f"matrix['answer'] missing required fields: {missing_answer}"
        )

    if not isinstance(matrix["distractors"], list):
        raise ValueError("matrix['distractors'] must be a list.")
    if not isinstance(matrix["explanation_steps"], list):
        raise ValueError("matrix['explanation_steps'] must be a list.")
    if not isinstance(matrix["validation_facts"], dict):
        raise ValueError("matrix['validation_facts'] must be a dict.")
    if not isinstance(matrix["visual_spec"], dict):
        raise ValueError("matrix['visual_spec'] must be a dict.")
    if not isinstance(matrix["givens"], dict):
        raise ValueError("matrix['givens'] must be a dict.")

    return True


def validate_full_matrix_shell(matrix: dict[str, Any], **kwargs: Any) -> bool:
    """Validate that a matrix contains the required top-level structural fields.

    Unlike validate_domain_matrix, this does NOT inspect the contents of
    matrix['answer'] — it only verifies the six outer shell fields are present
    and correctly typed. Useful for testing broken or partially-constructed answer
    dicts without tripping on the answer-schema gate.
    """
    if not isinstance(matrix, dict):
        raise ValueError("matrix must be a dict.")

    missing = [field for field in MATRIX_REQUIRED_FIELDS if field not in matrix]
    if missing:
        raise ValueError(f"domain matrix missing required fields: {missing}")

    if not isinstance(matrix["answer"], dict):
        raise ValueError("matrix['answer'] must be a dict.")
    if not isinstance(matrix["givens"], dict):
        raise ValueError("matrix['givens'] must be a dict.")
    if not isinstance(matrix["distractors"], list):
        raise ValueError("matrix['distractors'] must be a list.")
    if not isinstance(matrix["explanation_steps"], list):
        raise ValueError("matrix['explanation_steps'] must be a list.")
    if not isinstance(matrix["validation_facts"], dict):
        raise ValueError("matrix['validation_facts'] must be a dict.")
    if not isinstance(matrix["visual_spec"], dict):
        raise ValueError("matrix['visual_spec'] must be a dict.")

    return True


def normalize_domain_matrix(matrix: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Return a JSON-serializable copy of a domain matrix using basic types only.

    Accepts ignored **kwargs (answer_schema_key, component_id, problem_type_id,
    domain_operation) for forward-compatibility with pipeline_orchestrator callers.
    """
    validate_domain_matrix(matrix, **kwargs)
    normalized = _normalize_value(matrix)
    if not isinstance(normalized, dict):
        raise ValueError("normalized matrix must remain a dict.")
    json.dumps(normalized, ensure_ascii=False)
    return normalized


def _build_line_equation_answer_contract(
    *,
    presentation_mode: str,
    answer_type: str,
    semantic_answer: str,
    task_type: str = "",
) -> dict[str, Any]:
    if presentation_mode == "single_choice":
        return {
            "presentation_mode": "single_choice",
            "answer_type": "single_choice",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "answer_equivalence": "choice_label",
            "equivalence": "choice_label",
            "semantic_answer": semantic_answer,
        }
    if task_type == "compare_point_to_line_distances":
        if semantic_answer in {"L_1", "L_2"}:
            return {
                "presentation_mode": "short_answer",
                "answer_type": "text_short",
                "checker": "line_label_checker",
                "checker_key": "line_label_checker",
                "answer_equivalence": "normalized_line_label",
                "equivalence": "normalized_line_label",
                "semantic_answer": semantic_answer,
            }
        else:
            return {
                "presentation_mode": "short_answer",
                "answer_type": "text_short",
                "checker": "text_short_checker",
                "checker_key": "text_short_checker",
                "answer_equivalence": "exact_string",
                "equivalence": "exact_string",
                "semantic_answer": semantic_answer,
            }

    if task_type == "slope_intercept_find_x_intercept":
        return {
            "presentation_mode": "short_answer",
            "answer_type": "rational",
            "checker": "rational_checker",
            "checker_key": "rational_checker",
            "answer_equivalence": "rational_equivalent",
            "equivalence": "rational_equivalent",
            "semantic_answer": semantic_answer,
        }
    if task_type == "slope_intercept_read_slope_and_intercept":
        return {
            "presentation_mode": "short_answer",
            "answer_type": "text_short",
            "checker": "text_short_checker",
            "checker_key": "text_short_checker",
            "answer_equivalence": "exact_string",
            "equivalence": "exact_string",
            "semantic_answer": semantic_answer,
        }
    if task_type == "intercept_form_triangle_area":
        return {
            "presentation_mode": presentation_mode,
            "answer_type": "single_choice" if presentation_mode == "single_choice" else "rational",
            "checker": "choice_label_checker" if presentation_mode == "single_choice" else "rational_checker",
            "checker_key": "choice_label_checker" if presentation_mode == "single_choice" else "rational_checker",
            "answer_equivalence": "choice_label" if presentation_mode == "single_choice" else "rational_equivalent",
            "equivalence": "choice_label" if presentation_mode == "single_choice" else "rational_equivalent",
            "semantic_answer": semantic_answer,
        }
    if task_type == "intercept_form_equation_and_triangle_area":
        return {
            "presentation_mode": "short_answer",
            "answer_type": "multi_part",
            "answer_shape": "multi_part",
            "checker": "multi_part_answer_checker",
            "checker_key": "multi_part_answer_checker",
            "answer_equivalence": "multi_part_answer",
            "equivalence_type": "multi_part_answer",
            "equivalence": "multi_part_answer",
            "semantic_answer": semantic_answer,
            "parts": [
                {
                    "key": "equation",
                    "label": "equation",
                    "checker": "linear_equation_equivalent_checker",
                    "equivalence_type": "linear_equation_equivalent",
                    "expected_answer": semantic_answer.get("equation") if isinstance(semantic_answer, dict) else "",
                    "display_answer": canonicalize_part_display_answer({
                        "checker": "linear_equation_equivalent_checker",
                        "expected_answer": semantic_answer.get("equation") if isinstance(semantic_answer, dict) else "",
                    }),
                },
                {
                    "key": "area",
                    "label": "area",
                    "checker": "rational_checker",
                    "equivalence_type": "rational_equivalent",
                    "expected_answer": semantic_answer.get("area") if isinstance(semantic_answer, dict) else "",
                    "display_answer": canonicalize_part_display_answer({
                        "checker": "rational_checker",
                        "expected_answer": semantic_answer.get("area") if isinstance(semantic_answer, dict) else "",
                    }),
                },
            ],
        }
    if answer_type == "numeric_or_radical":
        return {
            "presentation_mode": "short_answer",
            "answer_type": "numeric_or_radical",
            "checker": "expression_equivalence_checker",
            "checker_key": "expression_equivalence_checker",
            "answer_equivalence": "radical_equivalence",
            "equivalence": "radical_equivalence",
            "semantic_answer": semantic_answer,
        }
    if answer_type in ("rational", "numeric_or_undefined"):
        return {
            "presentation_mode": "short_answer",
            "answer_type": answer_type,
            "checker": "rational_checker",
            "checker_key": "rational_checker",
            "answer_equivalence": "rational_equivalent",
            "equivalence": "rational_equivalent",
            "semantic_answer": semantic_answer,
        }
    return {
        "presentation_mode": "short_answer",
        "answer_type": answer_type,
        "checker": "linear_equation_equivalent_checker",
        "checker_key": "linear_equation_equivalent_checker",
        "answer_equivalence": "linear_equation_equivalent",
        "equivalence": "linear_equation_equivalent",
        "semantic_answer": semantic_answer,
    }


def convert_line_equation_matrix_to_question_payload(
    matrix: dict[str, Any],
    *,
    presentation_mode: str | None = None,
    answer_type: str | None = None,
    problem_type_id: str | None = None,
    component_id: str | None = None,
    textbook_example_id: int | None = None,
    source_kind: str | None = None,
    generator_key: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Map a line-equation domain matrix into a standard outward question payload."""
    domain_operation = str(kwargs.get("domain_operation") or "").strip()
    normalized = normalize_domain_matrix(matrix)
    givens = normalized["givens"]
    answer = normalized["answer"]
    validation_facts = dict(normalized["validation_facts"])
    if domain_operation:
        validation_facts.setdefault("domain_operation", domain_operation)
        validation_facts.setdefault("task_type", domain_operation)
        validation_facts.setdefault("line_type", domain_operation)
    visual_spec = normalized["visual_spec"]
    explanation_steps = normalized["explanation_steps"]
    distractors = normalized["distractors"]

    assert isinstance(givens, dict)
    assert isinstance(answer, dict)
    assert isinstance(validation_facts, dict)
    assert isinstance(visual_spec, dict)
    assert isinstance(explanation_steps, list)
    assert isinstance(distractors, list)

    canonical_raw = answer["canonical_form"]
    canonical = str(canonical_raw)
    semantic_answer: Any = canonical_raw
    question_text = _build_line_equation_question_text(givens, validation_facts)
    mode = str(presentation_mode or "short_answer").strip()
    task_type = str(validation_facts.get("task_type") or validation_facts.get("line_type") or "").strip()
    if mode == "single_choice":
        default_answer_type = "single_choice"
    elif task_type in (
        "slope_from_general_or_intercept_form",
        "slope_of_horizontal_or_vertical_line",
        "slope_from_general_form",
        "parallel_line_slope",
        "perpendicular_line_slope",
    ):
        default_answer_type = "numeric_or_undefined"
    elif task_type in ("perpendicular_condition_parameter", "parallel_condition_parameter"):
        default_answer_type = "rational"
    elif task_type == "intercept_form_triangle_area":
        default_answer_type = "rational"
    elif task_type == "intercept_form_equation_and_triangle_area":
        default_answer_type = "multi_part"
    elif task_type == "slope_intercept_find_x_intercept":
        default_answer_type = "rational"
    elif task_type == "slope_intercept_read_slope_and_intercept":
        default_answer_type = "text_short"
    elif task_type == "distance_from_point_to_line":
        default_answer_type = "rational"
    elif task_type in (
        "distance_from_point_to_line_parameter",
        "compare_point_to_line_distances",
    ):
        default_answer_type = "text_short"
    elif task_type in (
        "distance_between_parallel_lines",
        "solve_parameter_from_parallel_distance",
        "area_using_parallel_distance",
    ):
        default_answer_type = "numeric_or_radical"
    elif task_type == "parallel_lines_distance_single_choice":
        default_answer_type = "single_choice"
    else:
        default_answer_type = "expression"
    resolved_answer_type = str(answer_type or default_answer_type).strip()
    if task_type == "slope_intercept_find_x_intercept" and mode != "single_choice":
        resolved_answer_type = "rational"
    elif task_type == "slope_intercept_read_slope_and_intercept" and mode != "single_choice":
        resolved_answer_type = "text_short"
    elif task_type == "intercept_form_triangle_area" and mode != "single_choice":
        resolved_answer_type = "rational"
    elif task_type == "intercept_form_equation_and_triangle_area":
        resolved_answer_type = "multi_part"
    elif task_type in (
        "distance_between_parallel_lines",
        "solve_parameter_from_parallel_distance",
        "area_using_parallel_distance",
    ) and mode != "single_choice":
        resolved_answer_type = "numeric_or_radical"

    math_objects = _infer_math_objects(validation_facts)
    math_core: dict[str, Any] = {
        "givens": _format_givens_for_hint(givens),
        "raw_givens": givens,
        "target": canonical,
        "math_objects": math_objects,
        "derivation": [str(step) for step in explanation_steps],
        "validation_facts": validation_facts,
    }

    contract_fields = {
        "problem_type_id": problem_type_id,
        "component_id": component_id,
        "textbook_example_id": textbook_example_id,
        "source_kind": source_kind,
        "generator_key": generator_key or component_id,
    }
    metadata: dict[str, Any] = {
        "givens": math_core["givens"],
        "raw_givens": givens,
        "target": canonical,
        "derivation": math_core["derivation"],
        "coefficients": answer.get("coefficients"),
        "general_form": answer.get("general_form"),
        "line_equation": answer.get("line_equation") or canonical,
        "presentation_mode": mode,
        "answer_type": resolved_answer_type,
        "semantic_answer": semantic_answer,
    }
    for key, value in contract_fields.items():
        if value is not None:
            metadata[key] = value

    if mode == "single_choice":
        if task_type == "compare_line_slopes" or answer.get("choices") or givens.get("choices"):
            choices = _normalize_labeled_choices(answer.get("choices") or givens.get("choices"))
            correct_label = str(answer.get("correct_label") or "").strip()
            correct_choice_text = ""
            for choice in choices:
                if choice["label"] == correct_label:
                    correct_choice_text = str(choice["text"])
                    break
            semantic_answer = correct_choice_text
        elif task_type == "parabola_secant_parallel_line_choice":
            choices = _normalize_labeled_choices(answer.get("choices"))
            correct_label = str(answer.get("correct_label") or "").strip()
            if not choices or not correct_label:
                raise ValueError("unsupported_choices_generator:parabola_secant_choices_missing")
        elif task_type == "intercept_form_triangle_area":
            choices, correct_label = _build_area_choice_options(
                str(semantic_answer),
                seed_text=f"{semantic_answer}|{givens.get('x_intercept')}|{givens.get('y_intercept')}",
            )
        elif task_type == "slope_intercept_find_x_intercept":
            choices, correct_label = _build_x_intercept_choice_options(
                canonical,
                givens,
                seed_text=f"{canonical}|{givens.get('slope')}|{givens.get('y_intercept')}",
            )
        else:
            choices, correct_label = _build_choice_options(canonical, distractors, seed_text=canonical)
        payload_answer = correct_label
        payload_correct = correct_label
        if task_type == "parallel_lines_distance_single_choice":
            semantic_answer = correct_label
            display_answer = correct_label
        else:
            display_answer = _format_latex_display_answer(str(semantic_answer), task_type)
        choices = [
            {**choice, "text": _format_latex_display_answer(str(choice["text"]), task_type)}
            for choice in choices
        ]
        options = [str(choice["text"]) for choice in choices]
        answer_contract = _build_line_equation_answer_contract(
            presentation_mode=mode,
            answer_type=resolved_answer_type,
            semantic_answer=semantic_answer,
            task_type=task_type,
        )
    else:
        choices = []
        options = []
        payload_answer = semantic_answer
        payload_correct = semantic_answer
        display_answer = _format_display_answer(semantic_answer, task_type, resolved_answer_type)
        answer_contract = _build_line_equation_answer_contract(
            presentation_mode=mode,
            answer_type=resolved_answer_type,
            semantic_answer=semantic_answer,
            task_type=task_type,
        )

    # Merge comparison-specific fields into the contract for compare_point_to_line_distances.
    # This populates target_direction, closer_line, farther_line, comparison_relation,
    # comparison_result, and distances — required by validate_comparison_contract.
    if task_type == "compare_point_to_line_distances":
        for _cmp_key in (
            "target_direction",
            "closer_line",
            "farther_line",
            "comparison_relation",
            "comparison_result",
            "distances",
        ):
            if _cmp_key in answer and _cmp_key not in answer_contract:
                answer_contract[_cmp_key] = answer[_cmp_key]

    # Merge scalar-topology fields for the single_choice_scalar distance type.
    # validate_single_choice_scalar_topology checks choice_value_shape and solution_cardinality
    # from the answer_contract.
    if task_type == "distance_from_point_to_line_parameter_single_choice_scalar":
        for _sc_key in ("choice_value_shape", "solution_cardinality"):
            if _sc_key in answer and _sc_key not in answer_contract:
                answer_contract[_sc_key] = answer[_sc_key]

    payload: dict[str, Any] = {
        "question_text": question_text,
        "question": question_text,
        "correct_answer": payload_correct,
        "answer": payload_answer,
        "display_answer": display_answer,
        "semantic_answer": semantic_answer,
        "choices": choices,
        "options": options,
        "visual_spec": visual_spec,
        "math_core": math_core,
        "presentation_mode": mode,
        "answer_type": resolved_answer_type,
        "metadata": metadata,
        "answer_contract": answer_contract,
        "checker": answer_contract.get("checker"),
        "checker_type": answer_contract.get("checker"),
        "equivalence": answer_contract.get("answer_equivalence"),
    }
    if problem_type_id:
        payload["problem_type_id"] = problem_type_id
    if component_id:
        payload["component_id"] = component_id
    if textbook_example_id is not None:
        payload["textbook_example_id"] = textbook_example_id
    if source_kind:
        payload["source_kind"] = source_kind
    if generator_key or component_id:
        payload["generator_key"] = generator_key or component_id
    return payload


def _normalize_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return value.numerator
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {str(key): _normalize_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_value(item) for item in value]
    if isinstance(value, set):
        return [_normalize_value(item) for item in sorted(value, key=str)]
    raise TypeError(f"Unsupported non-JSON-serializable value type: {type(value)!r}")


def _latex_inline(value: Any) -> str:
    return f"\\({_format_latex_math_text(str(value))}\\)"


def _latex_inline_equation(value: Any) -> str:
    return f"\\({_format_latex_math_text(str(value))}\\)"


def _latex_dollar(value: Any) -> str:
    return f"${_format_latex_math_text(str(value))}$"


def _format_latex_display_answer(value: str, task_type: str = "") -> str:
    text = str(value or "").strip()
    if not text:
        return text
    if len(text) == 1 and text.upper() in {"A", "B", "C", "D"}:
        return text.upper()
    if task_type.startswith("slope_intercept"):
        return _latex_inline_equation(canonicalize_display_answer(text))
    if task_type == "intercept_form_triangle_area":
        return _latex_dollar(canonicalize_display_answer(text, answer_type="rational"))
    if task_type == "parabola_secant_parallel_line_choice":
        return _latex_dollar(canonicalize_display_answer(text))
    if _text_needs_math_latex(text):
        return _latex_dollar(text)
    return _format_latex_math_text(text)


def _format_display_answer(value: Any, task_type: str = "", answer_type: str = "") -> Any:
    if str(answer_type or "").strip() == "multi_part" and isinstance(value, dict):
        return canonicalize_multi_part_display(value)
    return _format_latex_display_answer(str(value), task_type)


def _format_latex_math_text(text: str) -> str:
    import re

    normalized = str(text or "").strip().replace("−", "-")
    if normalized.startswith("$") and normalized.endswith("$"):
        normalized = normalized[1:-1].strip()

    def repl_fraction(match: re.Match[str]) -> str:
        return canonicalize_display_answer(match.group(0), answer_type="rational")

    normalized = re.sub(r"(?<![\\\w])[-+]?\d+/\d+", repl_fraction, normalized)
    if "sqrt" in normalized or "*" in normalized:
        try:
            import sympy

            return sympy.latex(sympy.sympify(normalized))
        except Exception:
            normalized = re.sub(r"sqrt\(([^()]+)\)", r"\\sqrt{\1}", normalized)
            normalized = normalized.replace("*", "")
    return normalized


def _text_needs_math_latex(text: str) -> bool:
    return any(token in str(text) for token in ("sqrt(", "\\sqrt", "/", "*"))


def _build_line_equation_question_text(
    givens: dict[str, Any],
    validation_facts: dict[str, Any],
) -> str:
    task_type = str(validation_facts.get("task_type") or validation_facts.get("line_type") or "").strip()
    if not task_type:
        task_type = "point_slope"

    registered_task_types = {
        "point_slope",
        "two_points",
        "horizontal_line",
        "vertical_line",
        "oblique_line",
        "slope_intercept_equation",
        "slope_intercept_find_x_intercept",
        "slope_intercept_read_slope_and_intercept",
        "intercept_form_equation",
        "intercept_form_triangle_area",
        "intercept_form_equation_and_triangle_area",
        "intercept_form_from_intercept_sum_and_slope",
        "parabola_secant_parallel_line_choice",
        "triangle_area_bisector_line_equation",
        "slope_from_general_or_intercept_form",
        "line_through_point_parallel_to_line",
        "line_through_point_perpendicular_to_line",
        "slope_of_horizontal_or_vertical_line",
        "slope_from_general_form",
        "parallel_line_slope",
        "perpendicular_condition_parameter",
        "parallel_condition_parameter",
        "compare_line_slopes",
        "perpendicular_line_slope",
        "line_through_intersection_parallel_to_line",
        "perpendicular_bisector_application",
        "line_through_point_perpendicular_to_segment",
        "distance_from_point_to_line",
        "distance_from_point_to_line_parameter",
        "distance_from_point_to_line_parameter_single_choice_scalar",
        "compare_point_to_line_distances",
        "distance_between_parallel_lines",
        "solve_parameter_from_parallel_distance",
        "construct_parallel_line_at_distance",
        "parallel_lines_distance_single_choice",
        "area_using_parallel_distance",
    }

    if task_type not in registered_task_types:
        raise ValueError(f"unsupported_line_equation_task_type:{task_type}")

    if task_type == "distance_between_parallel_lines":
        line_1 = _format_latex_math_text(givens.get("line_1") or givens.get("equation_1"))
        line_2 = _format_latex_math_text(givens.get("line_2") or givens.get("equation_2"))
        if not line_1 or not line_2:
            raise ValueError("required_line_task_slot_missing:distance_between_parallel_lines:parallel_line_pair")
        return f"試求兩平行線 ${line_1}$ 與 ${line_2}$ 之間的距離。"

    if task_type == "solve_parameter_from_parallel_distance":
        line_1 = _format_latex_math_text(givens.get("line_1"))
        line_2 = _format_latex_math_text(givens.get("line_2"))
        target_distance = _format_latex_math_text(givens.get("target_distance") or "")
        param_name = givens.get("parameter_name") or "k"
        parameter_condition = _format_latex_math_text(givens.get("parameter_condition") or "")
        if not line_1 or not line_2:
            raise ValueError("required_line_task_slot_missing:solve_parameter_from_parallel_distance:parallel_line_pair")
        return (
            f"坐標平面上，若兩平行線 ${line_1}$ 與 ${line_2}$ 的距離為 ${target_distance}$，"
            f"且 ${parameter_condition}$，試求 ${param_name}$ 之值。"
        )

    if task_type == "area_using_parallel_distance":
        point_a = givens.get("point_a")
        line = _format_latex_math_text(givens.get("line"))
        segment_length = _format_latex_math_text(givens.get("segment_length"))
        if point_a is None or not line or segment_length is None:
            raise ValueError("required_line_task_slot_missing:area_using_parallel_distance:givens")
        pt = _format_point_for_question(point_a)
        return (
            f"設 A 點坐標為 {pt}，且 B、C 兩點在直線 $L: {line}$ 上，"
            f"若 $\\overline{{BC}}$ 的長為 ${segment_length}$，試求 △ABC 的面積。"
        )

    if task_type == "parallel_lines_distance_single_choice":
        line_expr = _format_latex_math_text(givens.get("line_expression") or "")
        slope = _format_latex_math_text(givens.get("slope") or "")
        origin_distance = _format_latex_math_text(givens.get("origin_distance") or "")
        a_value = givens.get("a_value")
        return (
            f"已知 $a>0$、$k>0$，且本題 $a={a_value}$。若直線 $L: {line_expr}$ 的斜率為 ${slope}$，"
            f"且點 $(0,0)$ 到直線 $L$ 的距離為 ${origin_distance}$，則 $a+k=$？"
        )

    if task_type == "construct_parallel_line_at_distance":
        line_1 = givens.get("line_1")
        line_2 = givens.get("line_2")
        if not line_1 or not line_2:
            raise ValueError("required_line_task_slot_missing:construct_parallel_line_at_distance:parallel_line_pair")
        return f"試求與 ${line_1}$ 平行且與 ${line_2}$ 相距離的直線方程式。"

    # 1. Slope-Intercept Forms
    if task_type == "slope_intercept_equation":
        if "slope" not in givens:
            raise ValueError("required_line_task_slot_missing:slope_intercept_equation:slope")
        if "y_intercept" not in givens:
            raise ValueError("required_line_task_slot_missing:slope_intercept_equation:y_intercept")
        slope = givens.get("slope")
        y_intercept = givens.get("y_intercept")
        return (
            f"已知直線的斜率為 {_latex_inline(slope)}，且 y 截距為 {_latex_inline(y_intercept)}，"
            "試求此直線方程式。"
        )

    if task_type == "slope_intercept_find_x_intercept":
        if "slope" not in givens:
            raise ValueError("required_line_task_slot_missing:slope_intercept_find_x_intercept:slope")
        if "y_intercept" not in givens:
            raise ValueError("required_line_task_slot_missing:slope_intercept_find_x_intercept:y_intercept")
        slope = givens.get("slope")
        y_intercept = givens.get("y_intercept")
        return (
            f"設直線 L 的斜率為 {_latex_inline(slope)}，且 y 截距為 {_latex_inline(y_intercept)}，"
            "求 L 的 x 截距。"
        )

    if task_type == "slope_intercept_read_slope_and_intercept":
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:slope_intercept_read_slope_and_intercept:equation")
        equation = givens.get("equation")
        return f"已知直線方程式為 {_latex_inline_equation(equation)}，判斷其斜率與 y 截距。"

    # 2. Intercept Forms & Word Problems
    if task_type in {
        "intercept_form_equation",
        "intercept_form_triangle_area",
        "intercept_form_equation_and_triangle_area",
        "intercept_form_from_intercept_sum_and_slope",
        "parabola_secant_parallel_line_choice",
        "triangle_area_bisector_line_equation",
    }:
        equation = givens.get("equation")
        x_intercept = givens.get("x_intercept")
        y_intercept = givens.get("y_intercept")
        if task_type == "triangle_area_bisector_line_equation":
            for slot in ("vertex", "edge_p1", "edge_p2", "midpoint"):
                if slot not in givens:
                    raise ValueError(f"required_line_task_slot_missing:triangle_area_bisector_line_equation:{slot}")
            vertex = _format_point_for_question(givens.get("vertex"))
            edge_p1 = _format_point_for_question(givens.get("edge_p1"))
            edge_p2 = _format_point_for_question(givens.get("edge_p2"))
            midpoint = _format_point_for_question(givens.get("midpoint"))
            return (
                f"已知三角形 ABC 中，A={edge_p1}、B={vertex}、C={edge_p2}。"
                f"若直線通過 B 並通過 AC 的中點 D={midpoint}，求此平分三角形 ABC 面積的直線方程式。"
            )
        if task_type == "parabola_secant_parallel_line_choice":
            if "p" not in givens or "q" not in givens:
                raise ValueError("required_line_task_slot_missing:parabola_secant_parallel_line_choice:interval_bounds")
            p = givens.get("p")
            q = givens.get("q")
            return (
                f"若 A、B 兩點分別是拋物線 $y=x^2$ 與直線 $x={p}$、$x={q}$ 的交點，"
                "則直線 AB 與下列哪一條直線平行？"
            )
        if task_type == "intercept_form_from_intercept_sum_and_slope":
            if "intercept_sum" not in givens or "slope" not in givens:
                raise ValueError("required_line_task_slot_missing:intercept_form_from_intercept_sum_and_slope:givens")
            intercept_sum = givens.get("intercept_sum")
            slope = givens.get("slope")
            return (
                f"已知直線 L 在兩坐標軸上的截距和為 {_latex_dollar(intercept_sum)}，"
                f"且 L 的斜率為 {_latex_dollar(slope)}，求 L 的方程式。"
            )
        if task_type == "intercept_form_triangle_area":
            if equation:
                return (
                    f"已知直線方程式為 {_latex_dollar(equation)}，求它與 x 軸及 y 軸"
                    "所圍成的三角形面積。"
                )
            return (
                f"已知一直線的 x 截距為 {_latex_dollar(x_intercept)}，y 截距為 "
                f"{_latex_dollar(y_intercept)}，求它與兩坐標軸所圍成的三角形面積。"
            )
        if equation:
            return (
                f"已知直線方程式為 {_latex_dollar(equation)}，將此直線化成截距式，"
                "並求與兩坐標軸所圍成的三角形面積。"
            )
        return (
            f"已知一直線 L 的 x 截距為 {_latex_dollar(x_intercept)}，y 截距為 "
            f"{_latex_dollar(y_intercept)}，試求直線 L 的方程式與兩坐標軸所圍成的三角形面積。"
        )

    # 3. V3 General Form Line types
    if task_type == "slope_from_general_or_intercept_form":
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:slope_from_general_or_intercept_form:equation")
        eq = givens["equation"]
        return f"試求直線的斜率：{_latex_dollar(eq)}。"

    if task_type == "line_through_point_parallel_to_line":
        if "point" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_point_parallel_to_line:point")
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_point_parallel_to_line:reference_line")
        pt = _format_point_for_question(givens["point"])
        eq = givens["equation"]
        return f"已知直線 $L_2$ 通過點 {pt} 且與直線 $L_1: {eq}$ 平行，試求 $L_2$ 的直線方程式。"

    if task_type == "line_through_point_perpendicular_to_line":
        if "point" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_point_perpendicular_to_line:point")
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_point_perpendicular_to_line:reference_line")
        pt = _format_point_for_question(givens["point"])
        eq = givens["equation"]
        return f"已知直線 $L_2$ 通過點 {pt} 且與直線 $L_1: {eq}$ 垂直，試求 $L_2$ 的直線方程式。"

    if task_type == "slope_of_horizontal_or_vertical_line":
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:slope_of_horizontal_or_vertical_line:equation")
        eq = givens["equation"]
        return f"試求直線的斜率：{_latex_dollar(eq)}。"

    if task_type == "slope_from_general_form":
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:slope_from_general_form:equation")
        eq = givens["equation"]
        return f"試求直線的斜率：{_latex_dollar(eq)}。"

    if task_type == "parallel_line_slope":
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:parallel_line_slope:reference_line")
        eq = givens["equation"]
        return f"試求與直線 {_latex_dollar(eq)} 平行之直線斜率。"

    if task_type == "perpendicular_condition_parameter":
        if "equation_1" not in givens:
            raise ValueError("required_line_task_slot_missing:perpendicular_condition_parameter:line_1")
        if "equation_2" not in givens:
            raise ValueError("required_line_task_slot_missing:perpendicular_condition_parameter:line_2")
        eq1 = givens["equation_1"]
        eq2 = givens["equation_2"]
        if "a" not in eq1 and "k" not in eq1:
            raise ValueError("required_line_task_slot_missing:perpendicular_condition_parameter:parameter")
        return f"設兩直線 $L_1: {eq1}$、$L_2: {eq2}$，若 $L_1 \\bot L_2$，則 $a =$"

    if task_type == "parallel_condition_parameter":
        if "equation_1" not in givens:
            raise ValueError("required_line_task_slot_missing:parallel_condition_parameter:line_1")
        if "equation_2" not in givens:
            raise ValueError("required_line_task_slot_missing:parallel_condition_parameter:line_2")
        eq1 = givens["equation_1"]
        eq2 = givens["equation_2"]
        if "a" not in eq1 and "k" not in eq1:
            raise ValueError("required_line_task_slot_missing:parallel_condition_parameter:parameter")
        return f"設兩直線 $L_1: {eq1}$、$L_2: {eq2}$，若 $L_1 \\parallel L_2$，則 $a =$"

    if task_type == "compare_line_slopes":
        if "choices" not in givens:
            raise ValueError("required_line_task_slot_missing:compare_line_slopes:lines")
        return "下列各直線方程式中，具有最大斜率的直線為"

    if task_type == "perpendicular_line_slope":
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:perpendicular_line_slope:reference_line")
        eq = givens["equation"]
        return f"與直線 {_latex_dollar(eq)} 垂直的直線之斜率為"

    if task_type == "line_through_intersection_parallel_to_line":
        if "equation_1" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_intersection_parallel_to_line:line_1")
        if "equation_2" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_intersection_parallel_to_line:line_2")
        if "equation_3" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_intersection_parallel_to_line:reference_line")
        eq1 = givens["equation_1"]
        eq2 = givens["equation_2"]
        eq3 = givens["equation_3"]
        return f"通過兩直線 {_latex_dollar(eq1)} 與 {_latex_dollar(eq2)} 的交點，並與直線 {_latex_dollar(eq3)} 平行的直線方程式為："

    if task_type == "perpendicular_bisector_application":
        if "point_a" not in givens:
            raise ValueError("required_line_task_slot_missing:perpendicular_bisector_application:point_a")
        if "point_b" not in givens:
            raise ValueError("required_line_task_slot_missing:perpendicular_bisector_application:point_b")
        pa = _format_point_for_question(givens["point_a"])
        pb = _format_point_for_question(givens["point_b"])
        return f"已知平面上兩點 A{pa}、B{pb}，求線段 AB 的垂直平分線（中垂線）方程式。"

    if task_type == "line_through_point_perpendicular_to_segment":
        if "point_b" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_point_perpendicular_to_segment:point_b")
        if "point_a" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_point_perpendicular_to_segment:point_a")
        if "point_c" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_point_perpendicular_to_segment:point_c")
        pb = _format_point_for_question(givens["point_b"])
        pa = _format_point_for_question(givens["point_a"])
        pc = _format_point_for_question(givens["point_c"])
        return f"若 A{pa}、B{pb}、C{pc} 為平面上三點，則過點 B 且與直線 AC 垂直的直線方程式為何？"

    if task_type == "distance_from_point_to_line":
        if "point" not in givens:
            raise ValueError("required_line_task_slot_missing:distance_from_point_to_line:point")
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:distance_from_point_to_line:equation")
        pt = _format_point_for_question(givens["point"])
        eq = givens["equation"]
        return f"試求平面上一點 {pt} 到直線 L : {eq} 的距離。"

    if task_type in (
        "distance_from_point_to_line_parameter",
        "distance_from_point_to_line_parameter_single_choice_scalar",
    ):
        if "point" not in givens:
            raise ValueError("required_line_task_slot_missing:distance_from_point_to_line_parameter:point")
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:distance_from_point_to_line_parameter:equation")
        if "distance" not in givens:
            raise ValueError("required_line_task_slot_missing:distance_from_point_to_line_parameter:distance")
        pt = _format_point_for_question(givens["point"])
        eq = givens["equation"]
        dist = givens["distance"]
        var_name = "k"
        if "a" in eq or "a" in str(givens.get("point")):
            var_name = "a"
        return f"若點 {pt} 到直線 L : {eq} 的距離為 {dist}，試求 {var_name} 的值。"

    if task_type == "compare_point_to_line_distances":
        if "point" not in givens:
            raise ValueError("required_line_task_slot_missing:compare_point_to_line_distances:point")
        if "equation_1" not in givens:
            raise ValueError("required_line_task_slot_missing:compare_point_to_line_distances:equation_1")
        if "equation_2" not in givens:
            raise ValueError("required_line_task_slot_missing:compare_point_to_line_distances:equation_2")
        pt = _format_point_for_question(givens["point"])
        eq1 = givens["equation_1"]
        eq2 = givens["equation_2"]
        target_direction = str(givens.get("target_direction") or "closer").strip().lower()
        if target_direction == "closer":
            return f"已知平面上一點 P{pt} 及兩直線 $L_1: {eq1}$、$L_2: {eq2}$，試問點 P 到哪一條直線的距離較近？"
        elif target_direction == "farther":
            return f"已知平面上一點 P{pt} 及兩直線 $L_1: {eq1}$、$L_2: {eq2}$，試問點 P 到哪一條直線的距離較遠？"
        else:
            return f"已知平面有一點 P{pt} 及兩直線 $L_1: {eq1}$ 與 $L_2: {eq2}$，試比較該點到兩直線的距離關係。"

    # 4. Fallbacks for standard Point-Slope / Two-Points / Horizontal / Vertical
    if task_type == "two_points" or ("point_a" in givens and "point_b" in givens):
        pa = givens["point_a"]
        pb = givens["point_b"]
        ax, ay = int(pa[0]), int(pa[1])
        bx, by = int(pb[0]), int(pb[1])
        if ax == bx:
            return (
                f"試求通過 $C({ax},\\,{ay})$ 與 $D({bx},\\,{by})$ 兩點之直線方程式。"
            )
        if ay == by:
            return (
                f"試求通過 $A({ax},\\,{ay})$ 與 $B({bx},\\,{by})$ 兩點之直線方程式。"
            )
        return (
            f"試求通過 $A({ax},\\,{ay})$ 與 $B({bx},\\,{by})$ 兩點之直線方程式。"
        )

    if task_type == "point_slope" or ("point" in givens and "slope" in givens):
        if "point" not in givens or "slope" not in givens:
            raise ValueError("required_line_task_slot_missing:point_slope:point_or_slope")
        point = givens["point"]
        slope = givens["slope"]
        px, py = int(point[0]), int(point[1])
        return (
            f"已知直線過點 $({px},\\,{py})$，斜率為 ${slope}$，求此直線方程式。"
        )

    if task_type == "horizontal_line" or line_type == "horizontal_line" or "y_intercept" in givens:
        y_val = givens.get("y_intercept")
        return f"寫出斜率為 0 且通過 y 軸上 {y_val} 的水平線方程式。"

    if task_type == "vertical_line" or line_type == "vertical_line" or "x_intercept" in givens:
        x_val = givens.get("x_intercept")
        return f"寫出鉛直且通過 x = {x_val} 的直線方程式。"

    raise ValueError(f"unsupported_line_equation_task_type:{task_type}")


def _build_choice_options(
    canonical: str,
    distractors: list[Any],
    *,
    seed_text: str,
) -> tuple[list[dict[str, str]], str]:
    unique_wrong: list[str] = []
    seen: set[str] = {canonical}
    for item in distractors:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        unique_wrong.append(text)

    option_texts = [canonical] + unique_wrong[:3]
    rng = random.Random(sum(ord(ch) for ch in seed_text))
    rng.shuffle(option_texts)

    choices: list[dict[str, str]] = []
    correct_label = "A"
    for index, text in enumerate(option_texts):
        label = chr(ord("A") + index)
        choices.append({"label": label, "text": text})
        if text == canonical:
            correct_label = label
    return choices, correct_label


def _format_point_for_question(value: Any) -> str:
    if isinstance(value, dict):
        return f"$({value.get('x')}, {value.get('y')})$"
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        return f"$({value[0]}, {value[1]})$"
    return "$()$"


def _normalize_labeled_choices(raw_choices: Any) -> list[dict[str, str]]:
    if not isinstance(raw_choices, list):
        return []
    choices: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_choices):
        if isinstance(raw, dict):
            label = str(raw.get("label") or chr(ord("A") + index)).strip()
            text = str(raw.get("text") or raw.get("value") or "").strip()
        else:
            label = chr(ord("A") + index)
            text = str(raw or "").strip()
        if not label or not text or text in seen:
            continue
        seen.add(text)
        choices.append({"label": label, "text": text})
    return choices


def _parse_fraction_text(value: Any) -> Fraction:
    if value is None or str(value).strip() == "":
        return Fraction(0, 1)
    return normalize_fraction_value(value)


def _format_fraction_text(value: Fraction) -> str:
    return fraction_to_plain(value)


def _build_x_intercept_choice_options(
    canonical: str,
    givens: dict[str, Any],
    *,
    seed_text: str,
) -> tuple[list[dict[str, str]], str]:
    correct = _parse_fraction_text(canonical)
    slope = _parse_fraction_text(givens.get("slope"))
    y_intercept = _parse_fraction_text(givens.get("y_intercept"))
    rng = random.Random(sum(ord(ch) for ch in seed_text))

    candidate_values: list[Fraction] = [
        correct,
        -correct,
        correct + 1,
        correct - 1,
        correct + Fraction(1, 2),
        correct - Fraction(1, 2),
        y_intercept,
        -y_intercept,
        slope,
        -slope,
    ]
    for offset in range(2, 10):
        candidate_values.append(correct + offset)
        candidate_values.append(correct - offset)

    wrong_values: list[Fraction] = []
    seen: set[Fraction] = {correct}
    for value in candidate_values:
        value = Fraction(value)
        if value in seen:
            continue
        seen.add(value)
        wrong_values.append(value)
        if len(wrong_values) >= 3:
            break
    while len(wrong_values) < 3:
        value = Fraction(rng.randint(-8, 8), rng.choice([1, 2, 3, 4, 5]))
        if value in seen:
            continue
        seen.add(value)
        wrong_values.append(value)

    option_values = [correct] + wrong_values[:3]
    rng.shuffle(option_values)

    choices: list[dict[str, str]] = []
    correct_label = "A"
    for index, value in enumerate(option_values):
        label = chr(ord("A") + index)
        text = _format_fraction_text(value)
        choices.append({"label": label, "text": text})
        if value == correct:
            correct_label = label
    return choices, correct_label


def _build_area_choice_options(
    canonical: str,
    *,
    seed_text: str,
) -> tuple[list[dict[str, str]], str]:
    correct = _parse_fraction_text(canonical)
    rng = random.Random(sum(ord(ch) for ch in seed_text))
    candidate_values: list[Fraction] = [
        correct,
        correct + 1,
        correct + 2,
        correct - 1,
        correct * 2,
        correct / 2 if correct != 0 else Fraction(1, 1),
        -correct,
    ]
    wrong_values: list[Fraction] = []
    seen: set[Fraction] = {correct}
    for value in candidate_values:
        value = Fraction(value)
        if value <= 0 or value in seen:
            continue
        seen.add(value)
        wrong_values.append(value)
        if len(wrong_values) >= 3:
            break
    while len(wrong_values) < 3:
        value = Fraction(rng.randint(1, 24), rng.choice([1, 2]))
        if value in seen:
            continue
        seen.add(value)
        wrong_values.append(value)

    option_values = [correct] + wrong_values[:3]
    rng.shuffle(option_values)
    choices: list[dict[str, str]] = []
    correct_label = "A"
    for index, value in enumerate(option_values):
        label = chr(ord("A") + index)
        text = _format_fraction_text(value)
        choices.append({"label": label, "text": text})
        if value == correct:
            correct_label = label
    return choices, correct_label


def _infer_math_objects(validation_facts: dict[str, Any]) -> list[str]:
    objects = ["coordinate_point", "linear_equation"]
    task_type = str(validation_facts.get("task_type") or "")
    if task_type.startswith("slope_intercept"):
        objects.append("slope_intercept_form")
    if task_type.startswith("intercept_form"):
        objects.append("intercept_form")
    if task_type == "triangle_area_bisector_line_equation":
        objects.extend(["triangle", "midpoint", "area_bisector"])
    if validation_facts.get("is_horizontal"):
        objects.append("horizontal_line")
    if validation_facts.get("is_vertical"):
        objects.append("vertical_line")
    return objects


def _format_givens_for_hint(givens: dict[str, Any]) -> list[str]:
    formatted: list[str] = []
    if "point_a" in givens and "point_b" in givens:
        formatted.append(f"A={tuple(givens['point_a'])}")
        formatted.append(f"B={tuple(givens['point_b'])}")
    if "point" in givens:
        formatted.append(f"point={tuple(givens['point'])}")
    if "slope" in givens:
        formatted.append(f"slope={givens['slope']}")
    if "y_intercept" in givens:
        formatted.append(f"y_intercept={givens['y_intercept']}")
    if "x_intercept" in givens:
        formatted.append(f"x_intercept={givens['x_intercept']}")
    if "equation" in givens:
        formatted.append(f"equation={givens['equation']}")
    return formatted


def convert_domain_matrix_to_question_payload(
    matrix: dict[str, Any],
    *,
    presentation_mode: str | None = None,
    answer_type: str | None = None,
    problem_type_id: str | None = None,
    component_id: str | None = None,
    textbook_example_id: int | None = None,
    source_kind: str | None = None,
    generator_key: str | None = None,
    domain_operation: str | None = None,
    answer_schema_key: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Convert a fixed-domain Full Matrix Dictionary into a runtime payload.

    Coordinate-geometry matrices keep their existing specialized adapter. Other
    domains use a conservative generic adapter that preserves the Full Matrix
    evidence and does not perform cross-domain routing.
    """
    op = str(domain_operation or kwargs.get("domain_operation") or "").strip()
    if op in {
        "two_points",
        "point_slope",
        "horizontal_line",
        "vertical_line",
        "oblique_line",
        "slope_intercept_equation",
        "slope_intercept_find_x_intercept",
        "slope_intercept_read_slope_and_intercept",
        "intercept_form_equation",
        "intercept_form_triangle_area",
        "intercept_form_equation_and_triangle_area",
        "intercept_form_from_intercept_sum_and_slope",
        "parabola_secant_parallel_line_choice",
        "triangle_area_bisector_line_equation",
        "slope_from_general_or_intercept_form",
        "slope_from_general_form",
        "slope_of_horizontal_or_vertical_line",
        "line_through_point_parallel_to_line",
        "line_through_point_perpendicular_to_line",
        "parallel_line_slope",
        "perpendicular_line_slope",
        "parallel_condition_parameter",
        "perpendicular_condition_parameter",
        "compare_line_slopes",
        "line_through_intersection_parallel_to_line",
        "line_through_point_perpendicular_to_segment",
        "perpendicular_bisector_application",
        "coordinate_geometry_word_problem",
        "distance_from_point_to_line",
        "distance_from_point_to_line_parameter",
        "distance_from_point_to_line_parameter_single_choice_scalar",
        "compare_point_to_line_distances",
        "distance_between_parallel_lines",
        "solve_parameter_from_parallel_distance",
        "construct_parallel_line_at_distance",
        "parallel_lines_distance_single_choice",
        "area_using_parallel_distance",
    }:
        return convert_line_equation_matrix_to_question_payload(
            matrix,
            presentation_mode=presentation_mode,
            answer_type=answer_type,
            problem_type_id=problem_type_id,
            component_id=component_id,
            textbook_example_id=textbook_example_id,
            source_kind=source_kind,
            generator_key=generator_key,
            answer_schema_key=answer_schema_key,
            domain_operation=op,
            **kwargs,
        )

    normalized = normalize_domain_matrix(matrix)
    answer = normalized["answer"]
    givens = normalized["givens"]
    validation_facts = dict(normalized["validation_facts"])
    if op:
        validation_facts.setdefault("domain_operation", op)
        validation_facts.setdefault("task_type", op)
    semantic_answer = answer.get("value", answer.get("canonical_form"))
    display_answer = str(answer.get("canonical_form", semantic_answer))
    mode = str(presentation_mode or "short_answer").strip()
    resolved_answer_type = str(answer_type or "integer").strip()
    table_chart_ops = {
        "read_category_value",
        "compare_category_values",
        "calculate_total_ratio_percent",
        "validate_chart_statement",
        "cumulative_above_fail_count",
        "cumulative_above_interval_count",
        "cumulative_below_interval_count",
    }
    if op in table_chart_ops or validation_facts.get("domain_operation") in table_chart_ops:
        operation = str(op or validation_facts.get("domain_operation") or problem_type_id or "read_category_value")
        cumulative_ops = {
            "cumulative_above_fail_count",
            "cumulative_above_interval_count",
            "cumulative_below_interval_count",
        }
        if operation in cumulative_ops:
            story = str(givens.get("story_context") or "統計資料")
            unit = str(givens.get("variable_unit") or "")
            direction = str(givens.get("cumulative_direction") or validation_facts.get("cumulative_direction") or "above")
            chart_phrase = "以上累積次數分配折線圖" if direction == "above" else "以下累積次數分配折線圖"
            if operation == "cumulative_above_fail_count":
                threshold = int(validation_facts.get("threshold") or givens.get("threshold") or 60)
                question_text = (
                    f"{story}的{chart_phrase}如下圖所示，試問：以{threshold}{unit}為準，不及格者有多少人？"
                )
            elif operation == "cumulative_above_interval_count":
                low = int(validation_facts.get("interval_low") or givens.get("interval_low") or 70)
                high = int(validation_facts.get("interval_high") or givens.get("interval_high") or 80)
                prefix = "接續上題，" if int(textbook_example_id or 0) == 3885 else ""
                question_text = (
                    f"{prefix}{story}的{chart_phrase}如下圖所示，成績在{low}～{high}{unit}有多少人？"
                )
            else:
                total = int(validation_facts.get("total_population") or givens.get("total_population") or 40)
                low = int(validation_facts.get("interval_low") or givens.get("interval_low") or 30)
                high = int(validation_facts.get("interval_high") or givens.get("interval_high") or 40)
                if "員工" in story or unit == "歲":
                    question_text = (
                        f"依某公司{total}名員工的年齡繪製以下{chart_phrase}如下圖所示，"
                        f"請問年齡在{low}～{high}{unit}有多少人？"
                    )
                else:
                    question_text = (
                        f"依{story}共{total}名員工繪製以下{chart_phrase}如下圖所示，"
                        f"請問年齡在{low}～{high}{unit}有多少人？"
                    )
            semantic_answer = answer.get("value", validation_facts.get("answer_value"))
            display_answer = str(semantic_answer)
            resolved_answer_type = "integer"
            rows = normalized.get("visual_spec", {}).get("rows") or []
            choices: list[dict[str, str]] = []
            options: list[str] = []
            payload_answer = semantic_answer
            payload_correct = semantic_answer
            answer_contract = {
                "presentation_mode": mode,
                "answer_type": resolved_answer_type,
                "checker": "integer_checker",
                "checker_key": "integer_checker",
                "answer_equivalence": "numeric_exact",
                "equivalence": "numeric_exact",
                "semantic_answer": semantic_answer,
            }
            if mode == "single_choice":
                choices, correct_label = _build_choice_options(
                    display_answer,
                    normalized.get("distractors", []),
                    seed_text=f"{operation}|{display_answer}|{component_id or ''}",
                )
                options = [str(choice["text"]) for choice in choices]
                payload_answer = correct_label
                payload_correct = correct_label
                answer_contract = {
                    "presentation_mode": "single_choice",
                    "answer_type": resolved_answer_type,
                    "checker": "choice_label_checker",
                    "checker_key": "choice_label_checker",
                    "answer_equivalence": "choice_label",
                    "equivalence": "choice_label",
                    "semantic_answer": semantic_answer,
                }
            return {
                "question_text": question_text,
                "answer": payload_answer,
                "correct_answer": payload_correct,
                "display_answer": display_answer,
                "semantic_answer": semantic_answer,
                "choices": choices,
                "options": options,
                "component_id": component_id,
                "textbook_example_id": textbook_example_id,
                "problem_type_id": operation,
                "domain_operation": operation,
                "fixed_domain_key": "statistics.table_chart",
                "source_kind": source_kind,
                "presentation_mode": mode,
                "answer_type": resolved_answer_type,
                "checker": answer_contract["checker"],
                "checker_key": answer_contract["checker_key"],
                "interaction_type": "single_choice" if mode == "single_choice" else "expression",
                "auto_checkable": True,
                "grading_mode": "auto",
                "answer_contract": answer_contract,
                "metadata": {
                    "givens": givens,
                    "raw_givens": givens,
                    "target": display_answer,
                    "derivation": [str(step) for step in normalized["explanation_steps"]],
                    "presentation_mode": mode,
                    "answer_type": resolved_answer_type,
                    "semantic_answer": semantic_answer,
                    "problem_type_id": operation,
                    "domain_operation": operation,
                    "fixed_domain_key": "statistics.table_chart",
                    "component_id": component_id,
                    "textbook_example_id": textbook_example_id,
                    "interaction_type": "single_choice" if mode == "single_choice" else "expression",
                    "auto_checkable": True,
                    "grading_mode": "auto",
                },
                "math_core": {
                    "givens": givens,
                    "raw_givens": givens,
                    "target": display_answer,
                    "math_objects": ["cumulative_frequency_polygon", "statistical_chart"],
                    "derivation": [str(step) for step in normalized["explanation_steps"]],
                    "validation_facts": validation_facts,
                },
                "visual_spec": normalized["visual_spec"],
                "visual_aids": normalized.get("visual_aids", matrix.get("visual_aids", [])),
                "image_base64": normalized.get("image_base64", matrix.get("image_base64", "")),
                "validation_facts": validation_facts,
                "generator_key": generator_key or component_id,
                "story_context": story,
            }

        rows = normalized.get("visual_spec", {}).get("rows") or []
        value_map = validation_facts.get("value_map") or givens.get("value_map") or {}
        categories = list(givens.get("categories") or list(value_map.keys()) or [])
        if not value_map and rows:
            value_map = {str(row[0]): int(row[1]) for row in rows if len(row) >= 2}
            categories = list(value_map.keys())
        target_label = str(validation_facts.get("target_label") or givens.get("target_label") or (categories[0] if categories else "A"))
        compare_a = str(validation_facts.get("compare_a") or givens.get("compare_a") or (categories[0] if categories else "A"))
        compare_b = str(validation_facts.get("compare_b") or givens.get("compare_b") or (categories[1] if len(categories) > 1 else compare_a))
        if operation == "compare_category_values":
            question_text = f"閱讀下列統計表，比較 {compare_a} 與 {compare_b} 的數值，兩者相差多少？"
            semantic_answer = answer.get("value", validation_facts.get("answer_value"))
            display_answer = str(semantic_answer)
            resolved_answer_type = "integer" if isinstance(semantic_answer, int) else resolved_answer_type
        elif operation == "calculate_total_ratio_percent":
            question_text = f"閱讀下列統計表，求 {target_label} 佔總量的百分比。"
            semantic_answer = answer.get("value", validation_facts.get("answer_value"))
            display_answer = str(answer.get("canonical_form", semantic_answer))
        elif operation == "validate_chart_statement":
            statement = str(validation_facts.get("statement") or givens.get("statement") or "")
            question_text = f"閱讀下列統計表，判斷敘述「{statement}」是否正確。"
            semantic_answer = bool(answer.get("value", validation_facts.get("answer_value")))
            display_answer = "true" if semantic_answer else "false"
            resolved_answer_type = "boolean"
        else:
            question_text = f"閱讀下列統計表，求 {target_label} 的數值。"
            semantic_answer = answer.get("value", validation_facts.get("answer_value"))
            display_answer = str(semantic_answer)
            resolved_answer_type = "integer" if isinstance(semantic_answer, int) else resolved_answer_type

        choices: list[dict[str, str]] = []
        options: list[str] = []
        payload_answer = semantic_answer
        payload_correct = semantic_answer
        checker = "integer_checker" if resolved_answer_type in {"integer", "numeric"} else "text_short_checker"
        equivalence = "numeric_exact" if checker == "integer_checker" else "exact_string"
        answer_contract = {
            "presentation_mode": mode,
            "answer_type": resolved_answer_type,
            "checker": checker,
            "checker_key": checker,
            "answer_equivalence": equivalence,
            "equivalence": equivalence,
            "semantic_answer": semantic_answer,
        }
        if mode == "single_choice":
            choices, correct_label = _build_choice_options(
                display_answer,
                normalized.get("distractors", []),
                seed_text=f"{operation}|{display_answer}|{component_id or ''}",
            )
            options = [str(choice["text"]) for choice in choices]
            payload_answer = correct_label
            payload_correct = correct_label
            answer_contract = {
                "presentation_mode": "single_choice",
                "answer_type": resolved_answer_type,
                "checker": "choice_label_checker",
                "checker_key": "choice_label_checker",
                "answer_equivalence": "choice_label",
                "equivalence": "choice_label",
                "semantic_answer": semantic_answer,
            }
        return {
            "question_text": question_text,
            "answer": payload_answer,
            "correct_answer": payload_correct,
            "display_answer": display_answer,
            "semantic_answer": semantic_answer,
            "choices": choices,
            "options": options,
            "component_id": component_id,
            "textbook_example_id": textbook_example_id,
            "problem_type_id": operation,
            "domain_operation": operation,
            "fixed_domain_key": "statistics.table_chart",
            "source_kind": source_kind,
            "presentation_mode": mode,
            "answer_type": resolved_answer_type,
            "checker": answer_contract["checker"],
            "checker_key": answer_contract["checker_key"],
            "interaction_type": "single_choice" if mode == "single_choice" else "expression",
            "auto_checkable": True,
            "grading_mode": "auto",
            "answer_contract": answer_contract,
            "metadata": {
                "givens": givens,
                "raw_givens": givens,
                "target": display_answer,
                "derivation": [str(step) for step in normalized["explanation_steps"]],
                "presentation_mode": mode,
                "answer_type": resolved_answer_type,
                "semantic_answer": semantic_answer,
                "problem_type_id": operation,
                "domain_operation": operation,
                "fixed_domain_key": "statistics.table_chart",
                "component_id": component_id,
                "textbook_example_id": textbook_example_id,
                "interaction_type": "single_choice" if mode == "single_choice" else "expression",
                "auto_checkable": True,
                "grading_mode": "auto",
            },
            "math_core": {
                "givens": givens,
                "raw_givens": givens,
                "target": display_answer,
                "math_objects": ["statistical_chart", "category_value"],
                "derivation": [str(step) for step in normalized["explanation_steps"]],
                "validation_facts": validation_facts,
            },
            "visual_spec": normalized["visual_spec"],
            "visual_aids": normalized.get("visual_aids", matrix.get("visual_aids", [])),
            "image_base64": normalized.get("image_base64", matrix.get("image_base64", "")),
            "validation_facts": validation_facts,
            "generator_key": generator_key or component_id,
        }
    question_text = str(kwargs.get("question_text") or "閱讀下列資料，根據表格回答問題。")
    if problem_type_id == "frequency_distribution_chart_construction":
        pass
    elif problem_type_id == "histogram_distribution_update":
        question_text = "下圖為某幼兒園班上25位小朋友身高分布之直方圖。今班上轉出一位身高117公分的小朋友，轉入一位身高112公分的小朋友，則此時班上小朋友身高分布之直方圖為何？（請說明哪兩組次數改變以及各改變多少）"
    else:
        target_label = validation_facts.get("target_label")
        if target_label:
            question_text = f"閱讀下列次數分配表，求 {target_label} 的次數。"

    if problem_type_id == "frequency_distribution_chart_construction":
        x_categories = [row[0] for row in matrix.get("visual_spec", {}).get("rows", [])]
        expected_values = [row[1] for row in matrix.get("visual_spec", {}).get("rows", [])]
        spec = {
            "drawing_type": "histogram_and_frequency_polygon",
            "x_categories": x_categories,
            "expected_values": expected_values,
            "required_elements": [
                "x_axis",
                "y_axis",
                "histogram_bars",
                "frequency_polygon"
            ],
            "grading_rules": {
                "bar_count_matches_categories": True,
                "histogram_bars_touch": True,
                "polygon_connects_category_midpoints_in_order": True
            },
            "bar_rules": {
                "count": len(x_categories),
                "expected_heights": expected_values,
                "touching": True,
                "baseline": 0
            },
            "polygon_rules": {
                "expected_points": [
                    [cat, val] for cat, val in zip(x_categories, expected_values)
                ],
                "connect_in_order": True
            },
            "tolerance": {
                "value": 0.8,
                "position_ratio": 0.12
            }
        }
        return {
            "question_text": question_text,
            "answer": "直方圖與折線圖已繪製於畫布。",
            "correct_answer": "直方圖與折線圖已繪製於畫布。",
            "display_answer": "直方圖與折線圖已繪製於畫布。",
            "choices": [],
            "options": [],
            "component_id": component_id,
            "textbook_example_id": textbook_example_id,
            "problem_type_id": problem_type_id,
            "source_kind": source_kind,
            "presentation_mode": mode,
            "answer_type": "drawing",
            "answer_shape": "drawing",
            "interaction_type": "handwriting_drawing",
            "auto_checkable": False,
            "grading_mode": "manual_or_ai_visual_review",
            "expected_drawing_spec": spec,
            "answer_contract": {
                "presentation_mode": mode,
                "answer_type": "drawing",
                "answer_shape": "drawing",
                "checker": "free_response_drawing_checker",
                "checker_key": "free_response_drawing_checker",
                "answer_equivalence": "drawing_equivalence",
                "equivalence": "drawing_equivalence",
                "semantic_answer": "直方圖與折線圖已繪製於畫布。",
                "expected_drawing_spec": spec,
            },
            "metadata": {
                "givens": givens,
                "raw_givens": givens,
                "target": "直方圖與折線圖已繪製於畫布。",
                "derivation": [str(step) for step in normalized["explanation_steps"]],
                "presentation_mode": mode,
                "answer_type": "drawing",
                "answer_shape": "drawing",
                "semantic_answer": "直方圖與折線圖已繪製於畫布。",
                "problem_type_id": problem_type_id,
                "component_id": component_id,
                "textbook_example_id": textbook_example_id,
                "interaction_type": "handwriting_drawing",
                "auto_checkable": False,
                "grading_mode": "manual_or_ai_visual_review",
                "expected_drawing_spec": spec,
            },
            "math_core": {
                "givens": givens,
                "raw_givens": givens,
                "target": "直方圖與折線圖已繪製於畫布。",
                "math_objects": ["frequency_table", "frequency"],
                "derivation": [str(step) for step in normalized["explanation_steps"]],
                "validation_facts": validation_facts,
            },
            "visual_spec": normalized["visual_spec"],
            "visual_aids": normalized.get("visual_aids", matrix.get("visual_aids", [])),
            "image_base64": normalized.get("image_base64", matrix.get("image_base64", "")),
            "validation_facts": validation_facts,
            "generator_key": generator_key or component_id,
        }

    choices: list[dict[str, str]] = []
    options: list[str] = []
    payload_answer = semantic_answer
    payload_correct = semantic_answer
    answer_contract = {
        "presentation_mode": mode,
        "answer_type": resolved_answer_type,
        "checker": "text_short_checker" if problem_type_id == "histogram_distribution_update" else "integer_checker",
        "checker_key": "text_short_checker" if problem_type_id == "histogram_distribution_update" else "integer_checker",
        "answer_equivalence": "string_equivalence" if problem_type_id == "histogram_distribution_update" else "numeric_exact",
        "equivalence": "string_equivalence" if problem_type_id == "histogram_distribution_update" else "numeric_exact",
        "semantic_answer": semantic_answer,
        "ui_contract": {
            "response_mode": "text",
            "text_input_enabled": True,
            "normal_submit_enabled": True,
            "ai_check_required": False,
            "canvas_required": False,
            "allow_image_upload": False,
            "allow_text_answer": True,
        } if problem_type_id == "histogram_distribution_update" else None,
    }
    if mode == "single_choice":
        choices, correct_label = _build_choice_options(
            display_answer,
            normalized.get("distractors", []),
            seed_text=f"{problem_type_id or op}|{display_answer}",
        )
        options = [str(choice["text"]) for choice in choices]
        payload_answer = correct_label
        payload_correct = correct_label
        answer_contract = {
            "presentation_mode": "single_choice",
            "answer_type": "single_choice",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "answer_equivalence": "choice_label",
            "equivalence": "choice_label",
            "semantic_answer": semantic_answer,
        }

    return {
        "question_text": question_text,
        "answer": payload_answer,
        "correct_answer": payload_correct,
        "display_answer": display_answer,
        "choices": choices,
        "options": options,
        "component_id": component_id,
        "textbook_example_id": textbook_example_id,
        "problem_type_id": problem_type_id or op,
        "source_kind": source_kind,
        "presentation_mode": mode,
        "answer_type": resolved_answer_type,
        "interaction_type": "expression",
        "auto_checkable": True,
        "grading_mode": "auto",
        "answer_contract": answer_contract,
        "metadata": {
            "givens": givens,
            "raw_givens": givens,
            "target": display_answer,
            "derivation": [str(step) for step in normalized["explanation_steps"]],
            "presentation_mode": mode,
            "answer_type": resolved_answer_type,
            "semantic_answer": semantic_answer,
            "problem_type_id": problem_type_id or op,
            "component_id": component_id,
            "textbook_example_id": textbook_example_id,
            "interaction_type": "expression",
            "auto_checkable": True,
            "grading_mode": "auto",
        },
        "math_core": {
            "givens": givens,
            "raw_givens": givens,
            "target": display_answer,
            "math_objects": ["frequency_table", "frequency"],
            "derivation": [str(step) for step in normalized["explanation_steps"]],
            "validation_facts": validation_facts,
        },
        "visual_spec": normalized["visual_spec"],
        "visual_aids": normalized.get("visual_aids", matrix.get("visual_aids", [])),
        "image_base64": normalized.get("image_base64", matrix.get("image_base64", "")),
        "validation_facts": validation_facts,
        "generator_key": generator_key or component_id,
    }
