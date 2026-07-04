"""Isolated payload adapter and checker for the operation candidate."""

from __future__ import annotations

from fractions import Fraction
from typing import Any


def _equivalent_scalar(actual: object, expected: object) -> bool:
    if actual is None or expected is None:
        return actual is expected
    try:
        return Fraction(str(actual).strip()) == Fraction(str(expected).strip())
    except (ValueError, ZeroDivisionError):
        return str(actual).replace(" ", "") == str(expected).replace(" ", "")


def check_multi_part_answer(
    user_answer: object,
    canonical_answer: dict[str, object],
) -> bool:
    if not isinstance(user_answer, dict):
        return False
    required = ("x_intercept", "y_intercept", "function_equation")
    if canonical_answer.get("function_equation") is None:
        required = ("x_intercept", "y_intercept", "line_equation")
    return all(
        key in user_answer
        and _equivalent_scalar(user_answer.get(key), canonical_answer.get(key))
        for key in required
    )


def adapt_matrix_to_component_payload(
    matrix: dict[str, Any],
    *,
    component_ref: str,
    source_example_ref: int,
) -> dict[str, Any]:
    canonical = dict(matrix["semantic_answer"])
    parts = [
        {
            "key": key,
            "label": label,
            "checker": checker,
            "expected_answer": canonical.get(key),
        }
        for key, label, checker in (
            ("x_intercept", "x 截距", "rational_checker"),
            ("y_intercept", "y 截距", "rational_checker"),
            ("function_equation", "f(x)", "linear_equation_equivalent_checker"),
        )
    ]
    return {
        "question_text": matrix["question"],
        "answer": canonical,
        "correct_answer": canonical,
        "display_answer": canonical,
        "semantic_answer": canonical,
        "semantic_answer_type": "multi_part",
        "answer_type": "multi_part",
        "presentation_mode": "graph_multi_part",
        "interaction_type": "multi_part",
        "problem_type_id": "graph_intercepts_and_linear_equation",
        "domain_operation": "graph_intercepts_and_linear_equation",
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "component_id": component_ref,
        "textbook_example_id": source_example_ref,
        "topology_tags": list(matrix["topology_tags"]),
        "visual_spec": dict(matrix["visual_spec"]),
        "answer_contract": {
            "presentation_mode": "graph_multi_part",
            "answer_type": "multi_part",
            "answer_shape": "multi_part",
            "checker": "multi_part_answer_checker",
            "checker_key": "multi_part_answer_checker",
            "answer_equivalence": "multi_part_answer",
            "equivalence": "multi_part_answer",
            "semantic_answer": canonical,
            "parts": parts,
            "ui_contract": {
                "response_mode": "multi_part",
                "text_input_enabled": True,
            },
        },
        "metadata": {
            "givens": dict(matrix["givens"]),
            "semantic_answer": canonical,
            "presentation_mode": "graph_multi_part",
            "answer_type": "multi_part",
            "source_example_id": source_example_ref,
        },
        "math_core": {
            "givens": dict(matrix["givens"]),
            "target": canonical,
            "derivation": list(matrix["explanation_steps"]),
            "validation_facts": dict(matrix["validation_facts"]),
        },
        "choices": [],
        "options": [],
        "auto_checkable": True,
        "grading_mode": "auto",
    }
