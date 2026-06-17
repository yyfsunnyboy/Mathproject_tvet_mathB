# -*- coding: utf-8 -*-
"""Practice API should preserve V3 runtime contract fields."""

from __future__ import annotations

from core.gencode.answer_payload import refresh_runtime_question_session
from core.routes.practice import _v3_runtime_contract_api_fields


def test_runtime_contract_helper_preserves_short_answer_fields():
    payload = refresh_runtime_question_session(
        {
            "question_text": "試求通過兩點之直線方程式。",
            "answer": "x = 6",
            "correct_answer": "x = 6",
            "presentation_mode": "short_answer",
            "answer_type": "expression",
            "problem_type_id": "write_line_equation_from_point_slope",
            "component_id": "src_4544",
            "textbook_example_id": 4544,
            "semantic_answer": "x = 6",
            "metadata": {
                "presentation_mode": "short_answer",
                "semantic_answer": "x = 6",
                "problem_type_id": "write_line_equation_from_point_slope",
            },
            "answer_contract": {
                "presentation_mode": "short_answer",
                "answer_type": "expression",
                "checker": "linear_equation_equivalent_checker",
            },
            "choices": [],
        },
        skill_id="vh_數學B1_HorizontalAndVerticalLineEquations",
    )
    api_fields = _v3_runtime_contract_api_fields(payload)
    assert api_fields["presentation_mode"] == "short_answer"
    assert api_fields["metadata"]["presentation_mode"] == "short_answer"
    assert api_fields["answer_contract"]
    assert api_fields["component_id"] == "src_4544"
    assert api_fields["textbook_example_id"] == 4544
    assert api_fields["choices"] == []
