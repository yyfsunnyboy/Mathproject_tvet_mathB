from __future__ import annotations

import re

from core.domain.trigonometry_oblique_triangle_measurement_domain import (
    build_trigonometry_oblique_triangle_measurement_matrix,
)
from core.domain.trigonometry_right_triangle_measurement_domain import (
    DECIMAL_HEIGHT_OP,
    TWO_ELEV_SHIFT_OP,
    build_trigonometry_right_triangle_measurement_matrix,
)
from core.domain.trigonometry_solid_measurement_domain import (
    TOWER_RIVER_OP,
    build_trigonometry_solid_measurement_matrix,
)
from core.gencode.numeric_display import format_display_number
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload


def test_display_number_removes_integral_float_tail_without_losing_decimal():
    assert format_display_number(120.0) == "120"
    assert format_display_number(55.0) == "55"
    assert format_display_number(1.25) == "1.25"
    assert format_display_number(1.2, decimal_places=3) == "1.200"


def test_decimal_height_stem_has_no_float_tail_and_keeps_answer_contract():
    matrix = build_trigonometry_right_triangle_measurement_matrix(
        operation=DECIMAL_HEIGHT_OP,
        sight_length=120,
        elevation_degrees=55,
        precision=3,
    )
    assert "$120$" in matrix["question_text"]
    assert "$55^\\circ$" in matrix["question_text"]
    assert ".000000" not in matrix["question_text"]
    assert matrix["answer"]["canonical_form"] == "98.298"


def test_two_elevation_shift_stem_defines_unique_collinear_direction():
    matrix = build_trigonometry_right_triangle_measurement_matrix(
        operation=TWO_ELEV_SHIFT_OP,
        seed=3,
    )
    stem = matrix["question_text"]
    for phrase in ("同一直線", "同側", "較近觀測點", "背離目標", "較遠觀測點"):
        assert phrase in stem


def test_river_width_stem_defines_points_perpendicular_and_width_segment():
    matrix = build_trigonometry_solid_measurement_matrix(operation=TOWER_RIVER_OP, seed=4)
    stem = matrix["question_text"]
    for phrase in ("塔底為 C", "A、B 為地面觀測點", "AC 垂直河岸", "AB 沿河岸", "AC\\perp AB", "AB 代表河寬"):
        assert phrase in stem


def _assert_diagram_matches_givens(matrix):
    givens = matrix["givens"]
    spec = matrix["diagram_spec"]
    assert spec["version"] == 1
    assert spec["type"] == "triangle"
    assert spec["vertices"] == ["A", "B", "C"]
    if matrix["validation_facts"]["domain_operation"] == "solve_side_by_law_of_sines":
        assert spec["parameters"]["angles_deg"] == {
            "A": givens["known_angle_degrees"],
            "C": givens["target_angle_degrees"],
        }
        assert spec["parameters"]["sides"] == {"a": givens["known_side"]}
        assert spec["show"]["unknown_sides"] == ["c"]
    else:
        assert spec["parameters"]["angles_deg"] == {"A": givens["included_angle_degrees"]}
        assert spec["parameters"]["sides"] == {"b": givens["side_b"], "c": givens["side_c"]}
        assert spec["show"]["unknown_sides"] == ["a"]


def test_oblique_triangle_100_samples_never_claim_non_right_for_90_degrees():
    for seed in range(100):
        matrix = build_trigonometry_oblique_triangle_measurement_matrix(
            operation="solve_side_by_law_of_cosines",
            seed=seed,
        )
        assert matrix["givens"]["included_angle_degrees"] != 90
        assert "非直角" in matrix["question_text"]


def test_oblique_triangle_50_sample_diagram_smoke():
    for seed in range(50):
        operation = "solve_side_by_law_of_sines" if seed % 2 == 0 else "solve_side_by_law_of_cosines"
        matrix = build_trigonometry_oblique_triangle_measurement_matrix(operation=operation, seed=seed)
        _assert_diagram_matches_givens(matrix)
        assert not re.search(r"\\d+\\.\\d{8,}", matrix["question_text"])


def test_diagram_spec_survives_domain_matrix_adapter():
    matrix = build_trigonometry_oblique_triangle_measurement_matrix(
        operation="solve_side_by_law_of_sines",
        seed=9,
    )
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="expression",
        problem_type_id="solve_side_by_law_of_sines",
        domain_operation="solve_side_by_law_of_sines",
    )
    assert payload["diagram_spec"] == matrix["diagram_spec"]
