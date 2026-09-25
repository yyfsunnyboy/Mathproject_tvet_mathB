# -*- coding: utf-8 -*-
"""Isolated vector drawing checker + legacy isolation regressions."""

from __future__ import annotations

from core.checkers.expression_equivalence_checker import check_expression_equivalence_answer
from core.checkers.vector_drawing_checker import (
    check_vector_drawing_answer,
    drawing_check_enabled,
)
from core.domain.vector_plane_domain import build_vector_plane_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload


def _points():
    return {
        "A": {"x": 40.0, "y": 160.0},
        "C": {"x": 200.0, "y": 40.0},
        "D": {"x": 120.0, "y": 100.0},
        "B": {"x": 90.0, "y": 140.0},
    }


def _stroke(x0, y0, x1, y1):
    return {"points": [{"x": x0, "y": y0}, {"x": (x0 + x1) / 2, "y": (y0 + y1) / 2}, {"x": x1, "y": y1}]}


def test_drawing_ac_pass():
    pts = _points()
    result = check_vector_drawing_answer(
        student_strokes=[_stroke(pts["A"]["x"], pts["A"]["y"], pts["C"]["x"], pts["C"]["y"])],
        labeled_point_canvas_positions=pts,
        expected_answer=r"\overrightarrow{AC}",
        answer_contract={"drawing_check": {"enabled": True, "expected_from": "A", "expected_to": "C"}},
        canvas_css_size={"width": 320, "height": 220},
    )
    assert result["status"] == "correct"
    assert result["correct"] is True


def test_drawing_ca_fail_direction():
    pts = _points()
    result = check_vector_drawing_answer(
        student_strokes=[_stroke(pts["C"]["x"], pts["C"]["y"], pts["A"]["x"], pts["A"]["y"])],
        labeled_point_canvas_positions=pts,
        expected_answer=r"\overrightarrow{AC}",
        answer_contract={"drawing_check": {"enabled": True}},
        canvas_css_size={"width": 320, "height": 220},
    )
    assert result["status"] == "incorrect"
    assert result["reason"] == "fail_direction"
    assert "方向相反" in result["result"]


def test_drawing_ad_fail_endpoint():
    pts = _points()
    result = check_vector_drawing_answer(
        student_strokes=[_stroke(pts["A"]["x"], pts["A"]["y"], pts["D"]["x"], pts["D"]["y"])],
        labeled_point_canvas_positions=pts,
        expected_answer=r"\overrightarrow{AC}",
        answer_contract={"drawing_check": {"enabled": True}},
        canvas_css_size={"width": 320, "height": 220},
    )
    assert result["status"] == "incorrect"
    assert result["reason"] == "fail_endpoint"


def test_tolerance_near_points_pass():
    pts = _points()
    result = check_vector_drawing_answer(
        student_strokes=[_stroke(pts["A"]["x"] + 8, pts["A"]["y"] - 6, pts["C"]["x"] - 7, pts["C"]["y"] + 5)],
        labeled_point_canvas_positions=pts,
        expected_answer=r"\overrightarrow{AC}",
        answer_contract={"drawing_check": {"enabled": True}},
        canvas_css_size={"width": 320, "height": 220},
    )
    assert result["status"] == "correct"


def test_far_stroke_uncertain_or_fail():
    pts = _points()
    result = check_vector_drawing_answer(
        student_strokes=[_stroke(10, 10, 20, 15)],
        labeled_point_canvas_positions=pts,
        expected_answer=r"\overrightarrow{AC}",
        answer_contract={"drawing_check": {"enabled": True}},
        canvas_css_size={"width": 320, "height": 220},
    )
    assert result["status"] in {"uncertain", "incorrect"}
    assert result["correct"] is not True


def test_conflicting_strokes_uncertain():
    pts = _points()
    result = check_vector_drawing_answer(
        student_strokes=[
            _stroke(pts["A"]["x"], pts["A"]["y"], pts["C"]["x"], pts["C"]["y"]),
            _stroke(pts["C"]["x"], pts["C"]["y"], pts["A"]["x"], pts["A"]["y"]),
        ],
        labeled_point_canvas_positions=pts,
        expected_answer=r"\overrightarrow{AC}",
        answer_contract={"drawing_check": {"enabled": True}},
        canvas_css_size={"width": 320, "height": 220},
    )
    assert result["status"] == "uncertain"
    assert result["reason"] == "conflicting_strokes"


def test_keyboard_coexists_for_ac():
    assert check_expression_equivalence_answer("AC", r"\overrightarrow{AC}")
    assert not check_expression_equivalence_answer("CA", r"\overrightarrow{AC}")


def test_simplify_path_payload_enables_drawing_check_only_for_that_family():
    matrix = build_vector_plane_matrix(
        domain_operation="simplify_vector_path_expression",
        seed=4,
        tokens=["AD", "+", "DC"],
    )
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="expression",
        problem_type_id="simplify_vector_path_expression",
        domain_operation="simplify_vector_path_expression",
    )
    ac = payload.get("answer_contract") or {}
    assert drawing_check_enabled(ac, payload) is True
    assert (ac.get("drawing_check") or {}).get("expected_from") == "A"
    assert (ac.get("drawing_check") or {}).get("expected_to") == "C"
    assert check_expression_equivalence_answer(
        "AC",
        payload.get("correct_answer") or payload.get("answer"),
        answer_contract=ac,
        payload=payload,
    )


def test_legacy_expression_family_does_not_enable_drawing_check():
    matrix = build_vector_plane_matrix(domain_operation="compute_dot_product_coordinates", seed=2)
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="expression",
        problem_type_id="compute_dot_product_coordinates",
        domain_operation="compute_dot_product_coordinates",
    )
    ac = payload.get("answer_contract") or {}
    assert drawing_check_enabled(ac, payload) is False


def test_drawing_check_gate_off_by_default():
    assert drawing_check_enabled({"answer_shape": "directed_segment"}, {}) is False
    assert drawing_check_enabled({"drawing_check": {"enabled": True}}, {}) is True
