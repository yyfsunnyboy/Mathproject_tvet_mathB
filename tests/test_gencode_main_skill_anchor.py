from __future__ import annotations

from unittest.mock import patch

from core.checkers.coordinate_pair_checker import check_coordinate_pair_answer
from core.gencode.example_feature_extractor import extract_example_feature
from core.gencode.main_skill_anchor import build_main_skill_anchor
from core.gencode.problem_type_induction import induce_problem_types_from_examples
from core.gencode.semantic_alignment import evaluate_source_example_alignment
from core.gencode.task_families import (
    DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
    DIVISION_POINT_COORDINATES_FAMILY,
)


def _ex(ex_id: int, stem: str, answer: str = "(0,-2)", skill_id: str = "vh_數學B1_DivisionPointCoordinates") -> dict:
    return {
        "id": ex_id,
        "example_id": ex_id,
        "skill_id": skill_id,
        "problem_text": stem,
        "correct_answer": answer,
    }


STEM_4423 = "已知 A(-1,1)、B(-3,-3)、C(4,-4)，試求 △ABC 的重心坐標。"
STEM_MIDPOINT = "求 A(1,2)、B(5,6) 的中點坐標。"
STEM_INTERNAL = "P 內分 AB，AP:PB=2:3，求 P 坐標。"
STEM_DISTANCE = "求 A(1,2) 與 B(5,6) 的距離。"


def test_main_skill_anchor_division_point():
    meta = {"skill_ch_name": "分點坐標", "skill_en_name": "Division Point Coordinates"}
    anchor = build_main_skill_anchor("vh_數學B1_DivisionPointCoordinates", meta)
    assert DIVISION_POINT_COORDINATES_FAMILY in anchor["expected_task_families"]
    assert DISTANCE_BETWEEN_TWO_POINTS_FAMILY not in anchor["expected_task_families"]


def test_4423_centroid_feature():
    feat = extract_example_feature(_ex(4423, STEM_4423, "(0,-2)"))
    assert feat["target_task"] == "compute_centroid_coordinates"
    assert feat["task_family"] == DIVISION_POINT_COORDINATES_FAMILY


def test_midpoint_and_internal_division():
    mid = extract_example_feature(_ex(1, STEM_MIDPOINT, "(3,4)"))
    assert mid["target_task"] == "compute_midpoint_coordinates"
    internal = extract_example_feature(_ex(2, STEM_INTERNAL, "(2,3)"))
    assert internal["target_task"] == "compute_internal_division_point_coordinates"


def test_4423_not_source_example_skill_mismatch():
    meta = {"skill_ch_name": "分點坐標"}
    anchor = build_main_skill_anchor("vh_數學B1_DivisionPointCoordinates", meta)
    feat = extract_example_feature(_ex(4423, STEM_4423))
    row = evaluate_source_example_alignment(set(), feat, main_skill_anchor=anchor)
    assert row["included_in_phase1"] is True
    assert row["exclude_reason"] != "source_example_skill_mismatch"


def test_distance_only_when_explicit():
    feat = extract_example_feature(_ex(10, STEM_DISTANCE, "5"))
    assert feat["target_task"] == "compute_distance_between_two_points"


def test_distance_under_division_anchor_not_auto_included():
    meta = {"skill_ch_name": "分點坐標"}
    anchor = build_main_skill_anchor("vh_數學B1_DivisionPointCoordinates", meta)
    feat = extract_example_feature(_ex(11, STEM_DISTANCE, "5"))
    row = evaluate_source_example_alignment(set(), feat, main_skill_anchor=anchor)
    assert row["exclude_reason"] in {"expected_family_mismatch", "task_family_mismatch"}


def test_mixed_family_blocks_distance_candidates():
    skill_id = "vh_數學B1_DivisionPointCoordinates"
    meta = {"skill_ch_name": "分點坐標"}
    examples = [
        _ex(4423, STEM_4423),
        _ex(4420, STEM_DISTANCE, "5"),
        _ex(4421, STEM_DISTANCE, "6"),
        _ex(4427, STEM_DISTANCE, "7"),
        _ex(4438, STEM_DISTANCE, "8"),
        _ex(4512, STEM_DISTANCE, "9"),
        _ex(4513, STEM_DISTANCE, "10"),
    ]
    with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value=meta):
        out = induce_problem_types_from_examples(skill_id, examples)
    cands = out.get("candidate_problem_types") or []
    families = {
        str((c.get("problem_type_spec_draft") or {}).get("task_family", "")).strip()
        for c in cands
        if isinstance(c, dict)
    }
    assert not any(f == DISTANCE_BETWEEN_TWO_POINTS_FAMILY for f in families)
    ex_gate = out.get("exception_review_gate") or {}
    assert ex_gate.get("required") is True


def test_coordinate_pair_checker_formats():
    ca = "(0,-2)"
    for ua in ["0,-2", "(0,-2)", "（0，-2）", "x=0,y=-2"]:
        assert check_coordinate_pair_answer(ua, ca)
    assert not check_coordinate_pair_answer("(1,-2)", ca)
