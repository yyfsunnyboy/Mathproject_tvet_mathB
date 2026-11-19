# -*- coding: utf-8 -*-
"""Regression: named-segment slopes must match final stem/visual coordinates."""

from __future__ import annotations

from fractions import Fraction

import pytest

from agent_skills_v3.vh_數學B1_SlopeOfALine.components.src_4519.generate import (
    generate as generate_4519,
)
from agent_skills_v3.vh_數學B1_SlopeOfALine.components.src_4533.generate import (
    generate as generate_4533,
)
from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload
from core.gencode.practice_quality_gates import run_practice_quality_gates
from core.gencode.runtime_skill_wrapper import check_answer


def _oracle_slope(p1: list[int], p2: list[int]) -> str:
    x1, y1 = int(p1[0]), int(p1[1])
    x2, y2 = int(p2[0]), int(p2[1])
    if x1 == x2:
        return "不存在"
    value = Fraction(y2 - y1, x2 - x1)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _assert_payload_matches_oracle(payload: dict) -> set[str]:
    meta = payload.get("metadata") or {}
    math_core = payload.get("math_core") or {}
    givens = meta.get("raw_givens") or math_core.get("raw_givens") or {}
    points = givens.get("points") or {}
    segments = givens.get("segments") or []
    semantic = payload.get("semantic_answer") or {}
    visual = payload.get("visual_spec") or {}

    assert points and segments and semantic
    visual_points = {
        item["label"]: [item["x"], item["y"]]
        for item in visual.get("points") or []
    }
    assert visual_points == {k: list(v) for k, v in points.items()}

    seen_kinds: set[str] = set()
    shared: dict[str, int] = {}
    for index, seg in enumerate(segments):
        a_lbl, b_lbl = seg["from"], seg["to"]
        shared[a_lbl] = shared.get(a_lbl, 0) + 1
        shared[b_lbl] = shared.get(b_lbl, 0) + 1
        oracle = _oracle_slope(points[a_lbl], points[b_lbl])
        key = f"part_{index + 1}"
        assert semantic[key] == oracle
        assert list(seg["points"][0]) == list(points[a_lbl])
        assert list(seg["points"][1]) == list(points[b_lbl])
        line = (visual.get("lines") or [])[index]
        assert line["through_points"] == [a_lbl, b_lbl]
        assert str(line.get("slope")) == oracle
        if oracle == "不存在":
            seen_kinds.add("vertical")
        elif oracle == "0":
            seen_kinds.add("horizontal")
        elif oracle.startswith("-"):
            seen_kinds.add("neg")
        else:
            seen_kinds.add("pos")

    assert max(shared.values()) >= 2
    assert check_answer(semantic, payload["correct_answer"], payload=payload)
    wrong = dict(semantic)
    first = next(iter(wrong))
    wrong[first] = "999"
    assert not check_answer(wrong, payload["correct_answer"], payload=payload)
    gate = run_practice_quality_gates(payload)
    assert gate["passed"], gate["blockers"]
    return seen_kinds


@pytest.mark.parametrize("component_id,generate", [("src_4519", generate_4519), ("src_4533", generate_4533)])
def test_named_segment_components_300_seeds_oracle(component_id, generate):
    kind_union = set()
    for seed in range(300):
        payload = generate(seed=seed, component_id=component_id)
        kind_union |= _assert_payload_matches_oracle(payload)
    assert {"pos", "neg", "horizontal", "vertical"} <= kind_union


def test_student_case_bc_ec_bf_cf_regression():
    """2026/11/19 student report: B(5,-2) C(1,-6) E(-3,-1) F(1,2)."""
    matrix = build_line_equation_matrix(
        seed=19,
        line_type="slopes_of_named_segments",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={
            "fixed_points": {
                "B": [5, -2],
                "C": [1, -6],
                "E": [-3, -1],
                "F": [1, 2],
            },
            "fixed_segments": ["BC", "EC", "BF", "CF"],
        },
    )
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        domain_operation="slopes_of_named_segments",
        answer_type="multi_part",
        problem_type_id="slopes_of_named_segments",
        component_id="src_4519",
    )
    expected = {
        "part_1": "1",
        "part_2": "-5/4",
        "part_3": "-1",
        "part_4": "不存在",
    }
    assert payload["semantic_answer"] == expected
    assert check_answer(expected, payload["correct_answer"], payload=payload)
    assert check_answer(
        {"part_1": "1", "part_2": "-1.25", "part_3": "-1", "part_4": "不存在"},
        payload["correct_answer"],
        payload=payload,
    )
    # System used to show the wrong key for this geometry.
    wrong_system_answers = {
        "part_1": "-1",
        "part_2": "3/2",
        "part_3": "0",
        "part_4": "不存在",
    }
    assert not check_answer(wrong_system_answers, payload["correct_answer"], payload=payload)
    gate = run_practice_quality_gates(payload)
    assert gate["passed"], gate["blockers"]
