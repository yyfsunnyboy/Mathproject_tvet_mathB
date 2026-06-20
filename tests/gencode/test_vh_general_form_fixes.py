import pytest
import sqlite3
import json
from fractions import Fraction
from core.gencode.pipeline_orchestrator import (
    _v3_resolve_dry_run_line_type,
    _v3_target_task_for_line_type,
    _v3_template_slot_for_line_type,
)
from core.gencode.domain_matrix_adapter import (
    _build_line_equation_question_text,
    convert_line_equation_matrix_to_question_payload,
)
from core.domain.coordinate_geometry.line_equation_domain import (
    build_line_equation_matrix,
    _build_distractors,
)


def test_dry_run_line_type_ex_resolution_does_not_default():
    # Verify ex_* doesn't silently return point_slope if actual metadata is present
    constraints = {"line_type": "parallel_line_slope"}
    resolved = _v3_resolve_dry_run_line_type(
        source_kind="ex_4592",
        constraints=constraints,
        skill_id="vh_數學B1_GeneralFormOfLinearEquation",
    )
    assert resolved == "parallel_line_slope"

    # Verify fallback triggers warning
    with pytest.warns(UserWarning, match="fallback_line_type_detected"):
        res = _v3_resolve_dry_run_line_type(
            source_kind="ex_unknown_999",
            constraints={},
            skill_id="vh_數學B1_GeneralFormOfLinearEquation",
        )
        assert res == "point_slope"


def test_line_type_mappings_target_task_and_template_slot():
    types = [
        "slope_from_general_or_intercept_form",
        "line_through_point_parallel_to_line",
        "line_through_point_perpendicular_to_line",
        "slope_of_horizontal_or_vertical_line",
        "slope_from_general_form",
        "parallel_line_slope",
        "perpendicular_condition_parameter",
        "compare_line_slopes",
        "perpendicular_line_slope",
        "line_through_intersection_parallel_to_line",
        "perpendicular_bisector_application",
    ]
    for t in types:
        assert _v3_target_task_for_line_type(t) == t
        assert _v3_template_slot_for_line_type(t) == t


def test_parallel_perpendicular_line_stems():
    # Parallel
    givens_parallel = {"point": [2, -1], "equation": "3x - 2y - 1 = 0"}
    facts_parallel = {"task_type": "line_through_point_parallel_to_line"}
    stem_parallel = _build_line_equation_question_text(givens_parallel, facts_parallel)
    assert "(2,\\,-1)" in stem_parallel or "(2, -1)" in stem_parallel
    assert "3x - 2y - 1 = 0" in stem_parallel
    assert "平行" in stem_parallel

    # Perpendicular
    givens_perp = {"point": [2, 5], "equation": "3x + y - 2 = 0"}
    facts_perp = {"task_type": "line_through_point_perpendicular_to_line"}
    stem_perp = _build_line_equation_question_text(givens_perp, facts_perp)
    assert "(2,\\,5)" in stem_perp or "(2, 5)" in stem_perp
    assert "3x + y - 2 = 0" in stem_perp
    assert "垂直" in stem_perp


def test_slope_stems():
    givens = {"equation": "x + 3y - 5 = 0"}
    facts = {"task_type": "slope_from_general_form"}
    stem = _build_line_equation_question_text(givens, facts)
    assert "x + 3y - 5 = 0" in stem
    assert "斜率" in stem


def test_compare_slopes_choices_retention():
    matrix = {
        "givens": {
            "choices": [
                {"label": "A", "text": "y = x/3 - 1"},
                {"label": "B", "text": "y = -3x + 1"},
                {"label": "C", "text": "x/2 + y/3 = 1"},
                {"label": "D", "text": "3x - y + 1 = 0"},
            ]
        },
        "answer": {
            "canonical_form": "D",
            "correct_label": "D",
            "general_form": "3x - y + 1 = 0",
            "coefficients": {"A": 3, "B": -1, "C": 1},
            "slope": "3",
            "intercept": "1",
            "choices": [
                {"label": "A", "text": "y = x/3 - 1"},
                {"label": "B", "text": "y = -3x + 1"},
                {"label": "C", "text": "x/2 + y/3 = 1"},
                {"label": "D", "text": "3x - y + 1 = 0"},
            ]
        },
        "validation_facts": {
            "line_type": "oblique_line",
            "task_type": "compare_line_slopes",
            "coefficients": {"A": 3, "B": -1, "C": 1}
        },
        "visual_spec": {},
        "explanation_steps": [],
        "distractors": []
    }
    payload = convert_line_equation_matrix_to_question_payload(
        matrix, presentation_mode="single_choice", problem_type_id="compare_line_slopes"
    )
    assert payload["answer"] == "D"
    assert payload["correct_answer"] == "D"
    assert "3x - y + 1 = 0" in payload["display_answer"]
    assert len(payload["choices"]) == 4
    assert payload["choices"][3]["label"] == "D"


def test_perpendicular_bisector_rendering():
    givens = {"point_a": [-3, 2], "point_b": [3, 4]}
    facts = {"task_type": "perpendicular_bisector_application"}
    stem = _build_line_equation_question_text(givens, facts)
    assert "A" in stem and "(-3, 2)" in stem
    assert "B" in stem and "(3, 4)" in stem
    assert "垂直平分線" in stem or "中垂線" in stem
    assert "通過" not in stem or "垂直平分線" in stem  # Ensure it is not classified as "through two points"


def test_numeric_distractors_only():
    # parallel_line_slope should only produce numerical distractors, no x/y equations
    distractors = _build_distractors(
        rng=importlib_import_random(),
        answer={"canonical_form": "4/5", "slope": "4/5"},
        actual_type="oblique_line",
        givens={},
        coord_min=-10,
        coord_max=10,
        task_type="parallel_line_slope",
    )
    for d in distractors:
        assert "x" not in d
        assert "y" not in d
        assert "=" not in d


def test_slot_contracts():
    # Missing point
    with pytest.raises(ValueError, match="required_line_task_slot_missing:line_through_point_parallel_to_line:point"):
        _build_line_equation_question_text(
            {"equation": "3x-2y-1=0"}, {"task_type": "line_through_point_parallel_to_line"}
        )

    # Missing reference_line
    with pytest.raises(ValueError, match="required_line_task_slot_missing:line_through_point_parallel_to_line:reference_line"):
        _build_line_equation_question_text(
            {"point": [1, 2]}, {"task_type": "line_through_point_parallel_to_line"}
        )

    # Missing endpoint in perpendicular bisector
    with pytest.raises(ValueError, match="required_line_task_slot_missing:perpendicular_bisector_application:point_b"):
        _build_line_equation_question_text(
            {"point_a": [1, 2]}, {"task_type": "perpendicular_bisector_application"}
        )


def test_unsupported_task_type():
    with pytest.raises(ValueError, match="unsupported_line_equation_task_type:non_existent_task"):
        _build_line_equation_question_text(
            {}, {"task_type": "non_existent_task"}
        )


def test_textbook_examples_generation_loop():
    import sqlite3
    db_path = "instance/kumon_math.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    target_ids = [4565, 4566, 4567, 4572, 4573, 4574, 4581, 4582, 4585, 4592, 4593, 4594, 4595, 4596, 4597, 4598, 4599]
    
    for ex_id in target_ids:
        row = conn.execute("SELECT * FROM textbook_examples WHERE id = ?", (ex_id,)).fetchone()
        assert row is not None
        
        # Test math matrix solver for all types
        tracker_row = conn.execute("SELECT * FROM gencode_component_tracker WHERE textbook_example_id = ?", (ex_id,)).fetchone()
        if tracker_row:
            spec = json.loads(tracker_row["induced_spec_payload"])
            line_type = spec.get("line_type")
            assert line_type is not None
            
            # Build domain matrix
            matrix = build_line_equation_matrix(
                seed=42,
                line_type=line_type,
                curriculum_profile="vocational_high_b",
                difficulty_profile="easy",
            )
            assert "coefficients" in matrix["answer"]
            
            # Convert to payload
            payload = convert_line_equation_matrix_to_question_payload(
                matrix,
                presentation_mode=spec.get("presentation_mode", "short_answer"),
                problem_type_id=spec.get("problem_type_id", line_type),
            )
            
            q_text = payload["question_text"]
            assert q_text != "請寫出符合題意的直線方程式。"
            assert len(q_text) > 0
            
    conn.close()


def importlib_import_random():
    import random
    return random.Random(42)
