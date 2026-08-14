"""Semantic validators shared by V3 coordinate-geometry generation gates."""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any


_POINT_PATTERNS = (
    re.compile(r"\((-?\d+)\s*,\s*(-?\d+)\)"),
    re.compile(r"\\left\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\\right\)"),
    re.compile(r"\((-?\d+)\s*,\s*[a-zA-Z]\s*\)"),
    re.compile(r"\\left\(\s*(-?\d+)\s*,\s*[a-zA-Z]\s*\\right\)"),
)


def validate_source_completeness(source_text: str, problem_type_id: str) -> dict[str, Any]:
    """Return source-completeness blockers for a classified source problem."""
    text = str(source_text or "")
    problem_type = str(problem_type_id or "").strip()
    blockers: list[str] = []
    if problem_type in {
        "distance_from_point_to_line",
        "distance_from_point_to_line_parameter",
        "distance_from_point_to_line_parameter_single_choice_scalar",
        "compare_point_to_line_distances",
    }:
        if not any(pattern.search(text) for pattern in _POINT_PATTERNS):
            blockers.append("source_incomplete:missing_point_coordinates")
    if problem_type in {
        "distance_from_point_to_line_parameter",
        "distance_from_point_to_line_parameter_single_choice_scalar",
    }:
        if "=" not in text:
            blockers.append("source_incomplete:missing_line_equation")
        if not re.search(r"[ak]\b|[ak]\s*=", text):
            blockers.append("source_incomplete:missing_parameter_symbol")
        if "距離" not in text and "distance" not in text.lower():
            blockers.append("source_incomplete:missing_distance_value")
    if problem_type in {
        "slope_from_two_points",
        "solve_parameter_from_known_slope",
        "solve_parameter_from_known_slope_choice",
        "collinear_three_points_parameter",
        "non_triangle_collinear_parameter",
        "parallel_segments_parameter",
        "perpendicular_segments_parameter",
    }:
        from core.gencode.services.v3_example_semantic_classifier import _slope_source_block_reason

        reason = _slope_source_block_reason(text)
        if reason:
            blockers.append(f"source_incomplete:{reason}")
    return {"passed": not blockers, "blockers": blockers}


def validate_equation_display_text(payload: dict[str, Any]) -> list[str]:
    text = " ".join(
        str(value or "")
        for value in (
            payload.get("question_text"),
            payload.get("question"),
            payload.get("display_answer"),
        )
    )
    blockers: list[str] = []
    compact = text.replace(" ", "")
    if "=0=0" in compact:
        blockers.append("bad_equation_serialization:double_equals_zero")
    if "=0+" in compact or "=0-" in compact:
        blockers.append("bad_equation_serialization:equation_used_as_expression")
    return blockers


def validate_comparison_contract(payload: dict[str, Any]) -> list[str]:
    if str(payload.get("problem_type_id") or "") != "compare_point_to_line_distances":
        return []
    contract = payload.get("answer_contract")
    if not isinstance(contract, dict):
        return ["comparison_contract_missing"]
    required = {
        "target_direction",
        "closer_line",
        "farther_line",
        "comparison_relation",
        "comparison_result",
        "distances",
    }
    missing = sorted(key for key in required if key not in contract)
    if missing:
        return [f"comparison_contract_missing:{','.join(missing)}"]
    target = str(contract.get("target_direction") or "")
    result = str(contract.get("comparison_result") or "")
    if target == "closer" and result != str(contract.get("closer_line")):
        return ["comparison_contract_mismatch:closer_result"]
    if target == "farther" and result != str(contract.get("farther_line")):
        return ["comparison_contract_mismatch:farther_result"]
    if target == "relation" and result != str(contract.get("comparison_relation")):
        return ["comparison_contract_mismatch:relation_result"]

    # Validator 補強規則
    q_text = str(payload.get("question_text") or "")
    checker = str(contract.get("checker") or contract.get("checker_key") or "").strip()
    semantic_ans = str(payload.get("metadata", {}).get("semantic_answer") or payload.get("correct_answer") or "")
    presentation_mode = str(payload.get("presentation_mode") or payload.get("metadata", {}).get("presentation_mode") or "").strip()

    if presentation_mode != "single_choice":
        if target in {"closer", "farther"}:
            expected_word = "較近" if target == "closer" else "較遠"
            if expected_word not in q_text:
                return [f"comparison_stem_mismatch:missing_{expected_word}"]
            if checker != "line_label_checker":
                return [f"comparison_checker_mismatch:expected_line_label_checker_got_{checker}"]
            if semantic_ans not in {"L_1", "L_2"}:
                return [f"comparison_answer_mismatch:expected_L1_or_L2_got_{semantic_ans}"]
        elif target == "relation":
            if "d(P,L_" not in semantic_ans:
                return [f"comparison_answer_mismatch:expected_relation_got_{semantic_ans}"]

    return []


def validate_single_choice_scalar_topology(payload: dict[str, Any]) -> list[str]:
    problem_type = str(payload.get("problem_type_id") or "")
    if problem_type != "distance_from_point_to_line_parameter_single_choice_scalar":
        return []
    contract = payload.get("answer_contract")
    if not isinstance(contract, dict):
        return ["single_choice_scalar_contract_missing"]
    if contract.get("choice_value_shape") != "scalar":
        return ["single_choice_scalar_shape_missing"]
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return ["single_choice_scalar_choices_missing"]
    for choice in choices:
        text = str(choice.get("text") if isinstance(choice, dict) else choice)
        if "或" in text or "," in text:
            return ["single_choice_scalar_choice_contains_solution_pair"]
    return []


def validate_distance_oracle(payload: dict[str, Any]) -> list[str]:
    meta = payload.get("metadata")
    if not isinstance(meta, dict):
        return []
    givens = meta.get("givens")
    if not isinstance(givens, dict):
        return []
    coeffs = meta.get("coefficients")
    if not isinstance(coeffs, dict):
        return []
    problem_type = str(payload.get("problem_type_id") or "")
    try:
        a = int(coeffs["A"])
        b = int(coeffs["B"])
        c = int(coeffs["C"])
    except Exception:
        return []
    if problem_type == "distance_from_point_to_line":
        point = givens.get("point")
        if not isinstance(point, list) or len(point) < 2:
            return ["distance_oracle_missing_point"]
        try:
            x0, y0 = int(point[0]), int(point[1])
            expected = Fraction(abs(a * x0 + b * y0 + c), int((a * a + b * b) ** 0.5))
            actual = Fraction(str(meta.get("distance") or payload.get("semantic_answer")))
        except Exception:
            return []
        if expected != actual:
            return ["distance_oracle_mismatch"]
    return []
