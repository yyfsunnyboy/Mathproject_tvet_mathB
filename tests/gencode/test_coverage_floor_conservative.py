from __future__ import annotations

from core.gencode.problem_type_induction import _build_quadratic_coverage_floor_suggestions


def test_quadratic_coverage_floor_is_suggestion_only_without_observed_problem_type() -> None:
    suggestions = _build_quadratic_coverage_floor_suggestions(
        skill_id="vh_數學B1_CompletingTheSquare",
        candidate_ids={
            "quadratic_vertex_or_parameter_computation",
            "quadratic_graph_vertex_axis_choice",
        },
        features_for_induction=[
            {
                "source_example_id": 4468,
                "target_task": "quadratic_vertex_or_parameter_computation",
                "question_text": "求 y=x^2+4x+1 的頂點或參數。",
                "math_objects": ["quadratic_vertex_form"],
            },
            {
                "source_example_id": 4501,
                "target_task": "quadratic_graph_vertex_axis_choice",
                "question_text": "判斷 y=x^2+4x+1 的頂點與對稱軸。",
                "math_objects": ["quadratic_vertex_form"],
            },
        ],
    )

    assert len(suggestions) == 1
    row = suggestions[0]
    assert row["problem_type_id"] == "quadratic_standard_to_vertex_properties"
    assert row["reason"] == "quadratic_vertex_form_coverage_floor"
    assert row["suggestion_only"] is True
    assert row["candidate_only"] is True
    assert row["requires_human_action"] is True
    assert row["phase3_include"] is False
    assert row["usable_for_phase3"] is False


def test_quadratic_coverage_floor_noops_when_type_is_observed() -> None:
    suggestions = _build_quadratic_coverage_floor_suggestions(
        skill_id="vh_數學B1_AnyQuadraticSkill",
        candidate_ids={"quadratic_standard_to_vertex_properties"},
        features_for_induction=[
            {
                "source_example_id": 1,
                "target_task": "quadratic_standard_to_vertex_properties",
                "question_text": "y=x^2+4x+1",
                "math_objects": ["quadratic_vertex_form"],
            }
        ],
    )

    assert suggestions == []
