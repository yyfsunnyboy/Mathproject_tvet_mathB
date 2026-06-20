# -*- coding: utf-8 -*-
"""Tests for V3 textbook example semantic classifier."""

from __future__ import annotations

import pytest
from unittest import mock
from core.gencode.services.v3_example_semantic_classifier import (
    TextbookExampleSource,
    classify_textbook_example,
)


def _make_source(example_id: int, text: str, choices: list = None) -> TextbookExampleSource:
    return TextbookExampleSource(
        skill_id="vh_數學B1_GeneralFormOfLinearEquation",
        textbook_example_id=example_id,
        question_text=text,
        answer="mock",
        choices=choices or [],
        explanation="mock explanation",
        source_label="mock label",
        source_type="mock type",
        presentation_mode="short_answer",
        question_type="mock qtype",
        source_hash=f"hash_{example_id}",
    )


def test_deterministic_classification_slope_general_or_intercept():
    src = _make_source(4565, "試求下列各直線的斜率： (1) 3x − 2y + 1 = 0 (2) x/2 - y/5 = 1")
    entry = {"allowed_problem_types": ["slope_from_general_or_intercept_form"]}
    
    # We patch Gemini client to ensure it is NOT called for deterministic rules
    with mock.patch("core.gencode.gencode_ai_resolve.resolve_gencode_ai_client") as mock_ai:
        res = classify_textbook_example(src, entry)
        assert not mock_ai.called
        assert res["problem_type_id"] == "slope_from_general_or_intercept_form"
        assert res["classification_source"] == "deterministic"


def test_deterministic_classification_parallel_point():
    src = _make_source(4566, "已知直線 L2 通過點 (-2,3) 且與直線 L1: x+2y-3=0 平行，試求 L2 的直線方程式。")
    entry = {"allowed_problem_types": ["line_through_point_parallel_to_line"]}
    res = classify_textbook_example(src, entry)
    assert res["problem_type_id"] == "line_through_point_parallel_to_line"


def test_deterministic_classification_perpendicular_point():
    src = _make_source(4567, "已知直線 L2 通過點 (-1,3) 且與直線 L1: 2x-3y+1=0 垂直，試求 L2 的直線方程式。")
    entry = {"allowed_problem_types": ["line_through_point_perpendicular_to_line"]}
    res = classify_textbook_example(src, entry)
    assert res["problem_type_id"] == "line_through_point_perpendicular_to_line"


def test_deterministic_classification_perpendicular_parameter():
    src = _make_source(4593, "設兩直線L1: ax-3y+5=0、L2: 3x+4y-5=0，若L1 垂直於 L2，則a =")
    entry = {"allowed_problem_types": ["perpendicular_condition_parameter"]}
    res = classify_textbook_example(src, entry)
    assert res["problem_type_id"] == "perpendicular_condition_parameter"


def test_deterministic_classification_intersection_parallel():
    src = _make_source(4597, "通過兩直線 3x-y-6=0 與 x+3y-2=0 的交點，並與直線 x+y-1=0 平行的直線方程式為")
    entry = {"allowed_problem_types": ["line_through_intersection_parallel_to_line"]}
    res = classify_textbook_example(src, entry)
    assert res["problem_type_id"] == "line_through_intersection_parallel_to_line"


def test_deterministic_classification_perpendicular_bisector():
    src = _make_source(4599, "公路上的任意一點到兩城市的距離相等，則此公路所在的直線方程式為")
    entry = {"allowed_problem_types": ["perpendicular_bisector_application"]}
    res = classify_textbook_example(src, entry)
    assert res["problem_type_id"] == "perpendicular_bisector_application"


def test_ai_fallback_classification():
    src = _make_source(9999, "This is a complex geometric word problem about coordinates and distance.")
    entry = {"allowed_problem_types": ["coordinate_geometry_word_problem"]}
    
    mock_client = mock.MagicMock()
    mock_resp = mock.MagicMock()
    mock_resp.text = '{"problem_type_id": "coordinate_geometry_word_problem", "math_family": "line_equation", "confidence": 0.9}'
    mock_client.generate_content.return_value = mock_resp
    
    with mock.patch("core.gencode.gencode_ai_resolve.resolve_gencode_ai_client", return_value=(mock_client, {})):
        res = classify_textbook_example(src, entry)
        assert res["problem_type_id"] == "coordinate_geometry_word_problem"
        assert res["classification_source"] == "ai_fallback"


def test_ai_fallback_invalid_type_raises():
    src = _make_source(9999, "This is a complex geometric word problem about coordinates and distance.")
    entry = {"allowed_problem_types": ["coordinate_geometry_word_problem"]}
    
    mock_client = mock.MagicMock()
    mock_resp = mock.MagicMock()
    mock_resp.text = '{"problem_type_id": "unsupported_type", "math_family": "line_equation"}'
    mock_client.generate_content.return_value = mock_resp
    
    with mock.patch("core.gencode.gencode_ai_resolve.resolve_gencode_ai_client", return_value=(mock_client, {})):
        with pytest.raises(ValueError, match="classification_failed"):
            classify_textbook_example(src, entry)
