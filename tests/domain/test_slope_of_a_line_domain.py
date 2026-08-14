# -*- coding: utf-8 -*-
"""Focused tests for SlopeOfALine operations on line_equation domain."""

from __future__ import annotations

from fractions import Fraction

import pytest

from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.answer_schema_registry import resolve_answer_schema_key, validate_answer_schema
from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload
from core.gencode.runtime_skill_wrapper import check_answer
from core.registry.domain_operation_registry import get_domain_spec
from core.registry.taxonomy_registry import resolve_domain_for_skill

MATRIX_FIELDS = (
    "givens",
    "answer",
    "distractors",
    "explanation_steps",
    "validation_facts",
    "visual_spec",
)

SLOPE_OPS = (
    "slope_from_two_points",
    "solve_parameter_from_known_slope",
    "solve_parameter_from_known_slope_choice",
    "collinear_three_points_parameter",
    "collinear_three_points_parameter_choice",
    "non_triangle_collinear_parameter",
    "parallel_segments_parameter",
    "perpendicular_segments_parameter",
    "slopes_of_named_segments",
    "classify_and_compare_figure_slopes",
)


def _build(line_type: str, seed: int = 42, **extra: object) -> dict:
    return build_line_equation_matrix(
        seed=seed,
        line_type=line_type,
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        **extra,
    )


def _slope(x1: int, y1: int, x2: int, y2: int) -> Fraction | str:
    if x1 == x2:
        return "不存在"
    return Fraction(y2 - y1, x2 - x1)


def test_taxonomy_and_registry_wire_slope_of_a_line():
    routing = resolve_domain_for_skill("vh_數學B1_SlopeOfALine")
    assert routing["fixed_domain_key"] == "coordinate_geometry.line_equation"
    assert routing["entrypoint"] == "build_line_equation_matrix"
    allowed = set(routing.get("allowed_types") or [])
    assert set(SLOPE_OPS) <= allowed
    spec = get_domain_spec("coordinate_geometry.line_equation")
    for op in SLOPE_OPS:
        assert op in spec.operations


@pytest.mark.parametrize("op", SLOPE_OPS)
def test_each_operation_has_six_matrix_fields(op: str):
    matrix = _build(op, seed=11)
    assert set(matrix.keys()) >= set(MATRIX_FIELDS)
    assert matrix["validation_facts"]["task_type"] == op
    schema_key = resolve_answer_schema_key(domain_operation=op)
    assert schema_key
    validate_answer_schema(matrix["answer"], answer_schema_key=schema_key, domain_operation=op)


def test_horizontal_and_vertical_two_point_slopes():
    h = _build("slope_from_two_points", seed=3, constraints={"line_kind": "horizontal"})
    assert h["answer"]["canonical_form"] == "0"
    assert h["answer"]["slope"] == "0"
    v = _build("slope_from_two_points", seed=5, constraints={"line_kind": "vertical"})
    assert v["answer"]["canonical_form"] == "不存在"
    assert v["answer"]["slope"] == "不存在"


def test_positive_negative_and_fraction_slopes():
    seen_pos = seen_neg = seen_frac = False
    for seed in range(1, 80):
        matrix = _build("slope_from_two_points", seed=seed, constraints={"line_kind": "oblique"})
        pa = matrix["givens"]["point_a"]
        pb = matrix["givens"]["point_b"]
        expected = _slope(int(pa[0]), int(pa[1]), int(pb[0]), int(pb[1]))
        assert isinstance(expected, Fraction)
        got = Fraction(str(matrix["answer"]["canonical_form"]))
        assert got == expected
        assert got.denominator > 0
        if got > 0:
            seen_pos = True
        if got < 0:
            seen_neg = True
        if got.denominator > 1:
            seen_frac = True
        if seen_pos and seen_neg and seen_frac:
            break
    assert seen_pos and seen_neg and seen_frac


def test_multi_segment_slopes_accept_reject():
    matrix = _build(
        "slopes_of_named_segments",
        seed=8,
        constraints={"segment_kinds": ["oblique_neg", "oblique_pos", "horizontal", "vertical"]},
    )
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        domain_operation="slopes_of_named_segments",
        answer_type="multi_part",
    )
    assert payload["answer_type"] == "multi_part"
    parts = payload["answer_contract"]["parts"]
    assert len(parts) >= 4
    assert "不存在" in str(payload.get("semantic_answer") or payload.get("answer") or "")
    assert check_answer(payload["semantic_answer"], payload["correct_answer"], payload=payload)
    wrong = dict(payload["semantic_answer"])
    first_key = next(iter(wrong))
    wrong[first_key] = "999"
    assert not check_answer(wrong, payload["correct_answer"], payload=payload)


def test_figure_classify_compare_six_slot_contract():
    matrix = _build("classify_and_compare_figure_slopes", seed=4)
    assert set(matrix.keys()) >= set(MATRIX_FIELDS)
    visual = matrix["visual_spec"]
    assert visual["kind"] == "coordinate_plane_multi_figure"
    assert len(visual["figures"]) == 4
    assert len(visual["comparisons"]) == 2
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        domain_operation="classify_and_compare_figure_slopes",
        answer_type="multi_part",
    )
    parts = payload["answer_contract"]["parts"]
    assert len(parts) == 6
    assert {p["key"] for p in parts} == {"fig1", "fig2", "fig3", "fig4", "cmp1", "cmp2"}
    assert check_multi_part_answer(
        payload["semantic_answer"],
        payload["correct_answer"],
        answer_contract=payload["answer_contract"],
    )["overall_correct"]
    bad = dict(payload["semantic_answer"])
    bad["fig1"] = "m<0"
    assert not check_multi_part_answer(
        bad,
        payload["correct_answer"],
        answer_contract=payload["answer_contract"],
    )["overall_correct"]


def test_collinear_and_non_triangle_share_kernel():
    for op in ("collinear_three_points_parameter", "non_triangle_collinear_parameter"):
        matrix = _build(op, seed=21)
        a = matrix["givens"]["point_a"]
        b_x = int(matrix["givens"]["point_b"][0])
        c = matrix["givens"]["point_c"]
        k = int(matrix["answer"]["parameter"])
        m1 = _slope(int(a[0]), int(a[1]), b_x, k)
        m2 = _slope(b_x, k, int(c[0]), int(c[1]))
        assert m1 == m2


def test_parallel_and_perpendicular_segments():
    parallel = _build("parallel_segments_parameter", seed=17)
    a, b = parallel["givens"]["point_a"], parallel["givens"]["point_b"]
    c, d = parallel["givens"]["point_c"], parallel["givens"]["point_d"]
    bx = int(parallel["answer"]["parameter"])
    m_ab = _slope(int(a[0]), int(a[1]), bx, int(b[1]))
    m_cd = _slope(int(c[0]), int(c[1]), int(d[0]), int(d[1]))
    assert m_ab == m_cd

    perp = _build("perpendicular_segments_parameter", seed=19)
    a, b = perp["givens"]["point_a"], perp["givens"]["point_b"]
    c, d = perp["givens"]["point_c"], perp["givens"]["point_d"]
    cy = int(perp["answer"]["parameter"])
    m_ab = _slope(int(a[0]), int(a[1]), int(b[0]), int(b[1]))
    m_cd = _slope(int(c[0]), cy, int(d[0]), int(d[1]))
    assert isinstance(m_ab, Fraction) and isinstance(m_cd, Fraction)
    assert m_ab * m_cd == -1


def test_choice_contract_with_semantic_value():
    matrix = _build("collinear_three_points_parameter_choice", seed=13)
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        domain_operation="collinear_three_points_parameter_choice",
    )
    assert payload["presentation_mode"] == "single_choice"
    assert payload["correct_answer"] in {"A", "B", "C", "D"}
    assert str(payload["semantic_answer"]).strip() == str(matrix["answer"]["value"])
    assert check_answer(payload["correct_answer"], payload["correct_answer"], payload=payload)
    wrong_label = next(lbl for lbl in ("A", "B", "C", "D") if lbl != payload["correct_answer"])
    assert not check_answer(wrong_label, payload["correct_answer"], payload=payload)


def test_multi_seed_variation():
    stems = set()
    answers = set()
    for seed in range(1, 12):
        matrix = _build("slope_from_two_points", seed=seed, constraints={"line_kind": "oblique"})
        payload = convert_line_equation_matrix_to_question_payload(
            matrix,
            presentation_mode="short_answer",
            domain_operation="slope_from_two_points",
        )
        stems.add(str(payload.get("question_text") or ""))
        answers.add(str(matrix["answer"]["canonical_form"]))
    assert len(stems) >= 5
    assert len(answers) >= 3


def test_existing_line_equation_regression_smoke():
    for op in (
        "point_slope",
        "two_points",
        "slope_from_general_form",
        "compare_line_slopes",
        "parallel_condition_parameter",
    ):
        matrix = _build(op, seed=7)
        assert set(matrix.keys()) >= set(MATRIX_FIELDS)
        convert_line_equation_matrix_to_question_payload(matrix, domain_operation=op)
