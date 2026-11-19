# -*- coding: utf-8 -*-
"""Regression: src_4603 slope/intercept multipart rational contract."""

from __future__ import annotations

from agent_skills_v3.vh_數學B1_SlopeInterceptForm.components.src_4603.generate import (
    generate as generate_4603,
)
from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.answer_grading import build_correct_answer_display
from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload
from core.gencode.practice_quality_gates import run_practice_quality_gates
from core.gencode.runtime_skill_wrapper import check_answer


def test_student_case_y_equals_2x_minus_5_over_4():
    matrix = build_line_equation_matrix(
        seed=19,
        line_type="slope_intercept_read_slope_and_intercept",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={"slope": "2", "y_intercept": "-5/4"},
    )
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="multi_part",
        problem_type_id="slope_intercept_read_slope_and_intercept",
        component_id="src_4603",
        textbook_example_id=4603,
    )
    assert payload["answer_type"] == "multi_part"
    assert payload["semantic_answer"] == {"m": "2", "b": "-5/4"}
    assert payload["answer_contract"]["checker"] == "multi_part_answer_checker"
    part_keys = [row["key"] for row in payload["answer_contract"]["parts"]]
    assert part_keys == ["m", "b"]
    assert all(row["checker"] == "rational_checker" for row in payload["answer_contract"]["parts"])

    assert check_answer({"m": "2", "b": "-5/4"}, payload["correct_answer"], payload=payload)
    assert check_answer({"m": "2", "b": "-1.25"}, payload["correct_answer"], payload=payload)
    assert check_answer(
        {"m": "2", "b": r"\frac{-5}{4}"},
        payload["correct_answer"],
        payload=payload,
    )
    assert not check_answer({"m": "2", "b": ""}, payload["correct_answer"], payload=payload)
    assert not check_answer({"m": "2"}, payload["correct_answer"], payload=payload)
    assert not check_answer(
        "m = 2, b = -5/4",
        payload["correct_answer"],
        payload=payload,
    )

    display = build_correct_answer_display(payload)
    assert display and display.get("items")
    gate = run_practice_quality_gates(payload)
    assert gate["passed"], gate["blockers"]


def test_src_4603_component_multipart_seeds():
    for seed in range(40):
        payload = generate_4603(seed=seed, component_id="src_4603")
        assert payload["answer_type"] == "multi_part"
        semantic = payload["semantic_answer"]
        assert set(semantic.keys()) == {"m", "b"}
        assert check_answer(semantic, payload["correct_answer"], payload=payload)
        wrong = {"m": semantic["m"], "b": "999"}
        assert not check_answer(wrong, payload["correct_answer"], payload=payload)
        gate = run_practice_quality_gates(payload)
        assert gate["passed"], gate["blockers"]


def test_legacy_combined_string_session_still_gradable_via_own_contract():
    """Old in-flight sessions keep their stored exact_string contract untouched."""
    legacy_answer = "m = 2, b = -5/4"
    legacy_payload = {
        "answer_type": "text_short",
        "correct_answer": legacy_answer,
        "semantic_answer": legacy_answer,
        "answer_contract": {
            "answer_type": "text_short",
            "checker": "text_short_checker",
            "checker_key": "text_short_checker",
            "equivalence": "exact_string",
            "semantic_answer": legacy_answer,
        },
    }
    assert check_answer(legacy_answer, legacy_answer, payload=legacy_payload)
    assert not check_answer("m = 2", legacy_answer, payload=legacy_payload)
