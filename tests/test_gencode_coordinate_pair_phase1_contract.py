# -*- coding: utf-8 -*-
"""Phase 1 coordinate_pair answer_contract / checker selection (not skill-specific)."""

from __future__ import annotations

from unittest.mock import patch

from core.checkers.coordinate_pair_checker import check_coordinate_pair_answer
from core.gencode.answer_contract_policy import infer_answer_contract_from_problem_context
from core.gencode.classifier_proposal import detect_answer_shape
from core.gencode.checker_registry import validate_answer_contract_capability
from core.gencode.pipeline_policy import evaluate_pipeline_gates
from core.gencode.problem_type_induction import induce_problem_types_from_examples


def test_ordered_pair_without_choices_uses_coordinate_pair_checker():
    ac = infer_answer_contract_from_problem_context(
        answer_type="ordered_pair",
        target_task="compute_internal_division_point_coordinates",
        task_family="division_point_coordinates_family",
        has_choices=False,
    )
    assert ac["checker"] == "coordinate_pair_checker"
    assert ac["answer_equivalence"] == "ordered_tuple_exact"
    assert ac["answer_shape"] == "coordinate_pair"
    assert ac["answer_type"] == "ordered_pair"
    assert detect_answer_shape(ac) == "coordinate_pair"
    cap = validate_answer_contract_capability(ac)
    assert cap["checker_capability_status"] == "ok"


def test_ordered_pair_with_source_choices_does_not_override_checker():
    ac = infer_answer_contract_from_problem_context(
        answer_type="ordered_pair",
        target_task="compute_internal_division_point_coordinates",
        task_family="division_point_coordinates_family",
        has_choices=True,
    )
    assert ac["checker"] == "coordinate_pair_checker"
    assert ac["answer_equivalence"] == "ordered_tuple_exact"
    assert ac["source_has_choices"] is True


def test_single_choice_with_choices_uses_choice_checker():
    ac = infer_answer_contract_from_problem_context(
        answer_type="single_choice",
        target_task="compute_internal_division_point_coordinates",
        has_choices=True,
    )
    assert ac["checker"] == "choice_label_checker"
    assert ac["answer_equivalence"] == "choice_label"


def test_detect_answer_shape_coordinate_pair_not_unknown():
    ac = {
        "answer_type": "ordered_pair",
        "answer_shape": "coordinate_pair",
        "checker": "coordinate_pair_checker",
        "answer_equivalence": "coordinate_pair_equivalence",
    }
    assert detect_answer_shape(ac) == "coordinate_pair"
    assert detect_answer_shape(ac) != "unknown_answer_shape"


def test_mixed_internal_division_splits_problem_types():
    skill_id = "mock_division_point_contract"
    examples = [
        {
            "id": 4420,
            "example_id": 4420,
            "skill_id": skill_id,
            "problem_text": "A(0,0)、B(6,0)，P 在 AB 上且 AP:PB=2:1，求 P 坐標。",
            "correct_answer": "(4,0)",
        },
        {
            "id": 4512,
            "example_id": 4512,
            "skill_id": skill_id,
            "problem_text": "A(1,2)、B(7,8)，P 在 AB 上且 AP:PB=1:2，求 P 坐標。",
            "correct_answer": "B",
            "choices": ["(3,4)", "(5,6)", "(2,3)", "(4,5)"],
        },
    ]
    meta = {
        "skill_ch_name": "分點坐標",
        "skill_en_name": "DivisionPointCoordinates",
        "expected_task_families": ["division_point_coordinates_family"],
        "expected_subskill_candidates": ["compute_internal_division_point_coordinates"],
    }

    def _feat(ex_id: int, answer_type: str, has_choices: bool, target_task: str) -> dict:
        return {
            "source_example_id": ex_id,
            "answer_type": answer_type,
            "target_task": target_task,
            "task_family": "division_point_coordinates_family",
            "has_choices": has_choices,
            "math_objects": ["two_coordinate_points", "section_ratio"],
            "question_text": f"ex{ex_id}",
            "answer": "B" if has_choices else "(4,0)",
            "semantic_classification": {
                "final_target_task": target_task,
                "final_task_family": "division_point_coordinates_family",
                "classifier_source": "ai",
            },
        }

    with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value=meta):
        with patch(
            "core.gencode.problem_type_induction.extract_example_feature",
            side_effect=lambda ex, *a, **k: _feat(
                int(ex.get("example_id") or ex.get("id")),
                "single_choice" if len(ex.get("choices") or []) >= 2 else "ordered_pair",
                len(ex.get("choices") or []) >= 2,
                "compute_internal_division_point_coordinates",
            ),
        ):
            with patch(
                "core.gencode.problem_type_induction.build_classified_example_feature",
                side_effect=lambda ex, *a, **k: (
                    _feat(
                        int(ex.get("example_id") or ex.get("id")),
                        "single_choice" if len(ex.get("choices") or []) >= 2 else "ordered_pair",
                        len(ex.get("choices") or []) >= 2,
                        "compute_internal_division_point_coordinates",
                    ),
                    {"classifier_source": "ai"},
                ),
            ):
                out = induce_problem_types_from_examples(
                    skill_id, examples, spec_mode="ai_first_induce_from_sources"
                )

    candidates = out.get("candidate_problem_types") or []
    assert len(candidates) >= 2
    checkers = {c.get("checker_key_proposal") for c in candidates}
    assert "tuple_checker" in checkers
    assert "choice_label_checker" in checkers
    coord_cands = [c for c in candidates if c.get("checker_key_proposal") == "tuple_checker"]
    for c in coord_cands:
        assert c.get("answer_shape") == "coordinate_pair"
        assert "unknown_answer_shape" not in str(c.get("answer_shape", ""))
    gates = evaluate_pipeline_gates(
        candidates,
        source_examples_count=len(examples),
        contract_tests_passed=True,
    )
    assert "unknown_answer_shape" not in (gates.get("exception_review_gate", {}).get("reasons") or [])


def test_division_point_phase1_candidate_shapes():
    skill_id = "vh_數學B1_DivisionPointCoordinates_mock"
    examples = [
        {
            "id": i,
            "example_id": i,
            "skill_id": skill_id,
            "problem_text": f"重心題 {i}",
            "correct_answer": "(1,2)",
        }
        for i in (1, 2, 3)
    ]
    meta = {
        "skill_ch_name": "分點坐標",
        "expected_task_families": ["division_point_coordinates_family"],
        "expected_subskill_candidates": [
            "compute_centroid_coordinates",
            "compute_internal_division_point_coordinates",
        ],
    }

    def _centroid_feat(ex_id: int) -> dict:
        return {
            "source_example_id": ex_id,
            "answer_type": "ordered_pair",
            "target_task": "compute_centroid_coordinates",
            "task_family": "division_point_coordinates_family",
            "has_choices": False,
            "math_objects": ["triangle", "centroid"],
            "question_text": "centroid",
            "answer": "(1,2)",
            "semantic_classification": {
                "final_target_task": "compute_centroid_coordinates",
                "final_task_family": "division_point_coordinates_family",
            },
        }

    with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value=meta):
        with patch(
            "core.gencode.problem_type_induction.build_classified_example_feature",
            side_effect=lambda ex, *a, **k: (_centroid_feat(int(ex.get("example_id") or ex.get("id"))), {}),
        ):
            out = induce_problem_types_from_examples(skill_id, examples)

        for c in out.get("candidate_problem_types") or []:
            if "centroid" in str(c.get("problem_type_id", "")):
                assert c.get("checker_key_proposal") == "tuple_checker"
            assert c.get("answer_shape") == "coordinate_pair"


def test_coordinate_pair_checker_point_label_formats():
    correct = "(3,2)"
    for ua in ("3,2", "(3,2)", "P(3,2)", "x=3,y=2"):
        assert check_coordinate_pair_answer(ua, correct), ua
