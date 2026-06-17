# -*- coding: utf-8 -*-
"""Regression tests for V3 slope-intercept skill contracts."""

from __future__ import annotations

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload
from core.gencode.pipeline_orchestrator import build_v3_component_draft_from_skill

SKILL_ID = "vh_數學B1_SlopeInterceptForm"


def test_slope_intercept_equation_short_answer_contract():
    matrix = build_line_equation_matrix(
        seed=1,
        line_type="slope_intercept_equation",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={"slope": "-2/3", "y_intercept": "-1"},
    )
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="expression",
        problem_type_id="slope_intercept_equation",
    )

    assert payload["presentation_mode"] == "short_answer"
    assert payload["choices"] == []
    assert payload["answer"] == payload["correct_answer"]
    assert payload["semantic_answer"] == payload["answer"]
    assert payload["display_answer"].startswith("\\(")
    assert "/" not in payload["question_text"]
    assert payload["answer_contract"]["checker"] == "linear_equation_equivalent_checker"


def test_slope_intercept_find_x_intercept_single_choice_contract():
    matrix = build_line_equation_matrix(
        seed=1,
        line_type="slope_intercept_find_x_intercept",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={"slope": "-5/3", "y_intercept": "10/3"},
    )
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        answer_type="single_choice",
        problem_type_id="slope_intercept_find_x_intercept",
    )

    assert payload["presentation_mode"] == "single_choice"
    assert len(payload["choices"]) >= 4
    assert payload["answer"] == payload["correct_answer"]
    assert payload["answer"] in {"A", "B", "C", "D"}
    assert payload["semantic_answer"]
    assert payload["display_answer"].startswith("\\(")
    assert "/" not in payload["question_text"]
    assert payload["answer_contract"]["checker"] == "choice_label_checker"
    assert all("y=" not in str(choice["text"]).replace(" ", "") for choice in payload["choices"])
    assert all("x=" not in str(choice["text"]).replace(" ", "") for choice in payload["choices"])
    assert len({choice["text"] for choice in payload["choices"]}) == len(payload["choices"])
    assert all("\\frac" in str(choice["text"]) or "/" not in str(choice["text"]) for choice in payload["choices"])


def test_slope_intercept_read_slope_and_intercept_short_answer_contract():
    matrix = build_line_equation_matrix(
        seed=2,
        line_type="slope_intercept_read_slope_and_intercept",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={"slope": "3/2", "y_intercept": "-4"},
    )
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="text_short",
        problem_type_id="slope_intercept_read_slope_and_intercept",
    )

    assert payload["presentation_mode"] == "short_answer"
    assert payload["choices"] == []
    assert payload["answer"] == payload["correct_answer"]
    assert payload["semantic_answer"] == payload["answer"]
    assert payload["display_answer"].startswith("\\(")
    assert "/" not in payload["question_text"]
    assert payload["answer_contract"]["checker"] == "text_short_checker"


def test_slope_intercept_components_vary_by_seed():
    samples = []
    for seed in range(20):
        matrix = build_line_equation_matrix(
            seed=seed,
            line_type="slope_intercept_equation",
            curriculum_profile="vocational_high_b",
            difficulty_profile="easy",
            constraints={"slope": "-2/3", "y_intercept": "-1"},
        )
        answer = matrix["answer"]
        samples.append((str(answer["slope"]), str(answer["intercept"])))

    assert len(set(samples)) >= 5


def test_v3_draft_infers_self_assessment_x_intercept_choice_contract():
    row = {
        "id": 4605,
        "skill_id": SKILL_ID,
        "problem_type": "self_assessment",
        "source_description": "CH1自我評量 題8",
        "problem_text": (
            "設直線 \\(L\\) 之斜率為 \\(-\\frac{5}{3}\\)，且 \\(L\\) 之 "
            "\\(y\\) 截距為 \\(\\frac{10}{3}\\)，則 \\(L\\) 之 \\(x\\) 截距為"
            "　　(A) \\(-1\\)　(B) \\(\\frac{1}{2}\\)　(C) \\(1\\)　(D) \\(2\\)。"
        ),
        "correct_answer": "",
    }
    draft = build_v3_component_draft_from_skill(
        SKILL_ID,
        textbook_example_id=4605,
        source_kind="test_4605",
        seed=42,
        textbook_row=row,
    )

    assert draft["line_type"] == "slope_intercept_find_x_intercept"
    assert draft["presentation_mode"] == "single_choice"
    assert draft["answer_type"] == "single_choice"
    assert draft["problem_type_id"] == "slope_intercept_find_x_intercept"
