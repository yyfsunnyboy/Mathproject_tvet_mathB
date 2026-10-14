# -*- coding: utf-8 -*-
from __future__ import annotations

from fractions import Fraction

from core.domain.trigonometry_angle_domain import (
    build_trigonometry_angle_matrix,
    clock_hour_interval_clockwise,
    degrees_to_pi_coeff,
    is_coterminal_degrees,
    min_pos_max_neg_degrees,
    min_pos_max_neg_pi,
    sector_arc_length_pi_coeff,
    sector_area_pi_coeff,
)
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
from core.gencode.services.failed_component_recovery_service import _has_executable_adapter_route
from core.registry.domain_operation_registry import get_operation_spec


def test_example1_gt_locked() -> None:
    matrix = build_trigonometry_angle_matrix(
        seed=1,
        domain_operation="convert_angle_measure",
        constraints={
            "variant": "two_way",
            "items": [
                {"kind": "deg_to_rad", "degrees": 135},
                {"kind": "rad_to_deg", "pi_coeff": "-5/3"},
            ],
        },
    )
    parts = matrix["answer"]["parts"]
    assert parts["part_1"] == "3*pi/4"
    assert parts["part_2"] == "-300"


def test_example2_gt_locked() -> None:
    matrix = build_trigonometry_angle_matrix(
        seed=1,
        domain_operation="sector_arc_and_area",
        constraints={"variant": "equal_slices", "radius": 16, "slices": 8},
    )
    parts = matrix["answer"]["parts"]
    assert parts["part_1"] == "32*pi"
    assert parts["part_2"] == "4*pi"


def test_sdg_sector_gt_locked() -> None:
    matrix = build_trigonometry_angle_matrix(
        seed=1,
        domain_operation="sector_arc_and_area",
        constraints={
            "variant": "given_angle",
            "radius": 1,
            "theta_degrees": 110,
            "include_convert": False,
        },
    )
    parts = matrix["answer"]["parts"]
    assert parts["part_1"] == "11*pi/18"
    assert parts["part_2"] == "11*pi/36"


def test_example3_gt_locked() -> None:
    matrix = build_trigonometry_angle_matrix(
        seed=1,
        domain_operation="coterminal_angles",
        constraints={
            "variant": "identify_which",
            "unit": "deg",
            "degrees": 50,
            "candidates": [-310, 770, 1250],
        },
    )
    assert matrix["answer"]["value"] == "1,2"
    assert is_coterminal_degrees(-310, 50)
    assert is_coterminal_degrees(770, 50)
    assert not is_coterminal_degrees(1250, 50)


def test_example4_gt_locked() -> None:
    pos, neg = min_pos_max_neg_degrees(1350)
    assert pos == 270
    assert neg == -90
    pos, neg = min_pos_max_neg_degrees(-1100)
    assert pos == 340
    assert neg == -20
    pos, neg = min_pos_max_neg_pi(Fraction(-21, 4))
    assert pos == Fraction(3, 4)
    assert neg == Fraction(-5, 4)
    matrix = build_trigonometry_angle_matrix(
        seed=1,
        domain_operation="coterminal_angles",
        constraints={
            "variant": "min_pos_max_neg",
            "items": [
                {"unit": "deg", "degrees": 1350},
                {"unit": "deg", "degrees": -1100},
                {"unit": "rad", "pi_coeff": "-21/4"},
            ],
        },
    )
    parts = matrix["answer"]["parts"]
    assert parts["part_1_pos"] == "270"
    assert parts["part_1_neg"] == "-90"
    assert parts["part_2_pos"] == "340"
    assert parts["part_2_neg"] == "-20"
    assert parts["part_3_pos"] == "3*pi/4"
    assert parts["part_3_neg"] == "-5*pi/4"


def test_special_angle_table_blanks() -> None:
    matrix = build_trigonometry_angle_matrix(
        seed=1,
        domain_operation="convert_angle_measure",
        constraints={"variant": "special_angle_table", "filled_radian_degrees": [30, 90, 180, 270]},
    )
    parts = matrix["answer"]["parts"]
    assert parts["c0"] == "0"
    assert "c1" not in parts  # 30 filled
    assert parts["c2"] == "pi/4"
    assert matrix["givens"]["question_text"]


def test_sector_formulas() -> None:
    k = degrees_to_pi_coeff(45)
    assert k == Fraction(1, 4)
    assert sector_area_pi_coeff(16, k) == 32
    assert sector_arc_length_pi_coeff(16, k) == 4


def test_clock_2019_not_used_as_gt() -> None:
    assert clock_hour_interval_clockwise(2019) == (7, 8)


OPS = ["convert_angle_measure", "sector_arc_and_area", "coterminal_angles"]


def test_adapter_generic_full_matrix() -> None:
    for op in OPS:
        matrix = build_trigonometry_angle_matrix(seed=7, domain_operation=op)
        payload = convert_domain_matrix_to_question_payload(
            matrix,
            presentation_mode="short_answer",
            answer_type="expression",
            problem_type_id=op,
            domain_operation=op,
        )
        assert isinstance(payload, dict)
        assert str(payload.get("question_text") or "").strip()
        assert payload.get("answer") is not None


def test_adapter_route_readiness() -> None:
    for op in OPS:
        spec = get_operation_spec("trigonometry.angle", op)
        assert spec is not None
        assert _has_executable_adapter_route(
            selected_operation=op,
            domain_module="core.domain.trigonometry_angle_domain",
            impl_fn_name=spec.handler,
            presentation_mode="short_answer",
            answer_type="expression",
        )
