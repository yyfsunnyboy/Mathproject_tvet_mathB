"""Typography-only regression checks for shared line-equation stems."""

from __future__ import annotations

import re
from copy import deepcopy

import pytest

from core.domain.coordinate_geometry.line_equation_domain import (
    build_graph_based_linear_application_inverse_matrix,
    build_line_equation_matrix,
)
from core.gencode.domain_matrix_adapter import (
    convert_line_equation_matrix_to_question_payload,
)


def _payload(operation: str, *, seed: int = 0) -> tuple[dict, dict]:
    matrix = build_line_equation_matrix(
        seed=seed,
        line_type=operation,
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
    )
    original_answer = deepcopy(matrix["answer"])
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        domain_operation=operation,
    )
    assert matrix["answer"] == original_answer
    return matrix, payload


@pytest.mark.parametrize(
    ("operation", "required_tokens"),
    (
        (
            "distance_from_point_to_line",
            ("$(2, 1)$", "$L: -7x + 24y - 2 = 0$"),
        ),
        (
            "distance_from_point_to_line_parameter",
            ("$(-2, 2)$", "$L: -7x + 24y + a = 0$", "$4$", "$a$"),
        ),
        (
            "compare_point_to_line_distances",
            ("$P(-1,3)$", "$L_1: -7x + 24y - 2 = 0$", "$P$"),
        ),
        (
            "perpendicular_bisector_application",
            ("$A(0,6)$", "$B(-6,-2)$", "$AB$"),
        ),
        ("slope_from_two_points", ("$A(0,6)$", "$B(-6,6)$")),
        ("slope_intercept_equation", ("\\(2\\)", "$y$", "\\(-\\frac{4}{3}\\)")),
    ),
)
def test_mixed_line_stems_group_each_math_atom(
    operation: str,
    required_tokens: tuple[str, ...],
) -> None:
    _, payload = _payload(operation)
    question_text = str(payload["question_text"])
    assert all(token in question_text for token in required_tokens)
    assert question_text.count("$") % 2 == 0
    assert question_text.count("\\(") == question_text.count("\\)")
    assert "$$" not in question_text


@pytest.mark.parametrize(
    ("operation", "expected_question"),
    (
        (
            "parallel_segments_parameter",
            "設 A(2,1)、B(a,5)、C(0,6)、D(-6,-2)，若線段 AB 與 CD 平行，試求 a 之值。",
        ),
        (
            "triangle_right_angle_verification",
            "已知坐標平面上三點 A(6,0)、B(-6,-2) 及 C(2,1)，試問 △ABC 是否為直角三角形？",
        ),
        (
            "collinear_three_points_parameter",
            "若 A(0,6)、B(-6,k)、C(-2,2) 三點共線，試求 k 之值。",
        ),
    ),
)
def test_readable_all_plain_line_stems_remain_unchanged(
    operation: str,
    expected_question: str,
) -> None:
    _, payload = _payload(operation)
    assert payload["question_text"] == expected_question


def test_linear_application_wraps_only_identifiers_around_existing_math() -> None:
    matrix = build_graph_based_linear_application_inverse_matrix(seed=0)
    question_text = str(matrix["question"])
    assert "$x$" in question_text
    assert "$y$" in question_text
    assert re.search(r"\$y=\d+x\+\d+\$", question_text)
    assert "$$" not in question_text
