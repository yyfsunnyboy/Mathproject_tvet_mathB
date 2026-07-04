"""Reusable deterministic source-topology classification rules."""

from __future__ import annotations

import re
from typing import Any


def _has_graph_reference(text: str) -> bool:
    return bool(re.search(r"(?:右圖|下圖|如圖|圖形)", text))


def _part_count(text: str) -> int:
    return len(set(re.findall(r"\(([1-9])\)", text)))


def _has_embedded_choices(text: str) -> bool:
    return len(set(re.findall(r"\(([A-D])\)", text, re.I))) >= 2


def _linear_expression_kind(text: str) -> str:
    match = re.search(
        r"(?:y\s*=\s*)?f\\left\(\s*x\s*\\right\)\s*=([^。\n]+)",
        text,
    )
    if not match:
        return ""
    expression = match.group(1)
    return "affine" if re.search(r"[+-]?\s*\d*\s*x", expression) else "constant"


def _contract(
    problem_type_id: str,
    *,
    required_givens: list[str],
    requested_quantity: list[str],
    topology_tags: list[str],
    answer_schema: str,
    presentation_mode: str,
) -> dict[str, Any]:
    if answer_schema.startswith("choice_label"):
        answer_type = "choice"
        checker_key = "choice_label_checker"
        equivalence_type = "choice_label"
        runtime_category = "deterministic_choice"
    elif answer_schema.startswith("multi_part"):
        answer_type = "multi_part"
        checker_key = "multi_part_answer_checker"
        equivalence_type = "multi_part_answer"
        runtime_category = "deterministic_expression"
    elif answer_schema == "coordinate_pair":
        answer_type = "coordinate_pair"
        checker_key = "coordinate_pair_checker"
        equivalence_type = "coordinate_pair_equivalence"
        runtime_category = "deterministic_expression"
    elif answer_schema == "numeric_scalar":
        answer_type = "numeric"
        checker_key = "numeric_checker"
        equivalence_type = "numeric_equivalence"
        runtime_category = "deterministic_expression"
    elif answer_schema == "graph":
        answer_type = "graph"
        checker_key = "graph_spec_checker"
        equivalence_type = "graph_equivalence"
        runtime_category = "deterministic_expression"
    else:
        answer_type = "expression"
        checker_key = "expression_equivalence_checker"
        equivalence_type = "algebraic_equivalent"
        runtime_category = "deterministic_expression"
    topology = {
        "problem_type_id": problem_type_id,
        "exact_task_operation": problem_type_id,
        "required_givens": required_givens,
        "requested_quantity": requested_quantity,
        "topology_tags": topology_tags,
        "answer_schema": answer_schema,
        "presentation_mode": presentation_mode,
    }
    return {
        **topology,
        "source_topology": topology,
        "answer_type": answer_type,
        "checker_key": checker_key,
        "equivalence_type": equivalence_type,
        "runtime_category": runtime_category,
    }


def classify_source_topology(row: dict[str, Any]) -> dict[str, Any] | None:
    """Classify reusable source structures without skill/component identity."""
    text = str(row.get("problem_text") or row.get("question") or "")
    solution = str(row.get("detailed_solution") or row.get("explanation") or "")
    combined = f"{text}\n{solution}"
    graph = _has_graph_reference(text)
    parts = _part_count(text)
    choices = _has_embedded_choices(text)

    requests_intercepts = "x截距" in text and "y截距" in text
    requests_function = bool(re.search(r"(?:試求|關係式為|則)\s*\$?f|x與y的關係式", text))
    if graph and parts >= 2 and requests_intercepts and requests_function:
        return _contract(
            "graph_intercepts_and_linear_equation",
            required_givens=["linear_function_graph"],
            requested_quantity=["x_intercept", "y_intercept", "linear_function_equation"],
            topology_tags=["graph_reading", "two_axis_intercepts", "equation_from_graph", "multi_part"],
            answer_schema="multi_part_intercepts_and_expression",
            presentation_mode="graph_multi_part",
        )

    contextual = bool(re.search(r"(?:費用|通話|行李|油量|預算|貨品)", text))
    threshold = bool(re.search(r"(?:以內|超過|免費)", text))
    if graph and contextual and parts >= 2 and threshold:
        return _contract(
            "graph_based_tiered_linear_application_multi_part",
            required_givens=["context_variables", "threshold_rule", "linear_relation_graph"],
            requested_quantity=["base_value", "evaluated_context_value"],
            topology_tags=["contextual_application", "graph_reading", "threshold", "multi_part"],
            answer_schema="multi_part_numeric",
            presentation_mode="graph_multi_part",
        )

    if (
        len(re.findall(r"[A-D]\\left\(", text)) >= 2
        and "同一直線" in text
        and "三等分" in text
        and re.search(r"(?:點C|C之坐標)", text)
    ):
        return _contract(
            "collinear_trisection_coordinate",
            required_givens=["two_segment_endpoints", "ordered_collinear_points", "trisection_relation"],
            requested_quantity=["trisection_point_coordinate"],
            topology_tags=["coordinate_geometry", "collinear", "equal_partition", "internal_division"],
            answer_schema="coordinate_pair",
            presentation_mode="short_answer",
        )

    draws_graph = bool(re.search(r"(?:畫出|繪出).*(?:圖形|函數)", text))
    expression_kind = _linear_expression_kind(text)
    if draws_graph and expression_kind == "constant":
        return _contract(
            "draw_constant_function_graph",
            required_givens=["constant_function_equation"],
            requested_quantity=["function_graph"],
            topology_tags=["graph_construction", "horizontal_line", "constant_function"],
            answer_schema="graph",
            presentation_mode="graph",
        )
    if draws_graph and expression_kind == "affine":
        return _contract(
            "draw_linear_function_graph",
            required_givens=["linear_function_equation"],
            requested_quantity=["function_graph"],
            topology_tags=["graph_construction", "linear_function", "two_point_plotting"],
            answer_schema="graph",
            presentation_mode="graph",
        )

    if graph and contextual and re.search(r"(?:幾公斤|多少公里|多少公升)", text):
        return _contract(
            "graph_based_linear_application_inverse",
            required_givens=["context_variables", "linear_relation_graph", "known_output_value"],
            requested_quantity=["corresponding_input_value"],
            topology_tags=["contextual_application", "graph_reading", "inverse_evaluation"],
            answer_schema="numeric_scalar",
            presentation_mode="graph_short_answer",
        )

    if graph and contextual and requests_function:
        return _contract(
            "graph_based_linear_model_equation",
            required_givens=["context_variables", "linear_relation_graph"],
            requested_quantity=["linear_model_equation"],
            topology_tags=["contextual_application", "graph_reading", "equation_from_graph"],
            answer_schema="expression",
            presentation_mode="graph_short_answer",
        )

    if contextual and choices and "預算" in text and "單價" in text:
        return _contract(
            "robust_budget_feasibility_choice",
            required_givens=["budget_limit", "two_possible_unit_prices", "quantity_pair_choices"],
            requested_quantity=["always_feasible_quantity_pair"],
            topology_tags=["linear_inequality", "uncertain_assignment", "robust_feasibility", "single_choice"],
            answer_schema="choice_label",
            presentation_mode="single_choice",
        )

    coordinate_pairs = re.findall(r"\\left\(\s*-?\d+\s*,\s*-?\d+\s*\\right\)", text)
    if len(coordinate_pairs) >= 2 and choices and re.search(r"f\\left\(\s*x\s*\\right\)\s*=", text):
        return _contract(
            "linear_equation_from_two_points_choice",
            required_givens=["two_points_on_linear_function"],
            requested_quantity=["linear_function_equation"],
            topology_tags=["two_points", "slope_then_intercept", "single_choice"],
            answer_schema="choice_label_with_expression",
            presentation_mode="single_choice",
        )

    asks_impossible_graph = "不可能" in text and "圖形" in text
    if asks_impossible_graph and re.search(r"f\\left\(\s*x\s*\\right\)\s*=", text):
        return _contract(
            "linear_graph_feasibility_choice",
            required_givens=["linear_function_family", "fixed_intercept_constraint", "graph_choices"],
            requested_quantity=["impossible_graph"],
            topology_tags=["intercept_constraint", "graph_family", "feasibility", "single_choice"],
            answer_schema="choice_label_with_graph",
            presentation_mode="graph_single_choice",
        )

    return None
